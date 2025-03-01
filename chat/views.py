from django.shortcuts import render

def chat_home(request):
    """ Renders the chat home page where users can enter a room. """
    return render(request, 'chat/home.html')

def chat_room(request, room_name):
    """ Renders the chat room where WebSocket communication happens. """
    return render(request, 'chat/room.html', {"room_name": room_name})


def index_page(request,room_name):
    return render(request,'chat/index.html',{"room_name":room_name})