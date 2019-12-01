from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
# Create your views here.

from django.http import HttpResponse


def home(request):
    context = {'title': 'Home'}
    return render(request, 'index.html', context)


def handler404(request, exception, template_name="404.html"):
    response = render_to_response(template_name)
    response.status_code = 404
    return response

def handler403(request, exception, template_name="403.html"):
    response = render_to_response(template_name)
    response.status_code = 403
    return response

def handler500(request, *args, **argv):
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response