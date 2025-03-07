from django.urls import path
from . import views_web, views_api

urlpatterns = [
    # Web-based authentication
    path("login/", views_web.google_login, name="google_login"),
    path("callback/", views_web.google_callback, name="google_callback"),
    path("logout/", views_web.google_logout, name="google_logout"),
    path("dashboard/", views_web.login_view, name="login_view"),
    path("logout-page/", views_web.logout_view, name="logout_view"),

    # API-based authentication
    path("api/login/", views_api.google_login_api, name="google_login_api"),
    path("api/callback/", views_api.google_callback_api, name="google_callback_api"),
    path("api/logout/", views_api.google_logout_api, name="google_logout_api"),
]
