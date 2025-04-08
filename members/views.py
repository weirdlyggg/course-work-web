from django.shortcuts import render

from django.http import HttpResponse
from django.template import loader
from .models import User

def members(request):
  myusers = User.objects.all().values() 
  template = loader.get_template('first.html')
  context = {
    'myusers' : myusers,
  }
  return HttpResponse(template.render(context, request))
