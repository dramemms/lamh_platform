import unicodedata
import pandas as pd

from apps.incidents.models import Accident
from apps.geo.models import Region, Cercle, Commune


def normalize(val):
    if pd.isna(val) or val is None:
        return ""

    val = str(val).replace("\xa0", "").strip().lower()

    # Supprimer accents : Ségou -> segou, Djenné -> djenne
    val = unicodedata.normalize("NFKD", val)
    val = "".join(c for c in val if not unicodedata.combining(c))

    # Nettoyer les suffixes Kobo
    val = val.replace("_cercle", "")
    val = val.replace("_commune", "")
    val = val.replace("_region", "")

    # Nettoyer séparateurs
    val = val.replace("_", " ")
    val = val.replace("-", " ")

    # Réduire espaces multiples
    val = " ".join(val.split())

    return val


def clean_text(val):
    if pd.isna(val) or val is None:
        return None
    return str(val).replace("\xa0", "").strip()


def parse_date(val):
    if pd.isna(val) or val is None or str(val).strip() == "":
        return None

    if hasattr(val, "date"):
        return val.date()

    val = str(val).replace("\xa0", "").strip()

    date = pd.to_datetime(val, dayfirst=True, errors="coerce")

    if pd.isna(date):
        return None

    return date.date()


def parse_time(val):
    if pd.isna(val) or val is None or str(val).strip() == "":
        return None

    if hasattr(val, "time"):
        return val.time()

    val = str(val).replace("\xa0", "").strip()

    time_value = pd.to_datetime(val, errors="coerce")

    if pd.isna(time_value):
        return None

    return time_value.time()


def parse_int(val):
    if pd.isna(val) or val is None or str(val).strip() == "":
        return 0

    try:
        return int(float(str(val).replace("\xa0", "").strip()))
    except Exception:
        return 0


def parse_float(val):
    if pd.isna(val) or val is None or str(val).strip() == "":
        return None

    try:
        return float(str(val).replace(",", ".").replace("\xa0", "").strip())
    except Exception:
        return None


def get_geo(model, name):
    name_clean = normalize(name)

    if not name_clean:
        return None

    # Match exact après normalisation
    for obj in model.objects.all():
        if normalize(obj.name) == name_clean:
            return obj

    # Match partiel : Excel inclus dans DB
    for obj in model.objects.all():
        if name_clean in normalize(obj.name):
            return obj

    # Match partiel inverse : DB inclus dans Excel
    for obj in model.objects.all():
        if normalize(obj.name) in name_clean:
            return obj

    print(f"⚠️ Non trouvé dans {model.__name__} : {name}")
    return None


def generate_reference(kobo_id):
    """
    Format demandé : ACC-XXX-XX
    Exemple :
    1   -> ACC-001-25
    25  -> ACC-025-25
    220 -> ACC-220-25
    """
    number = str(kobo_id).replace("\xa0", "").strip()
    return f"ACC-{number.zfill(3)}-25"


def import_accidents(file_path):
    df = pd.read_excel(file_path)

    success = 0
    errors = 0

    for _, row in df.iterrows():
        kobo_id = clean_text(row.get("1.1. ID de l'accident"))

        try:
            if not kobo_id:
                print("❌ ID accident manquant")
                errors += 1
                continue

            region = get_geo(Region, row.get("3.2. Région"))
            cercle = get_geo(Cercle, row.get("3.3. Cercle"))
            commune = get_geo(Commune, row.get("3.4. Commune"))

            if not region or not cercle or not commune:
                print(f"❌ GEO MANQUANT pour {kobo_id}")
                errors += 1
                continue

            reference = generate_reference(kobo_id)

            Accident.objects.update_or_create(
                reference=reference,
                defaults={
                    "status": Accident.STATUS_SUBMITTED,

                    "title": f"Accident {reference}",
                    "description": clean_text(row.get("2.7. Description de l' accident")),

                    "accident_associe_id": clean_text(row.get("ID de l'incident associé")),

                    "submitted_at_kobo": parse_date(row.get("1.2.  Date du rapport")),
                    "report_date": parse_date(row.get("1.2.  Date du rapport")),

                    "org_name": clean_text(row.get("1.3.Nom de l'organisation")),
                    "reported_by": clean_text(row.get("1.4. Rapporté par")),
                    "position": clean_text(row.get("1.5. Position")),
                    "team": clean_text(row.get("1.6. Equipe")),
                    "funding_source": clean_text(row.get("1.7. Source de financement ")),

                    "accident_date": parse_date(row.get("2.1. Date de l'accident")),
                    "accident_time": parse_time(row.get("2.2. Heure de l'accident")),

                    "category": clean_text(row.get("2.8. Type d'accident")),
                    "number_victims": parse_int(row.get("2.4. Nombre de victimes")),
                    "other_damage": clean_text(row.get("2.5. Autres dommages")),
                    "activity_at_time": clean_text(row.get("2.6. Activité au moment de l'accident")),

                    "device_type": clean_text(row.get("2.9. Type d'engin")),
                    "device_status": clean_text(row.get("2.10. Status de l'engin")),
                    "device_marked": clean_text(row.get("2.11. L'engin est-il marqué?")),

                    "country": clean_text(row.get("3.1. Pays")),
                    "region": region,
                    "cercle": cercle,
                    "commune": commune,
                    "locality": clean_text(row.get("3.5. Village / Quartier")),

                    "latitude": parse_float(row.get("Latitude")),
                    "longitude": parse_float(row.get("Longitude")),
                    "secure_access": clean_text(row.get("3.7. Accès sécurisé au lieu d'accident ?")),
                    "src_coordinates": clean_text(row.get("3.8. Source de coordonnées")),
                    "location_gps": clean_text(row.get("3.11. Détails de la localisation")),

                    "source_name": clean_text(row.get("4.1. Nom")),
                    "source_first_name": clean_text(row.get("4.2. Prenom")),
                    "source_contact": clean_text(row.get("4.3. Contact")),
                    "source_gender": clean_text(row.get("4.4. Sexe")),
                    "source_age": parse_int(row.get("4.5. Age")),
                    "source_type": clean_text(row.get("4.6. Type de source")),
                },
            )

            print(f"✔️ Importé : {reference}")
            success += 1

        except Exception as e:
            print(f"❌ Erreur {kobo_id} : {e}")
            errors += 1

    print(f"\n✅ Succès: {success} | ❌ Erreurs: {errors}")