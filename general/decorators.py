from functools import wraps
from django.shortcuts import redirect

def human_verification_required(view_func):
    @wraps(view_func)
    
    def _wrapped_view(request, *args, **kwargs):
        print("human_verification_required")
        if not request.session.get('is_human'):
            return redirect(f'/verify-human/?next={request.path}')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
