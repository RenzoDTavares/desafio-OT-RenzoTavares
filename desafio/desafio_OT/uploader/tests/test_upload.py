from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from uploader.models import UploadHistory
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
import os

class UploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.upload_url = reverse('file-upload')
        
        self.user = User.objects.create_user(username='renzo', password='renzo')
        
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
    
    def tearDown(self):
        UploadHistory.objects.all().delete()
    
    # CT001: Upload de um arquivo sem erros
    def test_upload_file_success(self):
        test_file_path = os.path.join(os.path.dirname(__file__), 'files/fileSuccess.csv')
        with open(test_file_path, 'rb') as file:
            response = self.client.post(self.upload_url, {'file': file, 'reference_date': '2024-10-29'}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UploadHistory.objects.count(), 1)

        uploaded_history = UploadHistory.objects.first()
        self.assertEqual(uploaded_history.row_failed, 0, "O número de linhas falhadas deve ser 0.")

    # CT002: Upload de um arquivo com erros em 6 linhas
    def test_upload_file_with_corrupted_file(self):
        test_file_path = os.path.join(os.path.dirname(__file__), 'files/fileWithError.csv')
        with open(test_file_path, 'rb') as file:
            response = self.client.post(self.upload_url, {'file': file, 'reference_date': '2024-10-29'}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UploadHistory.objects.count(), 1)

        uploaded_history = UploadHistory.objects.first()
        self.assertEqual(uploaded_history.row_failed, 6, "O número de linhas falhadas deve ser maior que 6.")

    # CT003: Upload de um arquivo já existente na base de dados
    def test_prevent_duplicate_upload(self):
        test_file_path = os.path.join(os.path.dirname(__file__), 'files/fileSuccess.csv')

        with open(test_file_path, 'rb') as file:
            for _ in range(2):
                response = self.client.post(self.upload_url, {'file': file, 'reference_date': '2024-10-29'}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(UploadHistory.objects.count(), 1)

    # CT004: Upload de um arquivo sem os campos obrigatórios (file e reference_date)
    def test_upload_file_without_file(self):
        response = self.client.post(self.upload_url, {}) 
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Arquivo e data de referência são obrigatórios.", response.data["error"])

    # CT005: Upload de um arquivo invalido
    def test_upload_file_with_invalid_file_type(self):
        test_file_path = os.path.join(os.path.dirname(__file__), 'files/fileInvalid.txt')  
        with open(test_file_path, 'rb') as file:
            response = self.client.post(self.upload_url, {'file': file, 'reference_date': '2024-10-29'}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Formato de arquivo inválido.", response.data["error"])
        
    # CT006: Upload de um arquivo sem as credenciais de acesso    
    def test_upload_file_without_authentication(self):
        self.client.credentials() 
        test_file_path = os.path.join(os.path.dirname(__file__), 'files/fileSuccess.csv')
        with open(test_file_path, 'rb') as file:
            response = self.client.post(self.upload_url, {'file': file, 'reference_date': '2024-10-29'}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) 
