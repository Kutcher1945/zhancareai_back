import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.layers import get_channel_layer
from django.urls import path
from zhancareai_back.websocket_consumers import VideoCallConsumer  # Import WebSocket consumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zhancareai_back.settings")
django.setup()

# ✅ Define WebSocket routes
websocket_urlpatterns = [
    path("ws/video-call/<str:meeting_id>/", VideoCallConsumer.as_asgi()),
]

# ✅ ASGI application handling HTTP & WebSockets
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
})

channel_layer = get_channel_layer()

app = application