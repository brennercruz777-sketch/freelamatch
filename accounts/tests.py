from django.test import TestCase
from django.urls import reverse

from .models import ClientProfile, FreelancerProfile, User


class SignUpTests(TestCase):
    def test_signup_creates_client_profile(self):
        response = self.client.post(reverse("signup"), {
            "username": "cliente1",
            "email": "cliente1@test.com",
            "role": User.Role.CLIENT,
            "password1": "SenhaForte123!",
            "password2": "SenhaForte123!",
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="cliente1")
        self.assertTrue(ClientProfile.objects.filter(user=user).exists())
        self.assertFalse(FreelancerProfile.objects.filter(user=user).exists())

    def test_signup_creates_freelancer_profile(self):
        response = self.client.post(reverse("signup"), {
            "username": "freela1",
            "email": "freela1@test.com",
            "role": User.Role.FREELANCER,
            "password1": "SenhaForte123!",
            "password2": "SenhaForte123!",
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="freela1")
        self.assertTrue(FreelancerProfile.objects.filter(user=user).exists())

    def test_signup_blocks_duplicate_email(self):
        User.objects.create_user(
            username="existente",
            email="dup@test.com",
            password="SenhaForte123!",
            role=User.Role.CLIENT,
        )
        response = self.client.post(reverse("signup"), {
            "username": "novo",
            "email": "DUP@test.com",
            "role": User.Role.CLIENT,
            "password1": "SenhaForte123!",
            "password2": "SenhaForte123!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Já existe uma conta com este e-mail.")


class DashboardAccessTests(TestCase):
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)