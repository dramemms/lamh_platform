from django.urls import path
from . import views

urlpatterns = [
    path("api/cercles/<int:region_id>/", views.cercles_by_region, name="geo_cercles_by_region"),
    path("api/communes/<int:cercle_id>/", views.communes_by_cercle, name="geo_communes_by_cercle"),
]