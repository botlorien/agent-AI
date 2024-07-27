from django.urls import path
from .views import ChatAPIView, chat_view

urlpatterns = [
    path('api/chat/', ChatAPIView.as_view(), name='chat-api'),
    path('chat/', chat_view, name='chat-view'),
]
