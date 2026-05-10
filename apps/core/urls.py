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

]