from django.urls import path
from . import views

app_name = "reporting"

urlpatterns = [

    path(
        "",
        views.reporting_home,
        name="reporting_home"
    ),

    path(
        "assistance-form/",
        views.assistance_form,
        name="assistance_form"
    ),

    path(
        "api/kobo/pai/webhook/",
        views.kobo_pai_webhook,
        name="kobo_pai_webhook"
    ),

    path(
        "assistance/<int:pk>/",
        views.assistance_detail,
        name="assistance_detail"
    ),

    path(
        "export-excel/",
        views.export_assistance_excel,
        name="export_assistance_excel"
    ),

    path(
        "dashboard/",
        views.assistance_dashboard,
        name="assistance_dashboard"
    ),

]