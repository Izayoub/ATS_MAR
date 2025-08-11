import time
import logging
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger('ai_engine')


class MatchingMiddleware:
    """Middleware pour le service de matching"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.log_requests = getattr(settings, 'LOG_MATCHING_REQUESTS', True)

    def __call__(self, request):
        start_time = time.time()

        # Traitement de la requête
        response = self.get_response(request)

        # Logging pour les endpoints AI Engine
        if request.path.startswith('/ai_engine/') and self.log_requests:
            duration_ms = (time.time() - start_time) * 1000

            logger.info(
                f"AI_ENGINE {request.method} {request.path} "
                f"[{response.status_code}] {duration_ms:.1f}ms"
            )

            # Ajouter headers de performance
            response['X-AI-Engine-Duration'] = f"{duration_ms:.1f}ms"
            response['X-AI-Engine-Version'] = "simplified-v1.0"

        return response

    def process_exception(self, request, exception):
        """Gestion des exceptions AI Engine"""
        if request.path.startswith('/ai_engine/api/'):
            logger.error(f"Exception AI Engine: {request.path} - {str(exception)}")

            return JsonResponse({
                'success': False,
                'error': 'Erreur interne du service de matching',
                'timestamp': time.time()
            }, status=500)

        return None