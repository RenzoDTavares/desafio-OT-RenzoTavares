# middleware.py
from django.http import JsonResponse

class EndpointValidationMiddleware:
    VALID_ENDPOINTS = [
        '/api/v1/search/',  # Adicione aqui seus endpoints válidos
        '/api/v1/token/',
        '/api/v1/upload/',
        '/api/v1/history/',
        '/api/v1/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Permite o acesso ao admin sem validação
        if request.path.startswith('/admin/'):
            return self.get_response(request)

        # Valida o endpoint se não for para o admin
        if request.path not in self.VALID_ENDPOINTS:
            return JsonResponse({"error": "Endpoint não encontrado."}, status=404)

        # Continua com o processamento da request
        response = self.get_response(request)
        return response
