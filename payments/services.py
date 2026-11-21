import base64
import os
from datetime import datetime

import requests


def normalize_phone(phone):
    digits = "".join(ch for ch in phone if ch.isdigit())
    if digits.startswith("0"):
        digits = "254" + digits[1:]
    elif digits.startswith("7") or digits.startswith("1"):
        digits = "254" + digits
    if not (digits.startswith("254") and len(digits) == 12):
        raise ValueError("Enter a valid Kenyan M-Pesa phone number.")
    return digits


class DarajaError(Exception):
    pass


class DarajaService:
    def __init__(self):
        self.environment = os.getenv("DARJA_ENVIRONMENT", "sandbox")
        self.consumer_key = os.getenv("DARJA_CONSUMER_KEY", "")
        self.consumer_secret = os.getenv("DARJA_CONSUMER_SECRET", "")
        self.shortcode = os.getenv("DARJA_SHORTCODE", "")
        self.passkey = os.getenv("DARJA_PASSKEY", "")
        self.callback_url = os.getenv("DARJA_CALLBACK_URL", "")
        self.base_url = "https://sandbox.safaricom.co.ke" if self.environment == "sandbox" else "https://api.safaricom.co.ke"

    @property
    def configured(self):
        return all((self.consumer_key, self.consumer_secret, self.shortcode, self.passkey, self.callback_url))

    def access_token(self):
        response = requests.get(
            f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials",
            auth=(self.consumer_key, self.consumer_secret),
            timeout=20,
        )
        response.raise_for_status()
        token = response.json().get("access_token")
        if not token:
            raise DarajaError("Daraja did not return an access token.")
        return token

    def stk_push(self, phone, amount, account_reference, description):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(f"{self.shortcode}{self.passkey}{timestamp}".encode()).decode()
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone,
            "PartyB": self.shortcode,
            "PhoneNumber": phone,
            "CallBackURL": self.callback_url,
            "AccountReference": account_reference[:12],
            "TransactionDesc": description[:13],
        }
        response = requests.post(
            f"{self.base_url}/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers={"Authorization": f"Bearer {self.access_token()}"},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        if data.get("ResponseCode") != "0":
            raise DarajaError(data.get("errorMessage") or data.get("ResponseDescription") or "STK Push could not be started.")
        return data

    def query_stk_status(self, checkout_request_id):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(f"{self.shortcode}{self.passkey}{timestamp}".encode()).decode()
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id,
        }
        response = requests.post(
            f"{self.base_url}/mpesa/stkpushquery/v1/query",
            json=payload,
            headers={"Authorization": f"Bearer {self.access_token()}"},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

