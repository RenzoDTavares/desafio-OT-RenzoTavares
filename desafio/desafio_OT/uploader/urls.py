from django.urls import path
from rest_framework.permissions import AllowAny
from .views import FileUploadView, UploadHistoryView, CustomAuthToken

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('history/', UploadHistoryView.as_view(), name='upload-history'),
    path('token/', CustomAuthToken.as_view(), name='token_obtain_pair'),
]
