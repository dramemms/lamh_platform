import unicodedata
from datetime import datetime, timedelta

import pandas as pd

from apps.eree.models import EREESession
from apps.geo.models import Region, Cercle, Commune


def normalize(val):
    if pd.isna(val) or val is None:
        return ""

    val = str(val).replace("\xa0", "").strip().lower()

    val = unicodedata.normalize("NFKD", val)
    val = "".join(c for c in val if not unicodedata.combining(c))

    val = val.replace("district de ", "")
    val = val.replace("region de ", "")
    val = val.replace("région de ", "")

    val = val.replace("_cercle", "")
    val = val.replace("_commune", "")
    val = val.replace("_region", "")
    val = val.replace("_", " ")
    val = val.replace("-", " ")

    val = " ".join(val.split())

    return val


def clean(val):
    if pd.isna(val) or val is None:
        return None

    val = str(val).replace("\xa0", "").strip()

    if val in ["", "-", "   -", "     -"]:
        return None

    return val


def get_value(row, *names):
    for name in names:
        value = row.get(name)
        if clean(value):
            return value
    return None


def parse_date(val):
    if pd.isna(val) or val is None or str(val).strip() == "":
        return None

    if isinstance(val, datetime):
        return val.date()

    try:
        if isinstance(val, (int, float)) and val > 20000:
            return (datetime(1899, 12, 30) + timedelta(days=int(val))).date()
    except Exception:
        pass

    val = str(val).replace("\xa0", "").strip()
    d = pd.to_datetime(val, dayfirst=True, errors="coerce")

    if pd.isna(d):
        return None

    return d.date()


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

    for obj in model.objects.all():
        db_name = normalize(obj.name)

        # 🔥 match exact
        if db_name == name_clean:
            return obj

        # 🔥 match partiel
        if name_clean in db_name:
            return obj

        # 🔥 inverse
        if db_name in name_clean:
            return obj

    # 🔥 correction spéciale Mali
    corrections = {
        "bamako": "district de bamako",
        "gao cercle": "gao",
        "tombouctou cercle": "tombouctou",
        "mopti cercle": "mopti",
    }

    if name_clean in corrections:
        return model.objects.filter(name__icontains=corrections[name_clean]).first()

    print(f"⚠️ Non trouvé dans {model.__name__} : {name}")
    return None


def get_region(row):
    return get_geo(
        Region,
        get_value(
            row,
            "Région",
            "Region",
            "region",
            "3.2. Région",
            "g_location/region",
            "Country Level 1",
        ),
    )


def get_cercle(row):
    return get_geo(
        Cercle,
        get_value(
            row,
            "Cercle",
            "cercle",
            "3.3. Cercle",
            "g_location/cercle",
        ),
    )


def get_commune(row):
    return get_geo(
        Commune,
        get_value(
            row,
            "Commune",
            "commune",
            "3.4. Commune",
            "g_location/commune",
        ),
    )


def fallback_geo(region, cercle, commune):
    if not region:
        region = Region.objects.first()

    if not cercle and region:
        cercle = Cercle.objects.filter(region=region).first()

    if not commune and cercle:
        commune = Commune.objects.filter(cercle=cercle).first()

    return region, cercle, commune


def field_exists(field_name):
    return any(f.name == field_name for f in EREESession._meta.fields)


def safe_defaults(data):
    return {
        key: value
        for key, value in data.items()
        if field_exists(key)
    }


def generate_eree_reference(index):
    return f"EREE-{str(index).zfill(3)}-25"


def import_eree(file_path):
    df = pd.read_excel(file_path)

    success = 0
    errors = 0

    for index, row in df.iterrows():
        reference = generate_eree_reference(index + 1)

        try:
            region = get_region(row)
            cercle = get_cercle(row)
            commune = get_commune(row)

            if not region or not cercle or not commune:
                print(f"⚠️ GEO non trouvé pour {reference} — fallback appliqué")
                region, cercle, commune = fallback_geo(region, cercle, commune)

            data = {
    "reference": reference,
    "session_status": "SUBMITTED",

    "title": clean(get_value(row,
        "Nom activité",
        "1.1 Nom activité",
        "activity_name"
    )) or f"Session EREE {reference}",

    "session_date": parse_date(get_value(row,
        "Date",
        "1.2 Date",
        "session_date"
    )),

    "region": get_geo(Region, get_value(row,
        "g_location/region"
    )),

    "cercle": get_geo(Cercle, get_value(row,
        "g_location/cercle"
    )),

    "commune": get_geo(Commune, get_value(row,
        "g_location/commune"
    )),

    "organisation": clean(get_value(row,
        "Organisation",
        "organisation"
    )),

    "reported_by": clean(get_value(row,
        "Rapporté par",
        "reported_by"
    )),

    "total_participants": parse_int(get_value(row,
        "participants_total",
        "Nombre participants",
        "total_participants"
    )),

    "narrative_description": clean(get_value(row,
        "description",
        "Description"
    )),
}

            EREESession.objects.update_or_create(
                reference=reference,
                defaults=safe_defaults(data),
            )

            print(f"✔️ Importé : {reference}")
            success += 1

        except Exception as e:
            print(f"❌ Erreur {reference} : {e}")
            errors += 1

    print(f"\n✅ Succès: {success} | ❌ Erreurs: {errors}")