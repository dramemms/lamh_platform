from django.http import JsonResponse
from .models import Cercle, Commune


def cercles_by_region(request, region_id):
    data = list(
        Cercle.objects.filter(region_id=region_id)
        .order_by("name")
        .values("id", "name", "code")
    )
    return JsonResponse(data, safe=False)


def communes_by_cercle(request, cercle_id):
    data = list(
        Commune.objects.filter(cercle_id=cercle_id)
        .order_by("name")
        .values("id", "name", "code")
    )
    return JsonResponse(data, safe=False)