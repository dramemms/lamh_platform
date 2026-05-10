from django.urls import path
from . import views

urlpatterns = [

    # =========================
    # DASHBOARD PRINCIPAL
    # =========================
    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),

    # =========================
    # EXPORT PDF DASHBOARD
    # =========================
    path(
        "dashboard/export-pdf/",
        views.export_lamh_dashboard_pdf,
        name="export_lamh_dashboard_pdf"
    ),

    # =========================
    # GESTION DES DONNEES
    # =========================
    path(
        "data-management/",
        views.data_management,
        name="data_management"
    ),

  
   # =========================
# GESTION ACCIDENTS
# =========================

path(
    "data-management/accidents/",
    views.manage_accidents,
    name="manage_accidents"
),

path(
    "data-management/accidents/<int:pk>/edit/",
    views.edit_accident,
    name="edit_accident"
),

path(
    "data-management/accidents/<int:pk>/delete/",
    views.delete_accident,
    name="delete_accident"
),


# =========================
# GESTION VICTIMES
# =========================

path(
    "data-management/victims/",
    views.manage_victims,
    name="manage_victims"
),

path(
    "data-management/victims/<int:pk>/edit/",
    views.edit_victim,
    name="edit_victim"
),

path(
    "data-management/victims/<int:pk>/delete/",
    views.delete_victim,
    name="delete_victim"
),


# =========================
# GESTION EREE
# =========================

path(
    "data-management/eree/",
    views.manage_eree,
    name="manage_eree"
),

path(
    "data-management/eree/<int:pk>/edit/",
    views.edit_eree,
    name="edit_eree"
),

path(
    "data-management/eree/<int:pk>/delete/",
    views.delete_eree,
    name="delete_eree"
),

path("data-management/regions/", views.manage_regions, name="manage_regions"),
path("data-management/cercles/", views.manage_cercles, name="manage_cercles"),
path("data-management/communes/", views.manage_communes, name="manage_communes"),

# =========================
# REGIONS
# =========================

path("data-management/regions/", views.manage_regions, name="manage_regions"),
path("data-management/regions/<int:pk>/edit/", views.edit_region, name="edit_region"),
path("data-management/regions/<int:pk>/delete/", views.delete_region, name="delete_region"),

# =========================
# CERCLES
# =========================

path("data-management/cercles/", views.manage_cercles, name="manage_cercles"),
path("data-management/cercles/<int:pk>/edit/", views.edit_cercle, name="edit_cercle"),
path("data-management/cercles/<int:pk>/delete/", views.delete_cercle, name="delete_cercle"),

# =========================
# COMMUNES
# =========================

path("data-management/communes/", views.manage_communes, name="manage_communes"),
path("data-management/communes/<int:pk>/edit/", views.edit_commune, name="edit_commune"),
path("data-management/communes/<int:pk>/delete/", views.delete_commune, name="delete_commune"),

]