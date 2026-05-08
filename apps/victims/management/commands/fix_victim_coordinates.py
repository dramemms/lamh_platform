from django.core.management.base import BaseCommand
from apps.victims.models import Victim


class Command(BaseCommand):
    help = "Remplit latitude/longitude des victimes depuis commune, cercle ou région"

    def handle(self, *args, **options):
        updated = 0
        skipped = 0

        victims = Victim.objects.filter(status="APPROVED").filter(
            latitude__isnull=True,
            longitude__isnull=True,
        )

        for v in victims:
            lat = None
            lon = None

            if v.commune and getattr(v.commune, "latitude", None) and getattr(v.commune, "longitude", None):
                lat = v.commune.latitude
                lon = v.commune.longitude

            elif v.cercle and getattr(v.cercle, "latitude", None) and getattr(v.cercle, "longitude", None):
                lat = v.cercle.latitude
                lon = v.cercle.longitude

            elif v.region and getattr(v.region, "latitude", None) and getattr(v.region, "longitude", None):
                lat = v.region.latitude
                lon = v.region.longitude

            if lat and lon:
                v.latitude = lat
                v.longitude = lon
                v.save(update_fields=["latitude", "longitude"])
                updated += 1
            else:
                skipped += 1

        self.stdout.write(self.style.SUCCESS(f"Victimes mises à jour : {updated}"))
        self.stdout.write(self.style.WARNING(f"Victimes sans coordonnées trouvées : {skipped}"))