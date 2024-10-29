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

class FileUploadView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        reference_date = request.data.get('reference_date')
        
        if not file or not reference_date:
            return Response({"error": "Arquivo e data de referência são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)
      
        if UploadHistory.objects.filter(file_name=file.name).exists():
            return Response({"error": "Este arquivo já foi carregado anteriormente."}, status=status.HTTP_400_BAD_REQUEST)

        if not self.is_valid_file_type(file.name):
            return Response({"error": "Formato de arquivo inválido. Somente arquivos CSV, XLSX e XLS são permitidos."}, status=status.HTTP_400_BAD_REQUEST)

        try:
           parsed_date = parse_date(reference_date)
           if not parsed_date or not self.is_valid_date(reference_date):
               raise ValueError 
        except (ValueError, TypeError):
            return Response({"error": "Data de referência inválida. O formato deve ser YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        
        upload_history = UploadHistory.objects.create(
            file_name=file.name,
            reference_date=parsed_date
        )
        
        try:
            decoded_file = file.read().decode('utf-8')
            df = pd.read_csv(io.StringIO(decoded_file), delimiter=';', skiprows=1)

            if df['RptDt'].isnull().any() or df['RptDt'].eq('').any():
                return Response({"error": "A coluna 'RptDt' não pode ser vazia."}, status=status.HTTP_400_BAD_REQUEST)

            df['Parsed_RptDt'] = pd.to_datetime(df['RptDt'], errors='coerce')

            if df['Parsed_RptDt'].isnull().any():
                invalid_dates = df[df['Parsed_RptDt'].isnull()]['RptDt'].unique()
                return Response({"error": f"Datas de referência inválidas: {', '.join(invalid_dates)}. O formato deve ser YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

            data_instances = []
            for _, row in df.iterrows():
                data_instance = Data(
                    RptDt=row['Parsed_RptDt'],
                    TckrSymb=row['TckrSymb'],
                    MktNm=row['MktNm'],
                    SctyCtgyNm=row['SctyCtgyNm'],
                    ISIN=row['ISIN'],
                    CrpnNm=row['CrpnNm'],
                )
                data_instances.append(data_instance)

            Data.objects.bulk_create(data_instances)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(UploadHistorySerializer(upload_history).data, status=status.HTTP_201_CREATED)

    def is_valid_date(self, date_str):
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        return bool(date_pattern.match(date_str))

    def is_valid_file_type(self, filename):
        valid_extensions = ['.csv', '.xlsx', 'xls']
        return any(filename.lower().endswith(ext) for ext in valid_extensions)

class UploadHistoryPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'  
    max_page_size = 100 

class UploadHistoryView(APIView):
    pagination_class = UploadHistoryPagination  

    def get(self, request):
        file_name = request.query_params.get('file_name')
        reference_date = request.query_params.get('reference_date')
        
        uploads = UploadHistory.objects.all()

        if file_name:
            uploads = uploads.filter(file_name__icontains=file_name)

        try:
            if reference_date:
                uploads = uploads.filter(reference_date=parse_date(reference_date))
        except:
            return Response({"error": "Data de referência inválida. O formato deve ser YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        if not uploads.exists():
            return Response({"error": "Nenhum upload encontrado com os critérios fornecidos."}, status=status.HTTP_404_NOT_FOUND)

        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', self.pagination_class.page_size)

        if (isinstance(page, str) and page.lstrip('-').isdigit()) and int(page) < 1:
            return Response({"error": "O número da página deve ser um inteiro positivo."}, status=status.HTTP_400_BAD_REQUEST)

        if (isinstance(page_size, str) and page_size.lstrip('-').isdigit()) and int(page_size) < 1:
            return Response({"error": "O tamanho da página deve ser um inteiro positivo."}, status=status.HTTP_400_BAD_REQUEST)

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(uploads, request)
        serializer = UploadHistorySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class CustomAuthToken(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            return super().post(request, *args, **kwargs)
        else:
            return Response({"error": "Credenciais inválidas."}, status=status.HTTP_400_BAD_REQUEST)

class SearchView(APIView):
    def get(self, request):
        tckr_symb = request.query_params.get('TckrSymb')
        rpt_dt = request.query_params.get('RptDt')
        mkt_nm = request.query_params.get('MktNm')
        scty_ctgy_nm = request.query_params.get('SctyCtgyNm')
        isin = request.query_params.get('ISIN')
        crpn_nm = request.query_params.get('CrpnNm')

        queryset = Data.objects.all()

        if tckr_symb:
            if not isinstance(tckr_symb, str) or not tckr_symb.strip():
                return Response({"error": "O campo 'TckrSymb' deve ser uma string não vazia."}, status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(TckrSymb=tckr_symb)

        if rpt_dt:
            try:
                parsed_date = datetime.strptime(rpt_dt, '%Y-%m-%d').date()  
                queryset = queryset.filter(RptDt=parsed_date)  
            except ValueError:
                return Response({"error": "O campo 'RptDt' deve estar no formato YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        if mkt_nm:
            if not isinstance(mkt_nm, str) or not mkt_nm.strip():
                return Response({"error": "O campo 'MktNm' deve ser uma string não vazia."}, status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(MktNm=mkt_nm)

        if scty_ctgy_nm:
            if not isinstance(scty_ctgy_nm, str) or not scty_ctgy_nm.strip():
                return Response({"error": "O campo 'SctyCtgyNm' deve ser uma string não vazia."}, status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(SctyCtgyNm=scty_ctgy_nm)

        if isin:
            if not isinstance(isin, str) or not isin.strip():
                return Response({"error": "O campo 'ISIN' deve ser uma string não vazia."}, status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(ISIN=isin)

        if crpn_nm:
            if not isinstance(crpn_nm, str) or not crpn_nm.strip():
                return Response({"error": "O campo 'CrpnNm' deve ser uma string não vazia."}, status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(CrpnNm=crpn_nm)

        paginator = UploadHistoryPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = SecurityDataSerializer(paginated_queryset, many=True)

        return paginator.get_paginated_response(serializer.data)