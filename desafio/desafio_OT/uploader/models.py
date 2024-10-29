from django.db import models

class UploadHistory(models.Model):
    file_name = models.CharField(max_length=255, unique=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    reference_date = models.DateField(default='1954-01-01')
    updated_by = models.CharField(max_length=255, blank=True) 
    file_size = models.PositiveIntegerField(null=True, blank=True, default=0) 
    row_count = models.PositiveIntegerField(null=True, blank=True, default=0)  
    row_processed = models.PositiveIntegerField(null=True, blank=True, default=0)  
    row_failed = models.PositiveIntegerField(null=True, blank=True, default=0) 
    failed_rows = models.TextField(blank=True)  

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