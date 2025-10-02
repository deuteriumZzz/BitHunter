import pytest
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from .models import UserProfile

class UserProfileTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='pass')
        self.client.force_authenticate(user=self.user)

    def test_profile_creation(self):
        data = {'telegram_chat_id': '123'}
        response = self.client.post('/api/accounts/profiles/', data)
        self.assertEqual(response.status_code, 201)
