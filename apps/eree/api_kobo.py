import json
from datetime import datetime

from django.conf import settings
from django.http import JsonResponse
from django.utils.dateparse import parse_date, parse_datetime
from django.views.decorators.csrf import csrf_exempt

from apps.geo.models import Region, Cercle, Commune
from .models import EREESession


def _to_int(v):
    try:
        return int(v) if v not in (None, "", "null") else 0
    except Exception:
        return 0


def _parse_datetime(v):
    if not v:
        return None

    dt = parse_datetime(v)
    if dt:
        return dt

    try:
        return datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except Exception:
        return None


def _normalize(v):
    return str(v or "").strip()


def _find_region(value):
    value = _normalize(value)
    if not value:
        return None

    obj = Region.objects.filter(code=value).first()
    if obj:
        return obj

    obj = Region.objects.filter(name__iexact=value).first()
    if obj:
        return obj

    return Region.objects.filter(name__icontains=value).first()


def _find_cercle(value, region=None):
    value = _normalize(value)
    if not value:
        return None

    qs = Cercle.objects.all()
    if region:
        qs = qs.filter(region=region)

    obj = qs.filter(code=value).first()
    if obj:
        return obj

    obj = qs.filter(name__iexact=value).first()
    if obj:
        return obj

    return qs.filter(name__icontains=value).first()


def _find_commune(value, cercle=None):
    value = _normalize(value)
    if not value:
        return None

    qs = Commune.objects.all()
    if cercle:
        qs = qs.filter(cercle=cercle)

    obj = qs.filter(code=value).first()
    if obj:
        return obj

    obj = qs.filter(name__iexact=value).first()
    if obj:
        return obj

    return qs.filter(name__icontains=value).first()


def _extract_gps(data):
    gps = data.get("g_session/location_gps") or data.get("location_gps")

    if gps:
        try:
            lat, lon, *_ = str(gps).split()
            return gps, float(lat), float(lon)
        except Exception:
            return gps, None, None

    geolocation = data.get("_geolocation")
    if isinstance(geolocation, list) and len(geolocation) >= 2:
        try:
            lat = float(geolocation[0])
            lon = float(geolocation[1])
            return f"{lat} {lon}", lat, lon
        except Exception:
            pass

    return None, None, None


