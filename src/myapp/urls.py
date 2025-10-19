from django.urls import path

from .views import GetCreateUserAPIView

urlpatterns = [
    path('users', GetCreateUserAPIView.as_view(), name='users')
]
