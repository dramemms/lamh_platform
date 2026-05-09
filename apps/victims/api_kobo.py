# apps/victims/api_kobo.py

import json
import uuid

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from django.utils import timezone

from apps.victims.models import Victim
from apps.incidents.models import Accident
from apps.geo.models import Region, Cercle, Commune


def val(data, *keys, default=None):
    """
    Retourne la première valeur trouvée.
    """
    for key in keys:
        value = data.get(key)

        if value not in [None, "", "null"]:
            return value

    return default


def parse_bool(value):
    if value in [True, "true", "True", "oui", "Oui", "yes", "1", 1]:
        return True

    return False


@csrf_exempt
def kobo_victim_webhook(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Méthode non autorisée"},
            status=405
        )

    try:

        payload = json.loads(request.body.decode("utf-8"))

        # =====================================================
        # DONNÉES KOBO
        # =====================================================

        data = payload.get("data", payload)

        # =====================================================
        # ACCIDENT
        # =====================================================

        accident_reference = val(
            data,
            "accident_id",
            "g_accident/accident_id",
            "q1_3",
        )

        if not accident_reference:
            return JsonResponse(
                {"error": "accident_id manquant"},
                status=400
            )

        try:
            accident = Accident.objects.get(
                reference=accident_reference
            )

        except Accident.DoesNotExist:
            return JsonResponse(
                {
                    "error": f"Accident introuvable : {accident_reference}"
                },
                status=400
            )

        # =====================================================
        # GEO
        # =====================================================

        region_name = val(
            data,
            "region",
            "g_localisation/region",
            "q_region",
        )

        cercle_name = val(
            data,
            "cercle",
            "g_localisation/cercle",
            "q_cercle",
        )

        commune_name = val(
            data,
            "commune",
            "g_localisation/commune",
            "q_commune",
        )

        region = None
        cercle = None
        commune = None

        if region_name:
            region = Region.objects.filter(
                name__iexact=region_name
            ).first()

        if cercle_name:
            cercle = Cercle.objects.filter(
                name__iexact=cercle_name
            ).first()

        if commune_name:
            commune = Commune.objects.filter(
                name__iexact=commune_name
            ).first()

        # =====================================================
        # ID VICTIME
        # =====================================================

        kobo_id = str(data.get("_id", ""))

        victim_id = f"VIC-{kobo_id[-6:]}"

        # =====================================================
        # NOM / PRENOM
        # =====================================================

        full_name = val(
            data,
            "q1_5",
            "victim_name",
            "g_identite/nom_complet",
        )

        victim_last_name = ""
        victim_first_name = ""

        if full_name:

            parts = full_name.split()

            if len(parts) >= 2:
                victim_last_name = parts[-1]
                victim_first_name = " ".join(parts[:-1])

            else:
                victim_last_name = full_name

        else:

            victim_last_name = val(
                data,
                "last_name",
                "victim_last_name",
                "g_identite/nom",
                default="-"
            )

            victim_first_name = val(
                data,
                "first_name",
                "victim_first_name",
                "g_identite/prenom",
                default="-"
            )

        # =====================================================
        # CREATION VICTIME
        # =====================================================

        victim = Victim.objects.create(

            # =================================================
            # SYSTEME
            # =================================================

            uuid=str(uuid.uuid4()),
            raw_data=data,

            kobo_submission_id=data.get("_id"),
            kobo_uuid=data.get("_uuid"),

            submitted_at=timezone.now(),
            created_at=timezone.now(),
            updated_at=timezone.now(),

            status=Victim.STATUS_SUBMITTED,

            # =================================================
            # IDENTITE
            # =================================================

            victim_id=victim_id,

            victim_last_name=victim_last_name,
            victim_first_name=victim_first_name,

            victim_gender=val(
                data,
                "gender",
                "sex",
                "g_identite/sexe",
            ),

            victim_age=val(
                data,
                "age",
                "g_identite/age",
            ),

            victim_type=val(
                data,
                "victim_type",
                "g_identite/type_victime",
            ),

            outcome_type=val(
                data,
                "outcome_type",
                "g_identite/issue",
            ),

            consent_given=parse_bool(
                val(
                    data,
                    "consent",
                    "g_identite/consentement",
                )
            ),

            father_name=val(
                data,
                "father_name",
                "g_identite/nom_pere",
            ),

            mother_name=val(
                data,
                "mother_name",
                "g_identite/nom_mere",
            ),

            nationality=val(
                data,
                "nationality",
                "g_identite/nationalite",
            ),

            marital_status=val(
                data,
                "marital_status",
                "g_identite/statut_matrimonial",
            ),

            profession_before=val(
                data,
                "profession_before",
                "g_identite/profession_avant",
            ),

            profession_after=val(
                data,
                "profession_after",
                "g_identite/profession_apres",
            ),

            # =================================================
            # ACCIDENT
            # =================================================

            accident=accident,
            accident_reference=accident.reference,

            activity=val(
                data,
                "activity",
                "g_contexte/activite",
            ),

            dangerous_area=parse_bool(
                val(
                    data,
                    "dangerous_area",
                    "g_contexte/zone_dangereuse",
                )
            ),

            entry_reason=val(
                data,
                "entry_reason",
                "g_contexte/raison_entree",
            ),

            object_seen=parse_bool(
                val(
                    data,
                    "object_seen",
                    "g_contexte/objet_vu",
                )
            ),

            explosion_cause=val(
                data,
                "explosion_cause",
                "g_contexte/cause_explosion",
            ),

            alpc_type=val(
                data,
                "alpc_type",
                "g_contexte/type_alpc",
            ),

            # =================================================
            # SANTE
            # =================================================

            emergency_evacuation=parse_bool(
                val(
                    data,
                    "emergency_evacuation",
                    "g_sante/evacuation_urgence",
                )
            ),

            prior_erw_session=parse_bool(
                val(
                    data,
                    "session_er_avant",
                    "g_sante/session_er_avant",
                )
            ),

            post_erw_session=parse_bool(
                val(
                    data,
                    "session_er_apres",
                    "g_sante/session_er_apres",
                )
            ),

            preexisting_disability=parse_bool(
                val(
                    data,
                    "handicap_preexistant",
                    "g_sante/handicap_preexistant",
                )
            ),

            injury_type=val(
                data,
                "type_blessure",
                "g_sante/type_blessure",
            ),

            body_part_loss=val(
                data,
                "perte_de",
                "g_sante/perte_de",
            ),

            injury_description=val(
                data,
                "description_blessure",
                "g_sante/description_blessure",
            ),

            health_structure=val(
                data,
                "structure_sante",
                "g_sante/structure_sante",
            ),

            medical_care=parse_bool(
                val(
                    data,
                    "prise_charge_medicale",
                    "g_sante/prise_charge_medicale",
                )
            ),

            non_medical_care=parse_bool(
                val(
                    data,
                    "prise_charge_non_medicale",
                    "g_sante/prise_charge_non_medicale",
                )
            ),

            # =================================================
            # SOURCE
            # =================================================

            source=val(
                data,
                "source",
                "g_source/source",
            ),

            source_other=val(
                data,
                "source_other",
                "g_source/autre_source",
            ),

            source_last_name=val(
                data,
                "source_last_name",
                "g_source/nom",
            ),

            source_first_name=val(
                data,
                "source_first_name",
                "g_source/prenom",
            ),

            source_contact=val(
                data,
                "source_contact",
                "g_source/contact",
            ),

            source_gender=val(
                data,
                "source_gender",
                "g_source/sexe",
            ),

            source_age=val(
                data,
                "source_age",
                "g_source/age",
            ),

            # =================================================
            # LOCALISATION
            # =================================================

            country=val(
                data,
                "country",
                "g_localisation/pays",
            ),

            region=region,
            cercle=cercle,
            commune=commune,

            village=val(
                data,
                "village",
                "g_localisation/village",
            ),

            latitude=val(
                data,
                "latitude",
                "g_localisation/latitude",
            ),

            longitude=val(
                data,
                "longitude",
                "g_localisation/longitude",
            ),

            location_details=val(
                data,
                "location_details",
                "g_localisation/details_emplacement",
            ),

            # =================================================
            # REPORTING
            # =================================================

            report_date=parse_date(
                str(
                    val(
                        data,
                        "q1_2",
                        "report_date",
                    )
                )
            ),

            reported_by=val(
                data,
                "reported_by",
                "reporter_name",
            ),

            org_name=val(
                data,
                "organization",
                "org_name",
            ),

            position=val(
                data,
                "position",
                "poste",
            ),

            team=val(
                data,
                "team",
                "equipe",
            ),

        )

        return JsonResponse({
            "success": True,
            "victim_id": victim.victim_id,
        })

    except Exception as e:

        return JsonResponse(
            {"error": str(e)},
            status=400
        )