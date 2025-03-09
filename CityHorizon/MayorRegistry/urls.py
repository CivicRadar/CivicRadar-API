from django.urls import path
from .views import Add, List, Update, Delete

urlpatterns = [
    path('add/', Add.as_view()),
    path('list/', List.as_view()),
    path('update/', Update.as_view()),
    path('delete/', Delete.as_view()),
]