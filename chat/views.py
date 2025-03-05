from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Room, Message

def chat_home(request):
    """ Renders the chat home page where users can enter or create a room. """
    rooms = Room.objects.all()
    return render(request, 'chat/home.html', {'rooms': rooms})

@login_required
def chat_room(request, room_name):
    """ Renders the chat room and fetches previous messages. """
    room, created = Room.objects.get_or_create(name=room_name)
    messages = Message.objects.filter(room=room).order_by("timestamp")
    
    return render(request, 'chat/index.html', {
        "room": room,
        "messages": messages
    })

@login_required
def create_room(request):
    """ Allows users to create a new chat room. """
    if request.method == "POST":
        room_name = request.POST.get("room_name")
        if room_name:
            room, created = Room.objects.get_or_create(name=room_name)
            return redirect("chat_room", room_name=room.name)
    
    return render(request, "chat/create_room.html")



