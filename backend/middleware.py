from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from .models import BlacklistedToken

class TokenBlacklistMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', None)

        if token:
            token = token.split(' ')[1]  # Assuming token is in format 'Token xxx'

            # Check if the token is blacklisted
            if BlacklistedToken.objects.filter(token=token).exists():
                return JsonResponse({"error": "Token has been blacklisted."}, status=401)