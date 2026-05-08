from pathlib import Path

import pandas as pd
from django.core.management.base import BaseCommand, CommandError

from apps.geo.models import Region, Cercle, Commune


class Command(BaseCommand):
    help = "Importe le découpage administratif Mali depuis un fichier Excel DCA."

    def add_arguments(self, parser):
        parser.add_argument(
            "excel_path",
            type=str,
            help="Chemin complet du fichier Excel à importer",
        )

    def handle(self, *args, **options):
        excel_path = Path(options["excel_path"])

        if not excel_path.exists():
            raise CommandError(f"Fichier introuvable : {excel_path}")

        try:
            df = pd.read_excel(excel_path, sheet_name=0)
        except Exception as e:
            raise CommandError(f"Impossible de lire le fichier Excel : {e}")

        expected_columns = [
            "Region",
            "Code_Région",
            "Cercle",
            "Code_Cercle",
            "Commune",
            "Code_Commune",
        ]
        missing = [c for c in expected_columns if c not in df.columns]
        if missing:
            raise CommandError(f"Colonnes manquantes : {', '.join(missing)}")

        df = df[expected_columns].dropna()

        created_regions = 0
        created_cercles = 0
        created_communes = 0

        for _, row in df.iterrows():
            region_name = str(row["Region"]).strip()
            region_code = str(row["Code_Région"]).strip()

            cercle_name = str(row["Cercle"]).strip()
            cercle_code = str(row["Code_Cercle"]).strip()

            commune_name = str(row["Commune"]).strip()
            commune_code = str(row["Code_Commune"]).strip()

            region, region_created = Region.objects.get_or_create(
                code=region_code,
                defaults={"name": region_name},
            )
            if region_created:
                created_regions += 1
            elif region.name != region_name:
                region.name = region_name
                region.save(update_fields=["name"])

            cercle = Cercle.objects.filter(
                region=region,
                name=cercle_name,
            ).first()

            if not cercle:
                cercle = Cercle.objects.create(
                    name=cercle_name,
                    code=cercle_code,
                    region=region,
                )
                created_cercles += 1
            else:
                updates = []
                if cercle.code != cercle_code:
                    cercle.code = cercle_code
                    updates.append("code")
                if cercle.name != cercle_name:
                    cercle.name = cercle_name
                    updates.append("name")
                if cercle.region_id != region.id:
                    cercle.region = region
                    updates.append("region")
                if updates:
                    cercle.save(update_fields=updates)

            commune = Commune.objects.filter(
                cercle=cercle,
                name=commune_name,
            ).first()

            if not commune:
                commune = Commune.objects.create(
                    name=commune_name,
                    code=commune_code,
                    cercle=cercle,
                )
                created_communes += 1
            else:
                updates = []
                if commune.code != commune_code:
                    commune.code = commune_code
                    updates.append("code")
                if commune.name != commune_name:
                    commune.name = commune_name
                    updates.append("name")
                if commune.cercle_id != cercle.id:
                    commune.cercle = cercle
                    updates.append("cercle")
                if updates:
                    commune.save(update_fields=updates)

        self.stdout.write(self.style.SUCCESS("Import terminé avec succès."))
        self.stdout.write(f"Régions créées : {created_regions}")
        self.stdout.write(f"Cercles créés : {created_cercles}")
        self.stdout.write(f"Communes créées : {created_communes}")
        self.stdout.write(f"Total régions : {Region.objects.count()}")
        self.stdout.write(f"Total cercles : {Cercle.objects.count()}")
        self.stdout.write(f"Total communes : {Commune.objects.count()}")