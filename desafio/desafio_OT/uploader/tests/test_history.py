from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from uploader.models import UploadHistory
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

class HistoryTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.history_url = reverse('upload-history')  
        
        self.user = User.objects.create_user(username='renzo', password='renzo')
        
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
    
    def tearDown(self):
        UploadHistory.objects.all().delete()
    
    # CT007: Filtro por nome do arquivo no histórico
    def test_filter_history_by_file_name(self):
        UploadHistory.objects.create(file_name="testfile.csv", reference_date="2024-01-01")
        response = self.client.get(self.history_url, {'file_name': 'testfile.csv'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    # CT008: Busca de histórico com diretório vazio
    def test_no_history_records(self):
        response = self.client.get(self.history_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Nenhum upload encontrado com os critérios fornecidos.", response.data['error'])
