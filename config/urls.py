from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from apps.core import views as core_views


urlpatterns = [

    path("admin/", admin.site.urls),

    path("", core_views.home, name="home"),

    # AJOUT IMPORTANT
    path("", include("apps.core.urls")),

    path(
        "dashboard/",
        core_views.dashboard,
        name="dashboard"
    ),

    path(
        "reporting/",
        include("apps.reporting.urls")
    ),

    path(
        "geo/",
        include("apps.geo.urls")
    ),

    path(
        "incidents/",
        include("apps.incidents.urls")
    ),

    path(
        "victims/",
        include("apps.victims.urls")
    ),

    path(
        "eree/",
        include("apps.eree.urls")
    ),

    path(
        "api/",
        include("apps.api.urls")
    ),

    path(
        "accounts/",
        include("apps.accounts.urls")
    ),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

]