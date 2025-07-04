from django.shortcuts import redirect
from django.urls import resolve, reverse, NoReverseMatch

class HumanVerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Print path being accessed
        if (request.path == "/"):
            return self.get_response(request)
        verified_at = request.session.get('is_human_verified_at')
        print("[Middleware] Request path:", request.path)
        print("[Middleware] is_human session:", request.session.get('is_human', False))

        try:
            captcha_url = reverse('general:captcha')
        except NoReverseMatch:
            print("[Middleware] 'captcha' URL not found. Skipping verification.")
            return self.get_response(request)

        exempt_paths = [captcha_url,  '/about-us','/logout','/login','/register','/get-download-progress/' ,'/static/', '/media/']
        if any(request.path.startswith(p) for p in exempt_paths):
            print("[Middleware] Exempt path:", request.path)
            return self.get_response(request)
        
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if not user_agent or any(bot_keyword in user_agent.lower() for bot_keyword in ['bot', 'crawl', 'spider']):
            print("[Middleware] Suspicious User-Agent detected:", user_agent)
            return redirect(f"{captcha_url}?next={request.path}")

        if not request.session.get('is_human', False):
            print("[Middleware] Not verified. Redirecting to CAPTCHA.")
            return redirect(f"{captcha_url}?next={request.path}")

        print("[Middleware] Verified. Proceeding.")
        return self.get_response(request)
