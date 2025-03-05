from django.urls import path
from .views import chat_home, chat_room, create_room

urlpatterns = [
    path('', chat_home, name='chat_home'),  # Main chat page
    path('create/', create_room, name='create_room'),  # Create room page
    path('<str:room_name>/', chat_room, name='chat_room'),  # Chat room
]
