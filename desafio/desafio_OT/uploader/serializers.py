from rest_framework import serializers
from .models import UploadHistory, Data

class UploadHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadHistory
        fields = ['file_name', 
                  'uploaded_at', 
                  'reference_date', 
                  'updated_by',
                  'file_size', 
                  'row_count', 
                  'row_processed',
                  'row_failed',
                  'failed_rows']

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