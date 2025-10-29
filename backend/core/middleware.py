import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class SecurityMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if 'sql' in request.GET or 'script' in request.POST:  # Простая проверка на инъекции
            logger.warning(f"Suspicious request from {request.META.get('REMOTE_ADDR')}: {request.path}")
            # Можно добавить блокировку IP
