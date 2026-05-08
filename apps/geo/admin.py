from django.contrib import admin
from .models import Region, Cercle, Commune


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(Cercle)
class CercleAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "region")
    list_filter = ("region",)
    search_fields = ("name", "code", "region__name")


@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "cercle")
    list_filter = ("cercle__region", "cercle")
    search_fields = ("name", "code", "cercle__name", "cercle__region__name")