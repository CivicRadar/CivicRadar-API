from django.urls import path
from .views import SignUp, Login, Profile, PasswordTokenCheck, RequestPasswordReset, SetNewPassword

urlpatterns = [
    path('signup/', SignUp.as_view()),
    path('login/', Login.as_view()),
    path('profile/', Profile.as_view()),
    path('request-reset-email/', RequestPasswordReset.as_view(), name='request-reset-email'),
    path('password-reset/<ui64>/<token>/', PasswordTokenCheck.as_view(), name='password-reset-confirmed'),
    path('password-reset-complete/', SetNewPassword.as_view(), name='password-reset-complete'),
    # path('email-verification/<token>/', )
]