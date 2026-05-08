from django.db import models


class Region(models.Model):
    name = models.CharField("Nom", max_length=150)
    code = models.CharField("Code", max_length=20, unique=True)

    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Région"
        verbose_name_plural = "Régions"

    def __str__(self):
        return self.name


class Cercle(models.Model):
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name="cercles",
        verbose_name="Région",
    )
    name = models.CharField("Nom", max_length=150)
    code = models.CharField("Code", max_length=20, unique=True)

    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Cercle"
        verbose_name_plural = "Cercles"
        unique_together = [("region", "name")]

    def __str__(self):
        return f"{self.name} ({self.region.name})"


class Commune(models.Model):
    cercle = models.ForeignKey(
        Cercle,
        on_delete=models.CASCADE,
        related_name="communes",
        verbose_name="Cercle",
    )
    name = models.CharField("Nom", max_length=200)
    code = models.CharField("Code", max_length=20, unique=True)

    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Commune"
        verbose_name_plural = "Communes"
        unique_together = [("cercle", "name")]

    def __str__(self):
        return f"{self.name} ({self.cercle.name})"