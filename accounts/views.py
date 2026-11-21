from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ProfileForm, RegistrationForm


def dashboard_for(user):
    if user.role == "organizer":
        return "dashboard:organizer"
    if user.role == "admin" or user.is_superuser:
        return "dashboard:admin"
    return "dashboard:student"


def register(request):
    if request.user.is_authenticated:
        return redirect(dashboard_for(request.user))
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your account has been created.")
        return redirect(dashboard_for(user))
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect(dashboard_for(request.user))
    if request.method == "POST":
        post_data = request.POST.copy()
        if "username" in post_data:
            post_data["username"] = post_data["username"].strip().lower()
        form = AuthenticationForm(request, data=post_data)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, f"Welcome back, {form.get_user().full_name}!")
            return redirect(request.POST.get("next") or dashboard_for(request.user))
    else:
        form = AuthenticationForm(request)
    next_url = request.GET.get("next") or request.POST.get("next")
    return render(request, "accounts/login.html", {"form": form, "next": next_url})


@login_required
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.username = user.email.lower()
        user.save()
        messages.success(request, "Your profile has been updated.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"form": form})
