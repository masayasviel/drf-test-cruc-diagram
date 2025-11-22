from django.urls import path

from .views import GetCreateUserAPIView, GetUpdateUserAPIView

urlpatterns = [
    path("users", GetCreateUserAPIView.as_view(), name="get_create_user"),
    path("users/<str:user_code>", GetUpdateUserAPIView.as_view(), name="get_update_user"),
]
