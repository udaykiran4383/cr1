from django.urls import path
from . import views

urlpatterns = [
    path('', views.points, name='points'),  # Your points view
    path('register/', views.register, name='register'),  # Your register view
    path('success/', views.success_view, name='success_view'),  # Your success view

    path('tasks/', views.tasks_view, name='tasks_view'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard_view'),
]
