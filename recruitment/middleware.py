import logging
from django.http import JsonResponse
from django.core.exceptions import RequestDataTooBig

logger = logging.getLogger(__name__)

class FileUploadErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except RequestDataTooBig:
            logger.warning(f"File upload too large from {request.META.get('REMOTE_ADDR')}")
            return JsonResponse({
                'success': False,
                'error': 'Fichier trop volumineux',
                'max_size_mb': 5
            }, status=413)
