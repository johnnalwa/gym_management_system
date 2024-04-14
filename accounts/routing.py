from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import accounts.routing
from .consumers import VideoConferenceConsumer

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            accounts.routing.websocket_urlpatterns
        )
    ),
})





websocket_urlpatterns = [
    path('ws/<str:room_name>/', VideoConferenceConsumer.as_asgi()),
]