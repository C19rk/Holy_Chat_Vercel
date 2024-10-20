from django.shortcuts import redirect
from django.contrib import messages

class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Redirect to forbidden page if user is not authenticated and trying to access dashboard
        if request.path.startswith('/dashboard/') and not request.user.is_authenticated:
            return redirect('forbidden')
        
        response = self.get_response(request)

        # Optionally set cache control headers if you want to prevent caching
        if request.path.startswith('/dashboard/'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # HTTP 1.1
            response['Pragma'] = 'no-cache'  # HTTP 1.0
            response['Expires'] = '0'  # Proxies

        return response
