from django.conf import settings
from django.contrib.auth.views import redirect_to_login

EXEMPT_URLS = [
    '/admin/',       # o admin já tem sua própria proteção de login
    '/api-auth/',    # login da API do DRF
]

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            return self.get_response(request)
        if any(request.path.startswith(url) for url in EXEMPT_URLS):
            return self.get_response(request)
        return redirect_to_login(request.get_full_path())