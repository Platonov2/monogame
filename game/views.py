from django.http import HttpResponse
from django.template import loader

# Create your views here.
def game(request):
    return HttpResponse(loader.get_template('game.html').render())