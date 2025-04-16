from django.urls import path
from .views import Notifications

urlpatterns = [
    path('notification/', Notifications.as_view())
]