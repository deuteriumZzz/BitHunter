from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from .models import UserProfile


class UserProfileTest(APITestCase):
    """
    Тестовый класс для проверки функциональности модели UserProfile.
    
    Наследуется от APITestCase для тестирования API эндпоинтов.
    """
    
    def setUp(self):
        """
        Настройка тестового окружения.
        
        Создает тестового пользователя и аутентифицирует клиента API.
        """
        self.user = User.objects.create_user(username='test', password='pass')
        self.client.force_authenticate(user=self.user)
    
    def test_profile_creation(self):
        """
        Тест создания профиля пользователя.
        
        Отправляет POST-запрос на эндпоинт создания профиля и проверяет,
        что статус ответа равен 201 (Created).
        """
        data = {'telegram_chat_id': '123'}
        response = self.client.post('/api/accounts/profiles/', data)
        self.assertEqual(response.status_code, 201)
