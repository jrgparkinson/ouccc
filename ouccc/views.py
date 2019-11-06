from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse


def home(request):
    context = {'title': 'Home'}
    return render(request, 'index.html', context)

