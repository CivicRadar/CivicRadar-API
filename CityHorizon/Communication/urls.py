from django.urls import path
from .views import Notifications, Like

urlpatterns = [
    path('notification/', Notifications.as_view()),
    path('like/', Like.as_view()),
]