from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class RegistrationTests(TestCase):
    def test_registration_creates_student(self):
        response = self.client.post(reverse("accounts:register"), {
            "full_name": "Test Student",
            "email": "student@example.edu",
            "student_number": "S001",
            "phone_number": "+254712345678",
            "role": "student",
            "password": "StrongPass!923",
            "password_confirmation": "StrongPass!923",
        })
        self.assertEqual(response.status_code, 302)
        user = get_user_model().objects.get(email="student@example.edu")
        self.assertEqual(user.role, "student")
        self.assertTrue(user.check_password("StrongPass!923"))

    def test_profile_requires_login_and_updates_account(self):
        user = get_user_model().objects.create_user(
            username="student", email="student@example.edu", password="StrongPass!923",
            full_name="Student", phone_number="+254712345678",
        )
        self.client.force_login(user)
        response = self.client.post(reverse("accounts:profile"), {
            "full_name": "Updated Student",
            "email": "student@example.edu",
            "student_number": "S001",
            "phone_number": "+254712345678",
        })
        self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        self.assertEqual(user.full_name, "Updated Student")
        self.assertEqual(user.student_number, "S001")

    def test_registration_rejects_password_mismatch(self):
        response = self.client.post(reverse("accounts:register"), {
            "full_name": "Test Student",
            "email": "mismatch@example.edu",
            "student_number": "S002",
            "phone_number": "+254712345678",
            "role": "student",
            "password": "StrongPass!923",
            "password_confirmation": "DifferentPass!923",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Passwords do not match")
        self.assertFalse(get_user_model().objects.filter(email="mismatch@example.edu").exists())
