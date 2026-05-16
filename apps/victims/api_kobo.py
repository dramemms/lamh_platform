# apps/victims/api_kobo.py

import json


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date

from apps.geo.models import Cercle, Commune, Region
from apps.incidents.models import Accident
from apps.victims.models import Victim
from apps.notifications.services import notify_victim_submitted


# =========================================================
# HELPERS
# =========================================================

def val(data, *keys, default=None):
    for key in keys:
        value = data.get(key)
        if value not in [None, "", "null"]:
            return value
    return default


def parse_bool(value):
    return str(value).strip().lower() in [
        "true",
        "oui",
        "yes",
        "1",
        "o",
        "y",
    ]


def parse_int(value):
    try:
        if value in [None, "", "null"]:
            return None
        return int(float(value))
    except Exception:
        return None


def clean_coord(value):
    try:
        if value in [None, "", "null"]:
            return None

        value = str(value).strip()

        if " " in value:
            value = value.split()[0]

        number = round(float(value), 6)

        if abs(number) >= 1000:
            return None

        return number

    except Exception:
        return None


def get_obj_by_code_or_name(model, value):
    if not value:
        return None

    value = str(value).strip()

    obj = model.objects.filter(code=value).first()
    if obj:
        return obj

    return model.objects.filter(name__iexact=value).first()


def only_existing_fields(model, values):
    model_fields = {field.name for field in model._meta.fields}

    return {
        key: value
        for key, value in values.items()
        if key in model_fields
    }


# =========================================================
# WEBHOOK
# =========================================================

