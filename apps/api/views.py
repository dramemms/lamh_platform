import json
from decimal import Decimal

from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from apps.geo.models import Region, Cercle, Commune
from apps.incidents.models import Accident


def _to_decimal(value):
    if value in (None, "", "None"):
        return None
    try:
        return Decimal(str(value))
    except Exception:
        return None


def _to_int(value):
    if value in (None, "", "None"):
        return None
    try:
        return int(value)
    except Exception:
        return None


@csrf_exempt
def kobo_accident_webhook(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Méthode non autorisée.")

    try:
        payload = json.loads(request.body.decode("utf-8"))
        print("PAYLOAD KOBO =", payload)
    except Exception as e:
        print("JSON ERROR =", e)
        return HttpResponseBadRequest("Payload JSON invalide.")

    data = payload.get("data", payload)
    print("DATA KOBO =", data)

    reference = data.get("reporting/accident_id")
    title = data.get("meta/instanceName") or "Accident Kobo"

    report_date = data.get("reporting/report_date")
    org_name = data.get("reporting/org_name")
    reported_by = data.get("reporting/reported_by")
    position = data.get("reporting/position")
    team = data.get("reporting/team")
    funding_source = data.get("reporting/funding_source")
    accident_associe_id = data.get("reporting/accident_associe_id")

    accident_date = data.get("accident_details/accident_date")
    accident_time = data.get("accident_details/accident_time")
    category = data.get("accident_details/type_accident")
    impact = data.get("accident_details/area_type")
    number_victims = data.get("accident_details/number_victims")
    other_damage = data.get("accident_details/other_damage")
    activity_at_time = data.get("accident_details/activity_at_time")
    description = data.get("accident_details/description")
    device_type = data.get("accident_details/device_type")
    device_status = data.get("accident_details/device_status")
    device_marked = data.get("accident_details/device_marked")

    country = data.get("location/country")
    region_code = data.get("location/region")
    cercle_code = data.get("location/cercle")
    commune_code = data.get("location/commune")
    locality = data.get("location/locality")
    secure_access = data.get("location/secure_access")
    src_coordinates = data.get("location/src_coordinates")
    location_gps = data.get("location/location_gps")
    latitude = data.get("location/latitude")
    longitude = data.get("location/longitude")

    source_last_name = data.get("source_details/source_last_name")
    source_first_name = data.get("source_details/source_first_name")
    source_contact = data.get("source_details/source_contact")
    source_gender = data.get("source_details/source_gender")
    source_age = data.get("source_details/source_age")
    source_type = data.get("source_details/source_type")

    if not reference:
        print("ERREUR: champ 'reference' manquant")
        return HttpResponseBadRequest("Le champ reference est obligatoire.")

    try:
        region = Region.objects.get(code=str(region_code)) if region_code else None
        cercle = Cercle.objects.get(code=str(cercle_code)) if cercle_code else None
        commune = Commune.objects.get(code=str(commune_code)) if commune_code else None
    except Exception as e:
        print("ERREUR GEO =", e)
        return HttpResponseBadRequest(f"Erreur géographique: {e}")

    accident, created = Accident.objects.update_or_create(
        reference=reference,
        defaults={
            "title": title,
            "description": description,

            "report_date": report_date,
            "org_name": org_name,
            "reported_by": reported_by,
            "position": position,
            "team": team,
            "funding_source": funding_source,
            "accident_associe_id": accident_associe_id,

            "accident_date": accident_date,
            "accident_time": accident_time or None,
            "category": category,
            "impact": impact or Accident.IMPACT_NONE,
            "number_victims": _to_int(number_victims),
            "other_damage": other_damage,
            "activity_at_time": activity_at_time,
            "device_type": device_type,
            "device_status": device_status,
            "device_marked": device_marked,

            "country": country,
            "region": region,
            "cercle": cercle,
            "commune": commune,
            "locality": locality,
            "secure_access": secure_access,
            "src_coordinates": src_coordinates,
            "location_gps": location_gps,
            "latitude": _to_decimal(latitude),
            "longitude": _to_decimal(longitude),

            "source": Accident.SOURCE_KOBO,
            "source_name": f"{source_first_name or ''} {source_last_name or ''}".strip(),
            "source_contact": source_contact,
            "source_last_name": source_last_name,
            "source_first_name": source_first_name,
            "source_gender": source_gender,
            "source_age": _to_int(source_age),
            "source_type": source_type,

            "kobo_submission_id": str(data.get("_id") or ""),
            "kobo_uuid": data.get("_uuid"),
            "raw_payload": payload,
            "is_synced": True,
        },
    )

    if created and not accident.submitted_at:
        accident.submitted_at = timezone.now()
        accident.status = Accident.STATUS_SUBMITTED
        accident.save(update_fields=["submitted_at", "status"])

    print("ACCIDENT CREE/MAJ =", accident.reference, created)

    return JsonResponse({
        "success": True,
        "created": created,
        "reference": accident.reference,
    })