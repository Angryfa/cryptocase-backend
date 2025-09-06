from django.urls import path
from .views import RegisterView, LoginView, MeView, RefreshView, ProfileView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/",    LoginView.as_view(),    name="login"),
    path("me/",       MeView.as_view(),       name="me"),
    path("refresh/",  RefreshView.as_view(),  name="refresh"),
    path("profile/",  ProfileView.as_view(),  name="profile"),
]
