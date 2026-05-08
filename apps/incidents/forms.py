from django import forms
from .models import Accident


class AccidentEditForm(forms.ModelForm):
    comment = forms.CharField(
        required=False,
        label="Commentaire de modification",
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
    )

    class Meta:
        model = Accident

        fields = [
            # 1. Identification / reporting
            "reference",
            "accident_associe_id",
            "report_date",
            "org_name",
            "reported_by",
            "position",
            "team",
            "funding_source",

            # 2. Détails accident
            "accident_date",
            "accident_time",
            "category",
            "number_victims",
            "other_damage",
            "activity_at_time",
            "description",
            "device_type",
            "device_status",
            "device_marked",

            # 3. Localisation
            "country",
            "region",
            "cercle",
            "commune",
            "locality",
            "secure_access",
            "src_coordinates",
            "latitude",
            "longitude",
            "location_gps",

            # 4. Source d'information
            "source_last_name",
            "source_first_name",
            "source_contact",
            "source_gender",
            "source_age",
            "source_type",

            # Soumissionnaire / système
            "submitter_email",
            "submitter_first_name",
            "submitter_last_name",
            "submitter_phone",
            "submitter_organization",
            "submitter_role",
            "submitter_username",
            "source",
            "kobo_submission_id",
            "kobo_uuid",
            "kobo_asset_uid",
        ]

        widgets = {
            # Identification
            "reference": forms.TextInput(attrs={"class": "form-control"}),
            "accident_associe_id": forms.TextInput(attrs={"class": "form-control"}),
            "report_date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date", "class": "form-control"},
            ),
            "org_name": forms.TextInput(attrs={"class": "form-control"}),
            "reported_by": forms.TextInput(attrs={"class": "form-control"}),
            "position": forms.TextInput(attrs={"class": "form-control"}),
            "team": forms.TextInput(attrs={"class": "form-control"}),
            "funding_source": forms.TextInput(attrs={"class": "form-control"}),

            # Détails accident
            "accident_date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date", "class": "form-control"},
            ),
            "accident_time": forms.TimeInput(
                format="%H:%M",
                attrs={"type": "time", "class": "form-control"},
            ),
            "category": forms.Select(attrs={"class": "form-select"}),
            "number_victims": forms.NumberInput(attrs={"class": "form-control"}),
            "other_damage": forms.TextInput(attrs={"class": "form-control"}),
            "activity_at_time": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "device_type": forms.TextInput(attrs={"class": "form-control"}),
            "device_status": forms.TextInput(attrs={"class": "form-control"}),
            "device_marked": forms.TextInput(attrs={"class": "form-control"}),

            # Localisation
            "country": forms.TextInput(attrs={"class": "form-control"}),
            "region": forms.Select(attrs={"class": "form-select"}),
            "cercle": forms.Select(attrs={"class": "form-select"}),
            "commune": forms.Select(attrs={"class": "form-select"}),
            "locality": forms.TextInput(attrs={"class": "form-control"}),
            "secure_access": forms.TextInput(attrs={"class": "form-control"}),
            "src_coordinates": forms.TextInput(attrs={"class": "form-control"}),
            "latitude": forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
            "longitude": forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
            "location_gps": forms.TextInput(attrs={"class": "form-control"}),

            # Source d'information
            "source_last_name": forms.TextInput(attrs={"class": "form-control"}),
            "source_first_name": forms.TextInput(attrs={"class": "form-control"}),
            "source_contact": forms.TextInput(attrs={"class": "form-control"}),
            "source_gender": forms.TextInput(attrs={"class": "form-control"}),
            "source_age": forms.NumberInput(attrs={"class": "form-control"}),
            "source_type": forms.TextInput(attrs={"class": "form-control"}),

            # Soumissionnaire / système
            "submitter_email": forms.EmailInput(attrs={"class": "form-control"}),
            "submitter_first_name": forms.TextInput(attrs={"class": "form-control"}),
            "submitter_last_name": forms.TextInput(attrs={"class": "form-control"}),
            "submitter_phone": forms.TextInput(attrs={"class": "form-control"}),
            "submitter_organization": forms.TextInput(attrs={"class": "form-control"}),
            "submitter_role": forms.TextInput(attrs={"class": "form-control"}),
            "submitter_username": forms.TextInput(attrs={"class": "form-control"}),
            "source": forms.Select(attrs={"class": "form-select"}),
            "kobo_submission_id": forms.TextInput(attrs={"class": "form-control"}),
            "kobo_uuid": forms.TextInput(attrs={"class": "form-control"}),
            "kobo_asset_uid": forms.TextInput(attrs={"class": "form-control"}),
        }

        labels = {
            "reference": "ID de l'accident",
            "accident_associe_id": "ID de l'incident associé",
            "report_date": "Date du rapport",
            "org_name": "Nom de l'organisation",
            "reported_by": "Rapporté par",
            "position": "Position",
            "team": "Équipe",
            "funding_source": "Source de financement",
            "accident_date": "Date de l'accident",
            "accident_time": "Heure de l'accident",
            "category": "Type d'accident",
            "number_victims": "Nombre de victimes",
            "other_damage": "Autres dommages",
            "activity_at_time": "Activité au moment de l'accident",
            "description": "Description de l'accident",
            "device_type": "Type d'engin",
            "device_status": "Status de l'engin",
            "device_marked": "L'engin est-il marqué ?",
            "country": "Pays",
            "region": "Région",
            "cercle": "Cercle",
            "commune": "Commune",
            "locality": "Village / Quartier",
            "secure_access": "Accès sécurisé au lieu d'accident ?",
            "src_coordinates": "Source de coordonnées",
            "latitude": "Latitude",
            "longitude": "Longitude",
            "location_gps": "Détails de la localisation",
            "source_last_name": "Nom",
            "source_first_name": "Prénom",
            "source_contact": "Contact",
            "source_gender": "Sexe",
            "source_age": "Âge",
            "source_type": "Type de source",
            "submitter_email": "Email du soumissionnaire",
            "submitter_first_name": "Prénom du soumissionnaire",
            "submitter_last_name": "Nom du soumissionnaire",
            "submitter_phone": "Téléphone du soumissionnaire",
            "submitter_organization": "Organisation du soumissionnaire",
            "submitter_role": "Fonction du soumissionnaire",
            "submitter_username": "Username Kobo / identifiant",
            "source": "Source",
            "kobo_submission_id": "Kobo Submission ID",
            "kobo_uuid": "Kobo UUID",
            "kobo_asset_uid": "Kobo Asset UID",
            "comment": "Commentaire de modification",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "accident_date" in self.fields:
            self.fields["accident_date"].input_formats = ["%Y-%m-%d"]

        if "report_date" in self.fields:
            self.fields["report_date"].input_formats = ["%Y-%m-%d"]

        if "accident_time" in self.fields:
            self.fields["accident_time"].input_formats = ["%H:%M", "%H:%M:%S"]

        readonly_fields = [
            "reference",
            "kobo_submission_id",
            "kobo_uuid",
            "kobo_asset_uid",
        ]

        for field_name in readonly_fields:
            if field_name in self.fields:
                self.fields[field_name].disabled = True
                existing_class = self.fields[field_name].widget.attrs.get("class", "")
                self.fields[field_name].widget.attrs["class"] = f"{existing_class} bg-light".strip()

        # Champs métier absents du formulaire mais existants dans le modèle :
        # on ne les affiche pas et on ne les laisse pas bloquer la validation.
        # En édition, leurs anciennes valeurs sont conservées sur l'instance.
        hidden_optional_if_present = [
            "title",
            "impact",
            "number_killed",
            "number_injured",
            "number_affected",
        ]
        for field_name in hidden_optional_if_present:
            if field_name in self.fields:
                self.fields[field_name].required = False