from django.urls import path
from . import views
from .api_kobo import kobo_eree_webhook

urlpatterns = [
    path("", views.eree_list, name="eree_list"),
    path("dashboard/", views.eree_dashboard, name="eree_dashboard"),
    path("dashboard/page2/", views.eree_dashboard_page2, name="eree_dashboard_page2"),
    path("add/", views.eree_add, name="eree_add"),
    path("detail/<int:pk>/", views.eree_detail, name="eree_detail"),
    path("detail/<int:pk>/edit/", views.eree_edit, name="eree_edit"),

    # 🔥 EXPORT EXCEL
    path("export-excel/", views.export_eree_excel, name="export_eree_excel"),

    # WORKFLOW
    path("detail/<int:pk>/tech-validate/", views.eree_tech_validate, name="eree_tech_validate"),
    path("detail/<int:pk>/send-to-program/", views.eree_send_to_program, name="eree_send_to_program"),
    path("detail/<int:pk>/program-validate/", views.eree_program_validate, name="eree_program_validate"),
    path("detail/<int:pk>/tech-reject/", views.eree_tech_reject, name="eree_tech_reject"),
    path("detail/<int:pk>/program-reject/", views.eree_program_reject, name="eree_program_reject"),
    path("detail/<int:pk>/approve/", views.eree_approve, name="eree_approve"),

    # KOBO
    path("api/kobo/webhook/", kobo_eree_webhook, name="kobo_eree_webhook"),
]