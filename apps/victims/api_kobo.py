import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.incidents.models import Accident
from apps.geo.models import Region, Cercle, Commune
from .models import Victim


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
        "y",
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
        parts = str(value).strip().split()
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
    if obj:
        return obj

    return None


def get_geo_coordinates(region=None, cercle=None, commune=None):
    if commune:
        lat = getattr(commune, "latitude", None)
        lon = getattr(commune, "longitude", None)
        if lat and lon:
            return lat, lon

    if cercle:
        lat = getattr(cercle, "latitude", None)
        lon = getattr(cercle, "longitude", None)
        if lat and lon:
            return lat, lon

    if region:
        lat = getattr(region, "latitude", None)
        lon = getattr(region, "longitude", None)
        if lat and lon:
            return lat, lon

    return None, None


@csrf_exempt
@require_POST
def kobo_victim_webhook(request):

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    print("=== KOBO VICTIM WEBHOOK ===")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    # =========================
    # ACCIDENT
    # =========================

    accident_ref = get_value(
        data,
        "g_report/accident_id",
        "accident_id",
        "id_accident",
        "g_report/id_accident",
        "g_identite/accident_id",
        "accident_reference",
    )

    print("Référence accident reçue :", accident_ref)

    if not accident_ref:
        return JsonResponse({"error": "accident_id manquant"}, status=400)

    accident = Accident.objects.filter(reference=accident_ref).first()

    print("Accident trouvé :", accident)

    if not accident:
        return JsonResponse(
            {
                "error": "Accident introuvable",
                "accident_ref": accident_ref,
            },
            status=400,
        )

    # =========================
    # LOCALISATION
    # =========================

    region_value = get_value(
        data,
        "g_location/region",
        "region",
        "q4_2",
    )

    cercle_value = get_value(
        data,
        "g_location/cercle",
        "cercle",
        "q4_3",
    )

    commune_value = get_value(
        data,
        "g_location/commune",
        "commune",
        "q4_4",
    )

    region = get_obj_by_code_or_name(Region, region_value)
    cercle = get_obj_by_code_or_name(Cercle, cercle_value)
    commune = get_obj_by_code_or_name(Commune, commune_value)

    gps_value = get_value(
        data,
        "g_location/location_gps",
        "g_location/gps",
        "location_gps",
        "gps",
    )

    latitude = get_value(
        data,
        "latitude",
        "g_location/latitude",
    )

    longitude = get_value(
        data,
        "longitude",
        "logitude",
        "g_location/longitude",
    )

    if not latitude or not longitude:
        latitude, longitude = parse_gps(gps_value)

    if not latitude or not longitude:
        latitude, longitude = get_geo_coordinates(
            region=region,
            cercle=cercle,
            commune=commune,
        )

    # =========================
    # IDENTITE VICTIME
    # =========================

    victim_id = get_value(
        data,
        "g_report/victim_id",
        "victim_id",
        "id_victime",
        "code_victime",
        "g_identite/code_victime",
        "q1_1",
    )

    if not victim_id:
        victim_id = f"VIC-{str(data.get('_id'))[-6:]}"

    victim_last_name = get_value(
        data,
        "g_victim/victim_last_name",
        "victim_last_name",
        "nom_victime",
        "q2_2",
    )

    victim_first_name = get_value(
        data,
        "g_victim/victim_first_name",
        "victim_first_name",
        "prenom_victime",
        "q2_3",
    )

    if not victim_last_name:
        victim_last_name = "Non renseigné"

    # =========================
    # CREATION VICTIME
    # =========================

    try:
        victim = Victim.objects.create(

            # Accident
            accident=accident,
            accident_reference=accident_ref,

            # Kobo / système
            kobo_submission_id=data.get("_id"),
            kobo_uuid=data.get("_uuid"),
            raw_payload=data,

            # Rapport
            victim_id=victim_id,
            report_date=get_value(
                data,
                "g_report/report_date",
                "report_date",
                "q1_2",
            ),
            reported_by=get_value(
                data,
                "g_report/reported_by",
                "reported_by",
                "q1_5",
            ),
            reporting_org=get_value(
                data,
                "g_report/reporting_org",
                "reporting_org",
                "q1_6",
            ),
            reporting_position=get_value(
                data,
                "g_report/reporting_position",
                "reporting_position",
                "q1_7",
            ),
            reporting_team=get_value(
                data,
                "g_report/reporting_team",
                "reporting_team",
                "q1_8",
            ),

            # Consentement
            consentement=to_bool(
                get_value(
                    data,
                    "g_victim/consentement",
                    "consentement",
                    "q2_1",
                )
            ),

            # Identité victime
            victim_last_name=victim_last_name,
            victim_first_name=victim_first_name,

            victim_type=get_value(
                data,
                "g_victim/victim_type",
                "victim_type",
                "q2_4",
            ),
            father_name=get_value(
                data,
                "g_victim/father_name",
                "father_name",
                "q2_5",
            ),
            mother_name=get_value(
                data,
                "g_victim/mother_name",
                "mother_name",
                "q2_6",
            ),

            nationality=get_value(
                data,
                "g_victim/nationality",
                "nationality",
                "q2_7",
            ),
            marital_status=get_value(
                data,
                "g_victim/marital_status",
                "marital_status",
                "q2_8",
            ),

            profession_before=get_value(
                data,
                "g_victim/profession_before",
                "profession_before",
                "q2_9",
            ),
            profession_after=get_value(
                data,
                "g_victim/profession_after",
                "profession_after",
                "q2_10",
            ),

            outcome_type=get_value(
                data,
                "g_victim/outcome_type",
                "outcome_type",
                "q2_11",
            ),

            birth_date_known=to_bool(
                get_value(
                    data,
                    "g_victim/birth_date_known",
                    "birth_date_known",
                    "q2_12",
                )
            ),
            birth_date=get_value(
                data,
                "g_victim/birth_date",
                "birth_date",
                "q2_12_1",
                "_2_12_2_Date_de_naissance_approximative",
            ),
            victim_age=to_int(
                get_value(
                    data,
                    "g_victim/victim_age",
                    "victim_age",
                    "_2_12_3_ge",
                )
            ),
            victim_sex=get_value(
                data,
                "g_victim/victim_sex",
                "victim_sex",
                "q2_13",
            ),

            main_breadwinner=to_bool(
                get_value(
                    data,
                    "g_victim/main_breadwinner",
                    "main_breadwinner",
                    "q2_14",
                )
            ),
            dependents_count=to_int(
                get_value(
                    data,
                    "g_victim/dependents_count",
                    "dependents_count",
                    "q2_15",
                )
            ),

            urgent_medical_evac=to_bool(
                get_value(
                    data,
                    "g_victim/urgent_medical_evac",
                    "urgent_medical_evac",
                    "q2_16",
                )
            ),

            victim_contact=get_value(
                data,
                "g_victim/victim_contact",
                "victim_contact",
                "q2_17",
            ),

            activity_at_accident=get_value(
                data,
                "g_victim/activity_at_accident",
                "activity_at_accident",
                "q2_18",
            ),

            knew_danger_zone=to_bool(
                get_value(
                    data,
                    "g_victim/knew_danger_zone",
                    "knew_danger_zone",
                    "q2_19",
                )
            ),
            reason_enter_zone=get_value(
                data,
                "g_victim/reason_enter_zone",
                "reason_enter_zone",
                "q2_20",
            ),
            times_entered_zone=to_int(
                get_value(
                    data,
                    "g_victim/times_entered_zone",
                    "times_entered_zone",
                    "q2_21",
                )
            ),

            saw_object=to_bool(
                get_value(
                    data,
                    "g_victim/saw_object",
                    "saw_object",
                    "q2_22",
                )
            ),

            blast_cause=get_value(
                data,
                "g_victim/blast_cause",
                "blast_cause",
                "q2_23",
            ),
            alpc_type=get_value(
                data,
                "g_victim/alpc_type",
                "alpc_type",
                "q2_23_2",
            ),

            received_er_before=to_bool(
                get_value(
                    data,
                    "g_victim/received_er_before",
                    "received_er_before",
                    "q2_24",
                )
            ),
            received_er_after=to_bool(
                get_value(
                    data,
                    "g_victim/received_er_after",
                    "received_er_after",
                    "q2_25",
                )
            ),

            pre_existing_disability=to_bool(
                get_value(
                    data,
                    "g_victim/pre_existing_disability",
                    "pre_existing_disability",
                    "q2_27",
                )
            ),

            health_structure=get_value(
                data,
                "g_victim/health_structure",
                "health_structure",
                "q2_31",
            ),
            medical_care=to_bool(
                get_value(
                    data,
                    "g_victim/medical_care",
                    "medical_care",
                    "q2_32",
                )
            ),
            non_medical_care=to_bool(
                get_value(
                    data,
                    "g_victim/non_medical_care",
                    "non_medical_care",
                    "q2_35",
                )
            ),

            # Source information
            info_source=get_value(
                data,
                "g_source/info_source",
                "info_source",
                "q3_1",
            ),
            source_age=to_int(
                get_value(
                    data,
                    "g_source/source_age",
                    "source_age",
                    "q3_2",
                )
            ),
            source_last_name=get_value(
                data,
                "g_source/source_last_name",
                "source_last_name",
                "q3_2_2",
            ),
            source_first_name=get_value(
                data,
                "g_source/source_first_name",
                "source_first_name",
                "q3_3",
            ),
            source_contact=get_value(
                data,
                "g_source/source_contact",
                "source_contact",
                "q3_4",
            ),
            source_sex=get_value(
                data,
                "g_source/source_sex",
                "source_sex",
                "q3_5",
            ),

            # Localisation
            country=get_value(
                data,
                "g_location/country",
                "country",
                "q4_1",
            ),
            region=region,
            cercle=cercle,
            commune=commune,
            village_quartier=get_value(
                data,
                "g_location/village",
                "g_location/village_quartier",
                "g_location/localite",
                "village_quartier",
                "village",
                "q4_5",
            ),

            latitude=latitude,
            longitude=longitude,

            # Workflow
            status=Victim.STATUS_SUBMITTED,
        )

        return JsonResponse(
            {
                "status": "success",
                "victim_pk": victim.id,
                "victim_id": victim.victim_id,
                "accident_reference": accident_ref,
                "latitude": latitude,
                "longitude": longitude,
                "source_coordinates": "kobo_gps" if gps_value else "geo_database",
            },
            status=201,
        )

    except Exception as e:
        print("Erreur création victime :", str(e))
        return JsonResponse({"error": str(e)}, status=400)