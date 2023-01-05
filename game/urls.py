from django.urls import path
from .views import *

urlpatterns = [
    path('', LoginUser.as_view(), name='login'),
    path('login/', LoginUser.as_view(), name='login'),  # http://127.0.0.1:8000/login
    path('register/', RegisterUser.as_view(), name='register'),  # http://127.0.0.1:8000/register
    path('monotony_game/', monotony_game_page, name='monotony_game'),  # http://127.0.0.1:8000/monotony_game
]
