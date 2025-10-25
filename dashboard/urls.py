from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.control_room_dashboard, name='control_room'),
]
