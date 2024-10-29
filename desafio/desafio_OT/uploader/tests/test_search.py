from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from uploader.models import Data
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

class SearchTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.search_url = reverse('search')
        
        self.user = User.objects.create_user(username='renzo', password='renzo')
        
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
    def tearDown(self):
        Data.objects.all().delete()
    
    # CT009: Busca de um item com parametros
    def test_search_content_with_parameters(self):
        Data.objects.create(
            RptDt="2024-08-22",
            TckrSymb="AMZO34",
            MktNm="EQUITY-CASH",
            SctyCtgyNm="BDR",
            ISIN="BRAMZOBDR002",
            CrpnNm="AMAZON.COM, INC"
        )
        response = self.client.get(self.search_url, {'TckrSymb': 'AMZO34', 'RptDt': '2024-08-22'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    # CT010: Busca de um item com parametro de data errado
    def test_search_with_wrong_parameter(self):
        response = self.client.get(self.search_url, {'RptDt': '20242-08-22'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("O campo 'RptDt' deve estar no formato YYYY-MM-DD.", response.data['error'])

    # CT011: Validação de paginação na busca de vários itens
    def test_paginated_search_no_params(self):
        for i in range(15):  
            Data.objects.create(
                RptDt="2024-08-22",
                TckrSymb=f"SYM{i}",
                MktNm="EQUITY-CASH",
                SctyCtgyNm="BDR",
                ISIN=f"ISIN{i}",
                CrpnNm=f"Company {i}"
            )
        
        response = self.client.get(self.search_url, {'page': 1, 'page_size': 10})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
