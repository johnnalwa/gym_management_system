# gym_management_system/routing.py

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from accounts.consumers import VideoConferenceConsumer

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("accounts/", VideoConferenceConsumer.as_asgi()),
        ])
    ),
})
