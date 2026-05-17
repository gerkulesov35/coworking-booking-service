from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Profile


class ProfileSignalTests(TestCase):
    def test_profile_auto_created(self):
        user = User.objects.create_user(username='alice', password='pass12345')
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertEqual(user.profile.role, Profile.ROLE_USER)

    def test_role_flags(self):
        user = User.objects.create_user(username='bob', password='pass12345')
        user.profile.role = Profile.ROLE_MANAGER
        user.profile.save()
        self.assertTrue(user.profile.is_manager)
        self.assertFalse(user.profile.is_admin)


class AuthFlowTests(TestCase):
    def test_register_creates_user(self):
        resp = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'StrongPass!23',
            'password2': 'StrongPass!23',
        })
        self.assertIn(resp.status_code, (200, 302))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_profile_requires_login(self):
        resp = self.client.get(reverse('profile'))
        self.assertEqual(resp.status_code, 302)

    def test_profile_when_logged_in(self):
        User.objects.create_user(username='carol', password='pass12345')
        self.client.login(username='carol', password='pass12345')
        resp = self.client.get(reverse('profile'))
        self.assertEqual(resp.status_code, 200)
