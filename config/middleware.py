from django.http import HttpResponseRedirect
from django.conf import settings

COUNT = 1 if settings.DEBUG else 2

def redirect_to_www(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.get_host().count('.') < COUNT:
           return HttpResponseRedirect(f'{request.scheme}://www.{request.get_host()}{request.get_full_path()}')
        response = get_response(request)
        # Code to be executed for each request/response after
        # the view is called.
        return response

    return middleware