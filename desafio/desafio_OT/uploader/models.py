from django.db import models

class UploadHistory(models.Model):
    file_name = models.CharField(max_length=255, unique=True)  
    uploaded_at = models.DateTimeField(auto_now_add=True)
    reference_date = models.DateField(default='1954-01-01')
    
    def __str__(self):
        return f"{self.file_name} - {self.reference_date}"

class Data(models.Model):
    RptDt = models.DateField(default='1954-01-01')
    TckrSymb = models.CharField(max_length=20, default='N/A')
    MktNm = models.CharField(max_length=50, default='N/A')
    SctyCtgyNm = models.CharField(max_length=50, default='N/A')
    ISIN = models.CharField(max_length=12, default='N/A')
    CrpnNm = models.CharField(max_length=255, default='N/A')
    
    def __str__(self):
       return f"{self.tckr_symb} - {self.rpt_dt}"