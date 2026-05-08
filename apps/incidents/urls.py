from django.urls import path
from . import views

urlpatterns = [
    path("", views.accident_list, name="accident_list"),
    path("dashboard/", views.accident_dashboard, name="accident_dashboard"),

    path("export/excel/", views.export_accidents_excel, name="export_accidents_excel"),
    path(
        "dashboard/export-pdf/",
        views.export_accident_dashboard_pdf,
        name="export_lamh_dashboard_pdf",
    ),

    path("<int:pk>/", views.accident_detail, name="accident_detail"),
    path("<int:pk>/edit/", views.accident_edit, name="accident_edit"),

    # =========================
    # WORKFLOW (PROPRE)
    # =========================
    path("<int:pk>/submit/", views.accident_submit, name="accident_submit"),
    path("<int:pk>/tech-validate/", views.accident_tech_validate, name="accident_tech_validate"),
    path("<int:pk>/program-validate/", views.accident_program_validate, name="accident_program_validate"),
    path("<int:pk>/approve/", views.accident_approve, name="accident_approve"),

    path("<int:pk>/tech-reject/", views.accident_tech_reject, name="accident_tech_reject"),
    path("<int:pk>/program-reject/", views.accident_program_reject, name="accident_program_reject"),

    # =========================
    # (OPTIONNEL - fallback)
    # =========================
    path("<int:pk>/transition/<str:action>/", views.accident_transition, name="accident_transition"),
    path("<int:pk>/workflow/<str:action>/", views.accident_reject_or_return, name="accident_workflow_form"),
]