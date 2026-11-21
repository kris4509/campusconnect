from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        min_length=8,
        help_text="Use at least 8 characters, including a mix of letters and numbers.",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password_confirmation = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=(("student", "Student"), ("organizer", "Organizer")))

    class Meta:
        model = User
        fields = ("full_name", "email", "student_number", "phone_number", "role")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this university email already exists.")
        return email

    def clean_student_number(self):
        number = self.cleaned_data.get("student_number")
        if number and User.objects.filter(student_number__iexact=number).exists():
            raise forms.ValidationError("This registration/student number is already in use.")
        return number

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        confirmation = cleaned.get("password_confirmation")
        if password and confirmation and password != confirmation:
            self.add_error("password_confirmation", "Passwords do not match.")
        if password:
            candidate = User(
                full_name=cleaned.get("full_name", ""),
                email=cleaned.get("email", ""),
            )
            try:
                validate_password(password, candidate)
            except ValidationError as exc:
                self.add_error("password", exc)
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"].lower()
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("full_name", "email", "student_number", "phone_number")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("An account with this university email already exists.")
        return email

    def clean_student_number(self):
        number = self.cleaned_data.get("student_number")
        if number and User.objects.filter(student_number__iexact=number).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This registration/student number is already in use.")
        return number
