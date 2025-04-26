from django.urls import path
from .views import Notifications, Like, Points, CommentReactions, Comments

urlpatterns = [
    path('notification/', Notifications.as_view()),
    path('like/', Like.as_view()),
    path('points/', Points.as_view()),
    path('comment/', Comments.as_view()),
    path('comment-reaction/', CommentReactions.as_view()),
]