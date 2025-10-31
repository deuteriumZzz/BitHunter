import logging

from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class SecurityMiddleware(MiddlewareMixin):
    """
    Middleware для обеспечения базовой безопасности веб-приложения.

    Проверяет входящие запросы на наличие потенциально опасных параметров,
    таких как 'sql' в GET-параметрах или 'script' в POST-параметрах.
    Логирует подозрительные запросы и блокирует доступ по IP-адресу.
    """

    def process_request(self, request):
        """
        Обрабатывает входящий запрос перед его передачей в view.

        Проверяет запрос на наличие подозрительных параметров.
        Если найдены, логирует предупреждение и блокирует доступ.

        :param request: Объект HttpRequest Django.
        :return: HttpResponseForbidden если запрос подозрительный, иначе None.
        """
        if "sql" in request.GET or "script" in request.POST:
            remote_addr = request.META.get("REMOTE_ADDR")
            logger.warning(f"Подозрительный запрос от {remote_addr}: {request.path}")
            return HttpResponseForbidden("Доступ запрещен")
        return None

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Блокировка подозрительных строк
        blocked_patterns = ["sql", "script", "javascript", "<script>", "union select"]
        for key, value in request.GET.items():
            if any(pattern in str(value).lower() for pattern in blocked_patterns):
                return HttpResponseForbidden("Suspicious request")
        # Логирование
        logger.warning(
            f"Suspicious request from {request.META.get('REMOTE_ADDR')}: {request.GET}"
        )
        return self.get_response(request)
