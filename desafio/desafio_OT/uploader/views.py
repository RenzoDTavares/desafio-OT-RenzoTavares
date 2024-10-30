from django.utils.dateparse import parse_date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import UploadHistory, Data
from .serializers import UploadHistorySerializer, SecurityDataSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Q
from datetime import datetime
import pandas as pd
import re
import io

class ApiOverviewView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        api_endpoints = {
            "upload/": "Faz o upload de um arquivo e armazena as informações no banco de dados.",
            "history/": "Retorna o histórico de uploads.",
            "search/": "Realiza uma busca de registros.",
            "token/": "Obtém um token de autenticação com base em nome de usuário e senha.",
        }
        return Response(api_endpoints)
    
class FileUploadView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        reference_date = request.data.get('reference_date')
        updated_by = request.user.username 

        # Validação de campo arquivo e data de referência
        error_response = self.validate_file_and_date(file, reference_date)
        if error_response:
            return error_response
        
        parsed_date = parse_date(reference_date)
        file_size = file.size
        
        upload_history = UploadHistory.objects.create(
            file_name=file.name,
            reference_date=parsed_date,
            updated_by=updated_by,
            file_size=file_size,
        )

        # Processamento do arquivo
        row_failed, row_processed, failed_rows = self.process_file(file, upload_history)

        # Persistência dos dados e histórico
        upload_history.row_processed = row_processed
        upload_history.row_failed = row_failed
        upload_history.failed_rows = ', '.join(map(str, failed_rows))  
        upload_history.save()

        return Response(UploadHistorySerializer(upload_history).data, status=status.HTTP_201_CREATED)

    def validate_file_and_date(self, file, reference_date):
        if not file or not reference_date:
            return Response({"error": "Arquivo e data de referência são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)
        if UploadHistory.objects.filter(file_name=file.name).exists():
            return Response({"error": "Este arquivo já foi carregado anteriormente."}, status=status.HTTP_400_BAD_REQUEST)
        if not self.is_valid_file_type(file.name):
            return Response({"error": "Formato de arquivo inválido. Somente arquivos CSV, XLSX e XLS são permitidos."}, status=status.HTTP_400_BAD_REQUEST)
        if not parse_date(reference_date) or not self.is_valid_date(reference_date):
            return Response({"error": "Data de referência inválida. O formato deve ser YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        return None
    
    def process_file(self, file, upload_history):
        row_failed, row_processed, failed_rows = 0, 0, []
        try:
            decoded_file = file.read().decode('utf-8')
            df = pd.read_csv(io.StringIO(decoded_file), delimiter=';', skiprows=1)

            data_instances = []
            for index, row in df.iterrows():
                if not self.validate_row(row):
                    row_failed += 1
                    failed_rows.append(index)
                    continue
                
                data_instance = Data(
                    RptDt=pd.to_datetime(row['RptDt'], format='%d/%m/%Y', errors='coerce'),
                    TckrSymb=row['TckrSymb'],
                    MktNm=row['MktNm'],
                    SctyCtgyNm=row['SctyCtgyNm'],
                    ISIN=row['ISIN'],
                    CrpnNm=row['CrpnNm'],
                )
                data_instances.append(data_instance)
                row_processed += 1
            
            Data.objects.bulk_create(data_instances)
        except Exception as e:
            raise e
        return row_failed, row_processed, failed_rows
    
    @staticmethod
    def validate_row(row):
        required_fields = ['RptDt', 'TckrSymb', 'MktNm', 'SctyCtgyNm', 'ISIN', 'CrpnNm']
        return all(not pd.isna(row[field]) for field in required_fields)

    @staticmethod
    def is_valid_date(date_str):
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        return bool(date_pattern.match(date_str))

    @staticmethod
    def is_valid_file_type(filename):
        valid_extensions = ['.csv', '.xlsx', '.xls']
        return any(filename.lower().endswith(ext) for ext in valid_extensions)


class UploadHistoryPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'  
    max_page_size = 100 


class UploadHistoryView(APIView):
    pagination_class = UploadHistoryPagination  

    def get(self, request):
        filters = {
            'file_name': 'file_name__icontains',
            'reference_date': 'reference_date',
            'uploaded_at': 'uploaded_at__date',
            'updated_by': 'updated_by__icontains',
            'file_size': 'file_size',
            'row_count': 'row_count'
        }

        uploads = UploadHistory.objects.all().order_by('uploaded_at')
        for param, db_filter in filters.items():
            value = request.query_params.get(param)
            if value:
                if param in ['reference_date', 'uploaded_at']:
                    try:
                        uploads = uploads.filter(**{db_filter: parse_date(value)})
                    except ValueError:
                        return Response({"error": f"Data inválida para o campo {param}."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    uploads = uploads.filter(**{db_filter: value})
        
        if not uploads.exists():
            return Response({"error": "Nenhum upload encontrado com os critérios fornecidos."}, status=status.HTTP_404_NOT_FOUND)
        
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(uploads, request)
        serializer = UploadHistorySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class CustomAuthToken(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username, password = request.data.get("username"), request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            return super().post(request, *args, **kwargs)
        return Response({"error": "Credenciais inválidas."}, status=status.HTTP_400_BAD_REQUEST)

class SearchView(APIView):
    def get(self, request):
        query_params = {
            'TckrSymb': 'TckrSymb',
            'RptDt': 'RptDt',
            'MktNm': 'MktNm',
            'SctyCtgyNm': 'SctyCtgyNm',
            'ISIN': 'ISIN',
            'CrpnNm': 'CrpnNm'
        }

        queryset = Data.objects.all().order_by('RptDt')
        for param, field in query_params.items():
            value = request.query_params.get(param)
            if value:
                if param == 'RptDt':
                    try:
                        value = datetime.strptime(value, '%Y-%m-%d').date()
                    except ValueError:
                        return Response({"error": f"O campo '{param}' deve estar no formato YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
                queryset = queryset.filter(**{field: value})
        
        paginator = UploadHistoryPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = SecurityDataSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)