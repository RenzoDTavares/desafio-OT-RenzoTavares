# middleware.py
from django.http import JsonResponse

class EndpointValidationMiddleware:
    VALID_ENDPOINTS = [
        '/uploads/search/',  # Adicione aqui seus endpoints válidos
        '/uploads/token/',
        '/uploads/upload/',
        '/uploads/history/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Valida o endpoint
        if request.path not in self.VALID_ENDPOINTS:
            return JsonResponse({"error": "Endpoint não encontrado."}, status=404)

        # Continua com o processamento da request
        response = self.get_response(request)
        return response
