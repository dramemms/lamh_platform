from django.urls import path
from . import views
from .api_kobo import kobo_victim_webhook

urlpatterns = [
    # =========================
    # LIST & DETAIL
    # =========================
    path("", views.victim_list, name="victim_list"),
    path("dashboard/", views.victim_dashboard, name="victim_dashboard"),
    path("dashboard/carte-cercles/", views.victim_cercle_heatmap, name="victim_cercle_heatmap"),
    path("detail/<int:pk>/", views.victim_detail, name="victim_detail"),
    path("detail/<int:pk>/edit/", views.victim_edit, name="victim_edit"),
    path("export-excel/", views.export_victims_excel, name="export_victims_excel"),
   

    # =========================
    # ➕ AJOUT VICTIME (lié à accident)
    # =========================
    path(
        "add/<int:accident_id>/",
        views.victim_add,
        name="victim_add"
    ),

    # ===================================
    # ➕ AJOUT ASSISTANCE (lié à victime)
    # ===================================

    path(
    "detail/<int:pk>/add-assistance/",
    views.victim_add_assistance_kobo,
    name="victim_add_assistance_kobo"
    ),

    # =========================
    # WORKFLOW
    # =========================
    path("detail/<int:pk>/tech-validate/", views.victim_tech_validate, name="victim_tech_validate"),
    path("detail/<int:pk>/program-validate/", views.victim_program_validate, name="victim_program_validate"),
    path("detail/<int:pk>/send-to-program/", views.victim_send_to_program, name="victim_send_to_program"),
    path("detail/<int:pk>/tech-reject/", views.victim_tech_reject, name="victim_tech_reject"),
    path("detail/<int:pk>/program-reject/", views.victim_program_reject, name="victim_program_reject"),
    path("detail/<int:pk>/approve/", views.victim_approve, name="victim_approve"),

    # =========================
    # KOBO WEBHOOK
    # =========================
    path("api/kobo/webhook/", kobo_victim_webhook, name="kobo_victim_webhook"),

    
]