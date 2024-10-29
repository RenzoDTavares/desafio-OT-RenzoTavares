from rest_framework import serializers
from .models import UploadHistory, Data

class UploadHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadHistory
        fields = ['file_name', 'uploaded_at', 'reference_date']

class SecurityDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Data
        fields = [
            'RptDt', 
            'TckrSymb', 
            'MktNm', 
            'SctyCtgyNm', 
            'ISIN', 
            'CrpnNm'
        ]