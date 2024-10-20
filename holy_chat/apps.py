from django.apps import AppConfig


class HolyChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'holy_chat'

from django.shortcuts import render

def homepage(request):
    return render(request, 'homepage.html')
