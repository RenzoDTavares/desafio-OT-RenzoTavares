from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status

class TokenAuthTests(APITestCase):

    def setUp(self):
        self.username = 'renzo'
        self.password = 'renzo'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.token_url = reverse('token_obtain_pair')  
        
    # CT012: Login com as credenciais corretas    
    def test_login_success(self):
        data = {
            'username': self.username,
            'password': self.password
        }
        response = self.client.post(self.token_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    # CT013: Login com as credenciais erradas
    def test_login_failure(self):
        data = {
            'username': self.username,
            'password': 'senha_errada'
        }
        response = self.client.post(self.token_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)
