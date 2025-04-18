from django.urls import path
from .views import Notifications, Like, Points

urlpatterns = [
    path('notification/', Notifications.as_view()),
    path('like/', Like.as_view()),
    path('points/', Points.as_view()),
]