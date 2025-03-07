from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Room, Message
from django.contrib import messages

def chat_home(request):
    """ Renders the chat home page where users can enter or create a room. """
    rooms = Room.objects.all()
    return render(request, 'chat/join_room.html', {'rooms': rooms})

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
def chat_home(request):
    """ Renders the chat home page where users can enter or create a room. """
    rooms = Room.objects.all()  # Get all available rooms

    if request.method == "POST":
        room_name = request.POST.get("room_name")
        
        if room_name:
            try:
                room = Room.objects.get(name=room_name)  # Try to fetch the room
                return redirect("chat_room", room_name=room.name)  # If room exists, redirect to that room
            except Room.DoesNotExist:
                # If the room doesn't exist, show an error message
                messages.error(request, "Room does not exist. Please choose a valid room name.")
    
    return render(request, 'chat/join_room.html', {'rooms': rooms})

@login_required
def creates_room(request):
    """ Allows users to create a new chat room. """
    if request.method == "POST":
        room_name = request.POST.get("room_name")
        if room_name:
            room, created = Room.objects.create(name=room_name)
            return redirect("chat_room", room_name=room.name)
    



@login_required
def create_room(request):
    """ Allows users to create a new chat room. """
    if request.method == "POST":
        room_name = request.POST.get("room_name")
        
        if room_name:
            # Check if room already exists
            if Room.objects.filter(name=room_name).exists():
                # Show warning if room already exists
                messages.warning(request, "Room already exists. Please choose a different name.")
                return redirect("create_room")  # Stay on the create room page
            else:
                # Create the new room if it doesn't exist
                room = Room.objects.create(name=room_name)
                return redirect("chat_room", room_name=room.name)  # Redirect to the created room
    
    return render(request, "chat/create_room.html")





