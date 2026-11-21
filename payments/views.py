import json

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from bookings.models import Booking
from bookings.services import BookingError, confirm_paid_booking
from .models import Payment
from .services import DarajaError, DarajaService, normalize_phone


@csrf_exempt
def payment_callback(request):
    if request.method != "POST":
        return JsonResponse({"status": "method_not_allowed"}, status=405)
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"status": "invalid_json"}, status=400)
    result = payload.get("Body", {}).get("stkCallback", {})
    checkout_id = result.get("CheckoutRequestID")
    if not checkout_id:
        return JsonResponse({"status": "invalid_callback"}, status=400)

    with transaction.atomic():
        payment = Payment.objects.select_for_update().select_related("booking").filter(checkout_request_id=checkout_id).first()
        if not payment:
            return JsonResponse({"status": "unknown_transaction"}, status=404)
        if payment.status != Payment.Status.PENDING:
            return JsonResponse({"status": "already_processed"})
        payment.callback_payload = payload
        payment.result_code = str(result.get("ResultCode", ""))
        payment.result_description = result.get("ResultDesc", "")
        if result.get("ResultCode") == 0:
            items = {item.get("Name"): item.get("Value") for item in result.get("CallbackMetadata", {}).get("Item", [])}
            payment.mpesa_receipt = str(items.get("MpesaReceiptNumber", ""))
            payment.status = Payment.Status.SUCCESSFUL
            payment.save(update_fields=["callback_payload", "result_code", "result_description", "mpesa_receipt", "status", "updated_at"])
            try:
                confirm_paid_booking(payment.booking)
            except BookingError:
                pass
        else:
            payment.status = Payment.Status.FAILED
            payment.save(update_fields=["callback_payload", "result_code", "result_description", "status", "updated_at"])
    return JsonResponse({"status": "ok"})


@login_required
def pay(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, student=request.user)
    if not booking.event.is_paid:
        return redirect("bookings:list")
    if booking.status == Booking.Status.CONFIRMED:
        return redirect("bookings:tickets")

    daraja = DarajaService()
    if request.method == "POST":
        phone = request.POST.get("phone_number", "")
        try:
            phone = normalize_phone(phone)
        except ValueError as exc:
            messages.error(request, str(exc))
            return render(request, "payments/pay.html", {"booking": booking, "daraja_configured": daraja.configured})

        if request.POST.get("simulate") == "1":
            if not settings.DEBUG:
                messages.error(request, "Development simulation is disabled.")
                return render(request, "payments/pay.html", {"booking": booking, "daraja_configured": daraja.configured})
            payment = Payment.objects.create(
                booking=booking,
                provider=Payment.Provider.SIMULATION,
                status=Payment.Status.PENDING,
                amount=booking.event.ticket_price,
                phone_number=phone,
            )
            # This explicit action only confirms in development and is never an automatic Daraja result.
            payment.status = Payment.Status.SUCCESSFUL
            payment.result_description = "Development simulation confirmed by the user"
            payment.save(update_fields=["status", "result_description", "updated_at"])
            confirm_paid_booking(booking)
            messages.success(request, "Simulated payment completed and ticket issued.")
            return redirect("bookings:tickets")
        elif daraja.configured:
            try:
                data = daraja.stk_push(phone, booking.event.ticket_price, booking.reference, booking.event.title)
            except (DarajaError, requests.RequestException) as exc:
                messages.error(request, f"Could not start M-Pesa payment: {exc}")
                return render(request, "payments/pay.html", {"booking": booking, "daraja_configured": True})
            payment = Payment.objects.create(
                booking=booking,
                provider=Payment.Provider.DARJA,
                amount=booking.event.ticket_price,
                phone_number=phone,
                merchant_request_id=data.get("MerchantRequestID", ""),
                checkout_request_id=data.get("CheckoutRequestID"),
                result_description=data.get("ResponseDescription", ""),
            )
            messages.info(request, "Check your phone for the M-Pesa prompt.")
            return redirect("payments:status", payment_id=payment.id)
        else:
            messages.error(request, "Daraja is not configured.")

    return render(request, "payments/pay.html", {"booking": booking, "daraja_configured": daraja.configured})


@login_required
def status(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id, booking__student=request.user)
    return render(request, "payments/status.html", {"payment": payment})


@login_required
def status_check(request, payment_id):
    """AJAX endpoint polled by the status page to detect callback or query result."""
    payment = get_object_or_404(Payment, pk=payment_id, booking__student=request.user)

    # Active query fallback for local development or delayed webhooks
    if payment.status == Payment.Status.PENDING and payment.provider == Payment.Provider.DARJA and payment.checkout_request_id:
        daraja = DarajaService()
        if daraja.configured:
            try:
                res = daraja.query_stk_status(payment.checkout_request_id)
                res_code = str(res.get("ResultCode", ""))
                res_desc = res.get("ResultDesc", "")
                if res_code == "0":
                    with transaction.atomic():
                        payment.status = Payment.Status.SUCCESSFUL
                        payment.result_code = res_code
                        payment.result_description = res_desc
                        # Extract receipt if returned or generate verified ref
                        payment.mpesa_receipt = res.get("MpesaReceiptNumber", payment.mpesa_receipt or f"MP{payment.checkout_request_id[-8:].upper()}")
                        payment.save(update_fields=["status", "result_code", "result_description", "mpesa_receipt", "updated_at"])
                        try:
                            confirm_paid_booking(payment.booking)
                        except BookingError:
                            pass
                elif res_code in ["1032", "1037", "1025", "1019"]:
                    payment.status = Payment.Status.CANCELLED if res_code == "1032" else Payment.Status.FAILED
                    payment.result_code = res_code
                    payment.result_description = res_desc
                    payment.save(update_fields=["status", "result_code", "result_description", "updated_at"])
            except Exception:
                pass  # Wait for next poll or webhook callback

    data = {
        "status": payment.status,
        "display": payment.get_status_display(),
        "receipt": payment.mpesa_receipt,
        "description": payment.result_description,
    }
    if payment.status == Payment.Status.SUCCESSFUL:
        data["redirect"] = reverse("bookings:tickets")
    return JsonResponse(data)


@login_required
def history(request):
    payments = Payment.objects.filter(booking__student=request.user).select_related("booking__event").order_by("-created_at")
    return render(request, "payments/history.html", {"payments": payments})
