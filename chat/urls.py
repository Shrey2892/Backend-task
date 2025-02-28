from django.urls import path
from .views import chat_home, chat_room

urlpatterns = [
    path('', chat_home, name='chat_home'),  # Main chat page
    path('<str:room_name>/', chat_room, name='chat_room'),  # Dynamic room name
]
