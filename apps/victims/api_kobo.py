# apps/victims/api_kobo.py

import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.geo.models import Region, Cercle, Commune
from apps.incidents.models import Accident
from .models import Victim


# =========================================================
# HELPERS
# =========================================================

def get_value(data, *keys, default=None):
    for key in keys:
        value = data.get(key)

        if value not in [None, ""]:
            return value

    return default


def to_bool(value):

    if value is None:
        return False

    return str(value).strip().lower() in [
        "yes",
        "true",
        "1",
        "oui",
        "o",
    ]


def to_int(value):

    try:

        if value in [None, ""]:
            return None

        return int(value)

    except Exception:
        return None


def parse_gps(value):

    if not value:
        return None, None

    try:

        parts = str(value).split()

        if len(parts) >= 2:
            return float(parts[0]), float(parts[1])

    except Exception:
        pass

    return None, None


def get_obj_by_code_or_name(model, value):

    if not value:
        return None

    value = str(value).strip()

    obj = model.objects.filter(code=value).first()

    if obj:
        return obj

    obj = model.objects.filter(name__iexact=value).first()

    return obj


# =========================================================
# WEBHOOK VICTIM
# =========================================================

@csrf_exempt
@require_POST
def kobo_victim_webhook(request):

    try:
        data = json.loads(request.body.decode("utf-8"))

    except Exception:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )

    print("\n================ KOBO VICTIM WEBHOOK ================\n")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    # =====================================================
    # ACCIDENT
    # =====================================================

    accident_ref = get_value(
        data,
        "accident_id",
        "g_report/accident_id",
        "accident_reference",
        "id_accident",
    )

    if not accident_ref:

        return JsonResponse(
            {"error": "accident_id manquant"},
            status=400
        )

    accident = Accident.objects.filter(
        reference=accident_ref
    ).first()

    if not accident:

        return JsonResponse(
            {
                "error": "Accident introuvable",
                "reference": accident_ref,
            },
            status=400,
        )

    # =====================================================
    # GEO
    # =====================================================

    region = get_obj_by_code_or_name(
        Region,
        get_value(data, "region", "g_location/region"),
    )

    cercle = get_obj_by_code_or_name(
        Cercle,
        get_value(data, "cercle", "g_location/cercle"),
    )

    commune = get_obj_by_code_or_name(
        Commune,
        get_value(data, "commune", "g_location/commune"),
    )

    # Auto récupération cercle / région

    if commune and not cercle:
        cercle = commune.cercle

    if cercle and not region:
        region = cercle.region

    # =====================================================
    # GPS
    # =====================================================

    gps_value = get_value(
        data,
        "location_gps",
        "g_location/location_gps",
    )

    latitude = get_value(data, "latitude")
    longitude = get_value(data, "longitude")

    if not latitude or not longitude:
        latitude, longitude = parse_gps(gps_value)

    # =====================================================
    # VICTIM ID
    # =====================================================

    victim_id = get_value(
        data,
        "victim_id",
        "code_victime",
        "g_identite/code_victime",
    )

    if not victim_id:
        victim_id = f"VIC-{str(data.get('_id'))[-6:]}"

    # =====================================================
    # NOMS VICTIME
    # =====================================================

    victim_last_name = get_value(
        data,
        "victim_last_name",
        "nom_victime",
        "q1_5",
    )

    if not victim_last_name:
        victim_last_name = "Non renseigné"

    victim_first_name = get_value(
        data,
        "victim_first_name",
        "prenom_victime",
        "q1_6",
    )

    # =====================================================
    # DATE KOBO
    # =====================================================

    submitted_at_kobo = get_value(
        data,
        "_submission_time",
        "_date_modified",
        "end",
    )

    # =====================================================
    # CREATE
    # =====================================================

    try:

        victim = Victim.objects.create(

            # =========================
            # SYSTEM
            # =========================

            raw_payload=data,

            kobo_submission_id=data.get("_id"),
            kobo_uuid=data.get("_uuid"),

            submitted_at_kobo=submitted_at_kobo,

            status=Victim.STATUS_SUBMITTED,

            # =========================
            # ACCIDENT
            # =========================

            accident=accident,
            accident_reference=accident_ref,

            # =========================
            # IDENTITE
            # =========================

            victim_id=victim_id,

            victim_last_name=victim_last_name,
            victim_first_name=victim_first_name,

            victim_age=to_int(
                get_value(
                    data,
                    "victim_age",
                    "age_victime",
                )
            ),

            victim_sex=get_value(
                data,
                "victim_sex",
                "sexe_victime",
            ),

            outcome_type=get_value(
                data,
                "outcome_type",
                "situation_victime",
            ),

            # =========================
            # SOURCE
            # =========================

            info_source=get_value(
                data,
                "info_source",
                "source",
            ),

            source_last_name=get_value(
                data,
                "source_last_name",
                "nom_source",
            ),

            source_first_name=get_value(
                data,
                "source_first_name",
                "prenom_source",
            ),

            source_contact=get_value(
                data,
                "source_contact",
                "contact_source",
            ),

            source_age=to_int(
                get_value(
                    data,
                    "source_age",
                    "age_source",
                )
            ),

            source_sex=get_value(
                data,
                "source_sex",
                "sexe_source",
            ),

            # =========================
            # LOCATION
            # =========================

            country=get_value(
                data,
                "country",
                "pays",
            ),

            region=region,
            cercle=cercle,
            commune=commune,

            village_quartier=get_value(
                data,
                "village_quartier",
                "village",
                "quartier",
                "localite",
            ),

            latitude=latitude,
            longitude=longitude,

            # =========================
            # CONTEXTE
            # =========================

            activity_at_accident=get_value(
                data,
                "activity_at_accident",
                "activite",
            ),

            blast_cause=get_value(
                data,
                "blast_cause",
                "cause_explosion",
            ),

            # =========================
            # MEDICAL
            # =========================

            health_structure=get_value(
                data,
                "health_structure",
                "structure_sante",
            ),

            medical_care=to_bool(
                get_value(
                    data,
                    "medical_care",
                    "prise_charge_medicale",
                )
            ),

            non_medical_care=to_bool(
                get_value(
                    data,
                    "non_medical_care",
                    "prise_charge_non_medicale",
                )
            ),
        )

        return JsonResponse(
            {
                "status": "success",
                "victim_pk": victim.pk,
                "victim_id": victim.victim_id,
            },
            status=201,
        )

    except Exception as e:

        print("\n================ ERREUR WEBHOOK VICTIM ================\n")
        print(str(e))

        return JsonResponse(
            {"error": str(e)},
            status=400,
        )