@csrf_exempt
def kobo_victim_webhook(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Méthode non autorisée"},
            status=405
        )

    try:
        payload = json.loads(request.body.decode("utf-8"))
        data = payload.get("data", payload)

        # =====================================================
        # ACCIDENT
        # =====================================================

        accident_reference = val(
            data,
            "accident_id",
            "g_report/accident_id",
            "g_report/accident_reference",
            "g_identite/accident_id",
            "g_identite/accident_reference",
            "accident_reference",
            "reference",
            "id_accident",
            "numero_accident",
            "num_accident",
            "q1_3",
        )

        if not accident_reference:
            return JsonResponse(
                {
                    "error": (
                        "Le numéro d'accident est obligatoire "
                        "pour créer une victime."
                    )
                },
                status=400
            )

        accident_reference = str(accident_reference).strip()

        # =====================================================
        # DATE ACCIDENT KOBO
        # =====================================================

        accident_date = parse_date(
            str(
                val(
                    data,
                    "accident_date",
                    "g_report/accident_date",
                    "date_accident",
                    "q1_4",
                ) or ""
            )
        )

        # =====================================================
        # RECHERCHE ACCIDENT
        # =====================================================

        accident = Accident.objects.filter(
            reference__iexact=accident_reference,
            accident_date=accident_date,
        ).first()

        if not accident:
            return JsonResponse(
                {
                    "error": (
                        f"Aucun accident trouvé avec "
                        f"le numéro {accident_reference} "
                        f"et la date {accident_date}"
                    )
                },
                status=400
            )


        # =====================================================
        # GEO
        # =====================================================

        region = get_obj_by_code_or_name(
            Region,
            val(
                data,
                "region",
                "g_location/region",
                "g_localisation/region",
                "q4_2",
            ),
        )

        cercle = get_obj_by_code_or_name(
            Cercle,
            val(
                data,
                "cercle",
                "g_location/cercle",
                "g_localisation/cercle",
                "q4_3",
            ),
        )

        commune = get_obj_by_code_or_name(
            Commune,
            val(
                data,
                "commune",
                "g_location/commune",
                "g_localisation/commune",
                "q4_4",
            ),
        )

        if commune and not cercle:
            cercle = commune.cercle

        if cercle and not region:
            region = cercle.region

        # =====================================================
        # GPS
        # =====================================================

        gps_value = val(
            data,
            "g_location/location_gps",
            "location_gps",
            "gps",
        )

        gps_lat = None
        gps_lon = None

        if gps_value:
            parts = str(gps_value).split()

            if len(parts) >= 2:
                gps_lat = clean_coord(parts[0])
                gps_lon = clean_coord(parts[1])

        latitude = (
            clean_coord(
                val(
                    data,
                    "latitude",
                    "g_location/latitude",
                )
            )
            or gps_lat
        )

        longitude = (
            clean_coord(
                val(
                    data,
                    "longitude",
                    "logitude",
                    "g_location/longitude",
                )
            )
            or gps_lon
        )

        # =====================================================
        # ID VICTIME
        # =====================================================

        kobo_id = str(data.get("_id", ""))

        victim_id = val(
            data,
            "victim_id",
            "id_victime",
            "code_victime",
            "g_report/victim_id",
            "q1_1",
            default=f"VIC-{kobo_id[-6:]}",
        )

        # =====================================================
        # VALUES
        # =====================================================

        values = {
            # =================================================
            # SYSTEME
            # =================================================

            "raw_payload": data,
            "kobo_submission_id": data.get("_id"),
            "kobo_uuid": data.get("_uuid"),

            "status": Victim.STATUS_SUBMITTED,

            # =================================================
            # ACCIDENT
            # =================================================

            "accident": accident,
            "accident_reference": getattr(accident, "reference", accident_reference),

            # =================================================
            # REPORTING
            # =================================================

            "victim_id": victim_id,

            "report_date": parse_date(
                str(
                    val(
                        data,
                        "q1_2",
                        "report_date",
                    ) or ""
                )
            ),

            "reported_by": val(
                data,
                "q1_5",
                "reported_by",
            ),

            "reporting_org": val(
                data,
                "q1_6",
                "reporting_org",
            ),

            "reporting_position": val(
                data,
                "q1_7",
                "reporting_position",
            ),

            "reporting_team": val(
                data,
                "q1_8",
                "reporting_team",
            ),

            # =================================================
            # IDENTITE
            # =================================================

            "consentement": parse_bool(
                val(
                    data,
                    "q2_1",
                    "consentement",
                )
            ),

            "victim_last_name": (
                val(
                    data,
                    "q2_2",
                    "victim_last_name",
                    "nom_victime",
                )
                or "Non renseigné"
            ),

            "victim_first_name": val(
                data,
                "q2_3",
                "victim_first_name",
                "prenom_victime",
            ),

            "victim_type": val(
                data,
                "q2_4",
                "victim_type",
            ),

            "father_name": val(
                data,
                "q2_5",
                "father_name",
            ),

            "mother_name": val(
                data,
                "q2_6",
                "mother_name",
            ),

            "nationality": val(
                data,
                "q2_7",
                "nationality",
            ),

            "marital_status": val(
                data,
                "q2_8",
                "marital_status",
            ),

            "profession_before": val(
                data,
                "q2_9",
                "profession_before",
            ),

            "profession_after": val(
                data,
                "q2_10",
                "profession_after",
            ),

            "outcome_type": val(
                data,
                "q2_11",
                "outcome_type",
            ),

            "birth_date_known": parse_bool(
                val(
                    data,
                    "q2_12",
                    "birth_date_known",
                )
            ),

            "birth_date": parse_date(
                str(
                    val(
                        data,
                        "q2_12_1",
                        "birth_date",
                    ) or ""
                )
            ),

            "victim_age": parse_int(
                val(
                    data,
                    "_2_12_3_ge",
                    "q2_12_3",
                    "victim_age",
                )
            ),

            "victim_sex": val(
                data,
                "q2_13",
                "victim_sex",
            ),

            "main_breadwinner": parse_bool(
                val(
                    data,
                    "q2_14",
                    "main_breadwinner",
                )
            ),

            "dependents_count": parse_int(
                val(
                    data,
                    "q2_15",
                    "dependents_count",
                )
            ),

            "urgent_medical_evac": parse_bool(
                val(
                    data,
                    "q2_16",
                    "urgent_medical_evac",
                )
            ),

            "victim_contact": val(
                data,
                "q2_17",
                "victim_contact",
            ),

            # =================================================
            # CONTEXTE ACCIDENT
            # =================================================

            "activity_at_accident": val(
                data,
                "q2_18",
                "activity_at_accident",
            ),

            "knew_danger_zone": parse_bool(
                val(
                    data,
                    "q2_19",
                    "knew_danger_zone",
                )
            ),

            "reason_enter_zone": val(
                data,
                "q2_20",
                "reason_enter_zone",
            ),

            "times_entered_zone": parse_int(
                val(
                    data,
                    "q2_21",
                    "times_entered_zone",
                )
            ),

            "saw_object": parse_bool(
                val(
                    data,
                    "q2_22",
                    "saw_object",
                )
            ),

            "blast_cause": val(
                data,
                "q2_23",
                "blast_cause",
            ),

            "alpc_type": val(
                data,
                "q2_23_2",
                "alpc_type",
            ),

            # =================================================
            # SANTE
            # =================================================

            "received_er_before": parse_bool(
                val(
                    data,
                    "q2_24",
                    "received_er_before",
                )
            ),

            "received_er_after": parse_bool(
                val(
                    data,
                    "q2_25",
                    "received_er_after",
                )
            ),

            "pre_existing_disability": parse_bool(
                val(
                    data,
                    "q2_27",
                    "pre_existing_disability",
                )
            ),

            "injury_type": val(
                data,
                "q2_28",
                "injury_type",
            ),

            "loss_of": val(
                data,
                "q2_29",
                "loss_of",
            ),

            "injury_description": val(
                data,
                "q2_30",
                "injury_description",
            ),

            "health_structure": val(
                data,
                "q2_31",
                "health_structure",
            ),

            "medical_care": parse_bool(
                val(
                    data,
                    "q2_32",
                    "medical_care",
                )
            ),

            "non_medical_care": parse_bool(
                val(
                    data,
                    "q2_35",
                    "non_medical_care",
                )
            ),

            # =================================================
            # SOURCE
            # =================================================

            "info_source": val(
                data,
                "q3_1",
                "info_source",
            ),

            "source_age": parse_int(
                val(
                    data,
                    "q3_2",
                    "source_age",
                )
            ),

            "source_last_name": val(
                data,
                "q3_2_2",
                "source_details/source_last_name",
                "source_last_name",
                "source_lastname",
                "last_name",
            ),

            "source_first_name": val(
                data,
                "q3_3",
                "source_first_name",
            ),

            "source_contact": val(
                data,
                "q3_4",
                "source_contact",
            ),

            "source_sex": val(
                data,
                "q3_5",
                "source_sex",
            ),

            # =================================================
            # LOCALISATION
            # =================================================

            "country": val(
                data,
                "q4_1",
                "country",
                "pays",
            ),

            "region": region,
            "cercle": cercle,
            "commune": commune,

            "village_quartier": val(
                data,
                "q4_5",
                "village_quartier",
                "village",
                "quartier",
            ),

            "latitude": latitude,
            "longitude": longitude,
        }

        # =====================================================
        # FILTRE CHAMPS EXISTANTS
        # =====================================================

        values = only_existing_fields(
            Victim,
            values
        )

        victim = Victim.objects.create(
            **values
        )

        notify_victim_submitted(victim)

        return JsonResponse(
            {
                "success": True,
                "victim_pk": victim.pk,
                "victim_id": victim.victim_id,
                "accident_reference": accident_reference,
            },
            status=201,
        )

    except Exception as e:
        print("ERREUR WEBHOOK VICTIM :", str(e))

        return JsonResponse(
            {"error": str(e)},
            status=400
        )