@csrf_exempt
def kobo_eree_webhook(request):
    auth_header = request.headers.get("Authorization", "")
    expected_token = f"Token {settings.KOBO_WEBHOOK_TOKEN}"

    if auth_header != expected_token:
        return JsonResponse(
            {
                "error": "Unauthorized",
                "received": auth_header,
                "expected": expected_token,
            },
            status=403,
        )

    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "invalid JSON"}, status=400)

    data = payload.get("_submission_json") or payload

    submission_id = (
        data.get("_id")
        or data.get("meta/instanceID")
        or data.get("__id")
        or data.get("id")
    )

    if not submission_id:
        return JsonResponse(
            {
                "error": "missing submission id",
                "available_keys": sorted(list(data.keys()))[:120],
            },
            status=400,
        )

    reference = f"EREE-{submission_id}"

    region_value = data.get("g_session/region") or data.get("region")
    cercle_value = data.get("g_session/cercle") or data.get("cercle")
    commune_value = data.get("g_session/commune") or data.get("commune")

    region = _find_region(region_value)
    cercle = _find_cercle(cercle_value, region=region)
    commune = _find_commune(commune_value, cercle=cercle)

    if not commune and commune_value:
        commune = _find_commune(commune_value)
        if commune:
            cercle = commune.cercle
            region = commune.cercle.region

    if commune and not cercle:
        cercle = commune.cercle

    if cercle and not region:
        region = cercle.region

    if not region or not cercle or not commune:
        return JsonResponse(
            {
                "error": "geo not found",
                "details": "Région, cercle ou commune introuvable dans la base.",
                "received": {
                    "region": region_value,
                    "cercle": cercle_value,
                    "commune": commune_value,
                },
                "sample_keys": sorted(list(data.keys()))[:120],
            },
            status=400,
        )

    session_date = parse_date(
        data.get("g_session/session_date") or data.get("session_date")
    )

    if not session_date:
        return JsonResponse(
            {
                "error": "invalid date",
                "value": data.get("g_session/session_date") or data.get("session_date"),
            },
            status=400,
        )

    week_from = parse_date(data.get("g_weekly/week_from"))
    week_to = parse_date(data.get("g_weekly/week_to"))
    quality_date = parse_date(data.get("g_quality/quality_date"))

    organisation = data.get("g_weekly/organisation") or "Sans organisation"
    location_gps, latitude, longitude = _extract_gps(data)

    total_pdi = sum(_to_int(v) for k, v in data.items() if "pdi_" in k)
    total_host = sum(_to_int(v) for k, v in data.items() if "ch_" in k)

    humanitarian_male = _to_int(data.get("g_session/humanitarian_male"))
    humanitarian_female = _to_int(data.get("g_session/humanitarian_female"))

    total_participants = (
        total_pdi
        + total_host
        + humanitarian_male
        + humanitarian_female
    )

    obj, created = EREESession.objects.update_or_create(
        kobo_submission_id=str(submission_id),
        defaults={
            "reference": reference,
            "title": f"EREE - {organisation}",

            "reported_by": data.get("g_weekly/reported_by"),
            "organisation": organisation,
            "narrative_description": data.get("g_weekly/narrative_description"),
            "week_number": _to_int(data.get("g_weekly/week_number")) or None,
            "week_from": week_from,
            "week_to": week_to,
            "month_name": data.get("g_weekly/month_name"),
            "year": _to_int(data.get("g_weekly/year")) or None,

            "session_date": session_date,
            "location_gps": location_gps,
            "latitude": latitude,
            "longitude": longitude,
            "team": data.get("g_session/team"),
            "session_status": data.get("g_session/status"),
            "region_code": region_value,
            "cercle_code": cercle_value,
            "commune_code": commune_value,
            "region": region,
            "cercle": cercle,
            "commune": commune,
            "village": data.get("g_session/village"),
            "methodology": data.get("g_session/methodology"),
            "sensitization_type": data.get("g_session/sensitization_type"),
            "civilian_subcategory": data.get("g_session/civilian_subcategory"),
            "humanitarian_org_type": data.get("g_session/humanitarian_org_type"),
            "other_precision": data.get("g_session/other_precision"),
            "humanitarian_male": humanitarian_male,
            "humanitarian_female": humanitarian_female,
            "funding_type": data.get("g_session/funding_type"),

            "pdi_boys_0_5": _to_int(data.get("g_pdi/pdi_boys_0_5")),
            "pdi_boys_0_5_dis": _to_int(data.get("g_pdi/pdi_boys_0_5_dis")),
            "pdi_girls_0_5": _to_int(data.get("g_pdi/pdi_girls_0_5")),
            "pdi_girls_0_5_dis": _to_int(data.get("g_pdi/pdi_girls_0_5_dis")),
            "pdi_boys_6_14": _to_int(data.get("g_pdi/pdi_boys_6_14")),
            "pdi_boys_6_14_dis": _to_int(data.get("g_pdi/pdi_boys_6_14_dis")),
            "pdi_girls_6_14": _to_int(data.get("g_pdi/pdi_girls_6_14")),
            "pdi_girls_6_14_dis": _to_int(data.get("g_pdi/pdi_girls_6_14_dis")),
            "pdi_boys_15_17": _to_int(data.get("g_pdi/pdi_boys_15_17")),
            "pdi_boys_15_17_dis": _to_int(data.get("g_pdi/pdi_boys_15_17_dis")),
            "pdi_girls_15_17": _to_int(data.get("g_pdi/pdi_girls_15_17")),
            "pdi_girls_15_17_dis": _to_int(data.get("g_pdi/pdi_girls_15_17_dis")),
            "pdi_men_18_24": _to_int(data.get("g_pdi/pdi_men_18_24")),
            "pdi_men_18_24_dis": _to_int(data.get("g_pdi/pdi_men_18_24_dis")),
            "pdi_women_18_24": _to_int(data.get("g_pdi/pdi_women_18_24")),
            "pdi_women_18_24_dis": _to_int(data.get("g_pdi/pdi_women_18_24_dis")),
            "pdi_men_25_49": _to_int(data.get("g_pdi/pdi_men_25_49")),
            "pdi_men_25_49_dis": _to_int(data.get("g_pdi/pdi_men_25_49_dis")),
            "pdi_women_25_49": _to_int(data.get("g_pdi/pdi_women_25_49")),
            "pdi_women_25_49_dis": _to_int(data.get("g_pdi/pdi_women_25_49_dis")),
            "pdi_men_50_59": _to_int(data.get("g_pdi/pdi_men_50_59")),
            "pdi_men_50_59_dis": _to_int(data.get("g_pdi/pdi_men_50_59_dis")),
            "pdi_women_50_59": _to_int(data.get("g_pdi/pdi_women_50_59")),
            "pdi_women_50_59_dis": _to_int(data.get("g_pdi/pdi_women_50_59_dis")),
            "pdi_men_60_plus": _to_int(data.get("g_pdi/pdi_men_60_plus")),
            "pdi_men_60_plus_dis": _to_int(data.get("g_pdi/pdi_men_60_plus_dis")),
            "pdi_women_60_plus": _to_int(data.get("g_pdi/pdi_women_60_plus")),
            "pdi_women_60_plus_dis": _to_int(data.get("g_pdi/pdi_women_60_plus_dis")),

            "ch_boys_0_5": _to_int(data.get("g_ch/ch_boys_0_5")),
            "ch_boys_0_5_dis": _to_int(data.get("g_ch/ch_boys_0_5_dis")),
            "ch_girls_0_5": _to_int(data.get("g_ch/ch_girls_0_5")),
            "ch_girls_0_5_dis": _to_int(data.get("g_ch/ch_girls_0_5_dis")),
            "ch_boys_6_14": _to_int(data.get("g_ch/ch_boys_6_14")),
            "ch_boys_6_14_dis": _to_int(data.get("g_ch/ch_boys_6_14_dis")),
            "ch_girls_6_14": _to_int(data.get("g_ch/ch_girls_6_14")),
            "ch_girls_6_14_dis": _to_int(data.get("g_ch/ch_girls_6_14_dis")),
            "ch_boys_15_17": _to_int(data.get("g_ch/ch_boys_15_17")),
            "ch_boys_15_17_dis": _to_int(data.get("g_ch/ch_boys_15_17_dis")),
            "ch_girls_15_17": _to_int(data.get("g_ch/ch_girls_15_17")),
            "ch_girls_15_17_dis": _to_int(data.get("g_ch/ch_girls_15_17_dis")),
            "ch_men_18_24": _to_int(data.get("g_ch/ch_men_18_24")),
            "ch_men_18_24_dis": _to_int(data.get("g_ch/ch_men_18_24_dis")),
            "ch_women_18_24": _to_int(data.get("g_ch/ch_women_18_24")),
            "ch_women_18_24_dis": _to_int(data.get("g_ch/ch_women_18_24_dis")),
            "ch_men_25_49": _to_int(data.get("g_ch/ch_men_25_49")),
            "ch_men_25_49_dis": _to_int(data.get("g_ch/ch_men_25_49_dis")),
            "ch_women_25_49": _to_int(data.get("g_ch/ch_women_25_49")),
            "ch_women_25_49_dis": _to_int(data.get("g_ch/ch_women_25_49_dis")),
            "ch_men_50_59": _to_int(data.get("g_ch/ch_men_50_59")),
            "ch_men_50_59_dis": _to_int(data.get("g_ch/ch_men_50_59_dis")),
            "ch_women_50_59": _to_int(data.get("g_ch/ch_women_50_59")),
            "ch_women_50_59_dis": _to_int(data.get("g_ch/ch_women_50_59_dis")),
            "ch_men_60_plus": _to_int(data.get("g_ch/ch_men_60_plus")),
            "ch_men_60_plus_dis": _to_int(data.get("g_ch/ch_men_60_plus_dis")),
            "ch_women_60_plus": _to_int(data.get("g_ch/ch_women_60_plus")),
            "ch_women_60_plus_dis": _to_int(data.get("g_ch/ch_women_60_plus_dis")),
            "leaflets_adults": _to_int(data.get("g_ch/leaflets_adults")),
            "leaflets_children": _to_int(data.get("g_ch/leaflets_children")),

            "quality_date": quality_date,
            "quality_team": data.get("g_quality/quality_team"),
            "quality_method": data.get("g_quality/quality_method"),
            "quality_observations": data.get("g_quality/quality_observations"),
            "difficulties_solutions": data.get("g_quality/difficulties_solutions"),

            "total_pdi": total_pdi,
            "total_host_community": total_host,
            "total_participants": total_participants,

            "kobo_uuid": data.get("_uuid"),
            "submitted_at_kobo": _parse_datetime(data.get("_submission_time")),
            "raw_payload": data,
        },
    )

    if obj.status == EREESession.STATUS_DRAFT:
        obj.status = EREESession.STATUS_SUBMITTED
        obj.submitted_at = obj.submitted_at_kobo
        obj.save()

    return JsonResponse(
    {
        "success": True,
        "created": created,
        "reference": obj.reference,
        "participants": obj.total_participants,
        "total_pdi": obj.total_pdi,
        "total_host_community": obj.total_host_community,
    }
)