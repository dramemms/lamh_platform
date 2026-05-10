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

]