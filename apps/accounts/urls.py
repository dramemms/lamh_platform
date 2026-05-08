# apps/accounts/urls.py

from django.urls import path

from . import views

urlpatterns = [

    # Dashboard utilisateurs
    path(
        "admin-users/",
        views.admin_users,
        name="admin_users"
    ),

    # Activer utilisateur
    path(
        "admin-users/<int:user_id>/activate/",
        views.admin_user_activate,
        name="admin_user_activate"
    ),

    # Désactiver utilisateur
    path(
        "admin-users/<int:user_id>/deactivate/",
        views.admin_user_deactivate,
        name="admin_user_deactivate"
    ),

    # Reset password
    path(
        "admin-users/<int:user_id>/reset-password/",
        views.admin_user_reset_password,
        name="admin_user_reset_password"
    ),

    # Changement mot de passe
    path(
        "change-password/",
        views.change_password,
        name="change_password"
    ),

    # Password expiré
    path(
        "password-expired/",
        views.temporary_password_expired,
        name="temporary_password_expired"
    ),
]

urlpatterns = [
    path("admin-users/", views.admin_users, name="admin_users"),

    path(
        "admin-users/create/",
        views.admin_user_create,
        name="admin_user_create"
    ),

    path(
        "admin-users/<int:user_id>/edit/",
        views.admin_user_edit,
        name="admin_user_edit"
    ),

    path(
        "admin-users/<int:user_id>/reset-password/",
        views.admin_user_reset_password,
        name="admin_user_reset_password"
    ),

    path(
        "admin-users/<int:user_id>/activate/",
        views.admin_user_activate,
        name="admin_user_activate"
    ),

    path(
        "admin-users/<int:user_id>/deactivate/",
        views.admin_user_deactivate,
        name="admin_user_deactivate"
    ),

    path(
        "change-password/",
        views.change_password,
        name="change_password"
    ),

    path(
        "password-expired/",
        views.temporary_password_expired,
        name="temporary_password_expired"
    ),

    


path(
    "admin-groups/",
    views.admin_groups,
    name="admin_groups",
),

path(
    "admin-groups/create/",
    views.admin_group_create,
    name="admin_group_create",
),

path(
    "admin-groups/<int:group_id>/edit/",
    views.admin_group_edit,
    name="admin_group_edit",
),

path(
    "admin-groups/<int:group_id>/delete/",
    views.admin_group_delete,
    name="admin_group_delete",
),

]