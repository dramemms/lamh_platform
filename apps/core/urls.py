from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/export-pdf/", views.export_lamh_dashboard_pdf, name="export_lamh_dashboard_pdf"),
]