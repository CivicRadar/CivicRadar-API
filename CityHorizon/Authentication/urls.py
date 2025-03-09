from django.urls import path
from .views import SignUp, Login, Profile

urlpatterns = [
    path('signup/', SignUp.as_view()),
    path('login/', Login.as_view()),
    path('profile/', Profile.as_view()),
]