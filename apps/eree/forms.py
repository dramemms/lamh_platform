from django import forms

from .models import EREESession


class BaseEREESessionForm(forms.ModelForm):
    """
    Base commune pour ajout et modification EREE.
    """

    class Meta:
        model = EREESession
        exclude = [
            "status",
            "submitted_at",
            "tech_validated_at",
            "program_validated_at",
            "approved_at",
            "tech_validated_by",
            "program_validated_by",
            "approved_by",
            "created_by",
            "created_at",
            "updated_at",
            "total_participants",
            "total_pdi",
            "total_host_community",
        ]
        widgets = {
            "reference": forms.TextInput(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "reported_by": forms.TextInput(attrs={"class": "form-control"}),
            "week_number": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "week_from": forms.DateInput(
                attrs={"type": "date", "class": "form-control"},
                format="%Y-%m-%d",
            ),
            "week_to": forms.DateInput(
                attrs={"type": "date", "class": "form-control"},
                format="%Y-%m-%d",
            ),
            "month_name": forms.TextInput(attrs={"class": "form-control"}),
            "year": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "organisation": forms.TextInput(attrs={"class": "form-control"}),
            "narrative_description": forms.Textarea(
                attrs={"rows": 4, "class": "form-control"}
            ),
            "session_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"},
                format="%Y-%m-%d",
            ),
            "location_gps": forms.TextInput(attrs={"class": "form-control"}),
            "latitude": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.000001"}
            ),
            "longitude": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.000001"}
            ),
            "team": forms.TextInput(attrs={"class": "form-control"}),
            "session_status": forms.TextInput(attrs={"class": "form-control"}),
            "region_code": forms.TextInput(attrs={"class": "form-control"}),
            "cercle_code": forms.TextInput(attrs={"class": "form-control"}),
            "commune_code": forms.TextInput(attrs={"class": "form-control"}),
            "region": forms.Select(attrs={"class": "form-select"}),
            "cercle": forms.Select(attrs={"class": "form-select"}),
            "commune": forms.Select(attrs={"class": "form-select"}),
            "village": forms.TextInput(attrs={"class": "form-control"}),
            "methodology": forms.TextInput(attrs={"class": "form-control"}),
            "sensitization_type": forms.TextInput(attrs={"class": "form-control"}),
            "civilian_subcategory": forms.TextInput(attrs={"class": "form-control"}),
            "humanitarian_org_type": forms.TextInput(attrs={"class": "form-control"}),
            "other_precision": forms.TextInput(attrs={"class": "form-control"}),
            "humanitarian_male": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "humanitarian_female": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "funding_type": forms.TextInput(attrs={"class": "form-control"}),

            "pdi_boys_0_5": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_boys_0_5_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_girls_0_5": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_girls_0_5_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_boys_6_14": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_boys_6_14_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_girls_6_14": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_girls_6_14_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_boys_15_17": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_boys_15_17_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_girls_15_17": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_girls_15_17_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_men_18_24": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_men_18_24_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_women_18_24": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_women_18_24_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_men_25_49": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_men_25_49_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_women_25_49": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_women_25_49_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_men_50_59": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_men_50_59_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_women_50_59": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_women_50_59_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_men_60_plus": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_men_60_plus_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_women_60_plus": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "pdi_women_60_plus_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),

            "ch_boys_0_5": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_boys_0_5_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_girls_0_5": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_girls_0_5_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_boys_6_14": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_boys_6_14_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_girls_6_14": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_girls_6_14_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_boys_15_17": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_boys_15_17_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_girls_15_17": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_girls_15_17_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_men_18_24": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_men_18_24_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_women_18_24": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_women_18_24_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_men_25_49": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_men_25_49_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_women_25_49": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_women_25_49_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_men_50_59": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_men_50_59_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_women_50_59": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_women_50_59_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_men_60_plus": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_men_60_plus_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_women_60_plus": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "ch_women_60_plus_dis": forms.NumberInput(attrs={"class": "form-control", "min": 0}),

            "leaflets_adults": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "leaflets_children": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "quality_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"},
                format="%Y-%m-%d",
            ),
            "quality_team": forms.TextInput(attrs={"class": "form-control"}),
            "quality_method": forms.TextInput(attrs={"class": "form-control"}),
            "quality_observations": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
            "difficulties_solutions": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),

            "validation_comment": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
            "rejection_reason": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
            "correction_comment": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            existing = field.widget.attrs.get("class", "")

            if isinstance(field.widget, forms.Select):
                if "form-select" not in existing:
                    field.widget.attrs["class"] = (existing + " form-select").strip()
            elif isinstance(field.widget, forms.CheckboxInput):
                if "form-check-input" not in existing:
                    field.widget.attrs["class"] = (existing + " form-check-input").strip()
            else:
                if "form-control" not in existing:
                    field.widget.attrs["class"] = (existing + " form-control").strip()

        labels = {
            "reference": "Référence",
            "title": "Titre",
            "reported_by": "Rapporté par",
            "week_number": "Semaine",
            "week_from": "Du",
            "week_to": "Au",
            "month_name": "Mois",
            "year": "Année",
            "organisation": "Organisation",
            "narrative_description": "Description narrative",
            "session_date": "Date session",
            "location_gps": "Coordonnées GPS",
            "team": "Équipe",
            "session_status": "Statut session",
            "region_code": "Code région Kobo",
            "cercle_code": "Code cercle Kobo",
            "commune_code": "Code commune Kobo",
            "region": "Région",
            "cercle": "Cercle",
            "commune": "Commune",
            "village": "Village",
            "methodology": "Méthodologie",
            "sensitization_type": "Type de sensibilisation",
            "civilian_subcategory": "Sous-catégorie civils",
            "humanitarian_org_type": "Type organisation humanitaire",
            "other_precision": "Précision autres",
            "humanitarian_male": "Hommes humanitaires",
            "humanitarian_female": "Femmes humanitaires",
            "funding_type": "Source de financement",
            "quality_date": "Date qualité",
            "quality_team": "Équipe qualité",
            "quality_method": "Méthode qualité",
            "quality_observations": "Observations qualité",
            "difficulties_solutions": "Difficultés / solutions",
            "leaflets_adults": "Dépliants adultes",
            "leaflets_children": "Dépliants enfants",
            "validation_comment": "Commentaire validation",
            "rejection_reason": "Motif rejet",
            "correction_comment": "Commentaire correction",
        }

        for field_name, label in labels.items():
            if field_name in self.fields:
                self.fields[field_name].label = label

    def clean(self):
        cleaned_data = super().clean()

        numeric_fields = [
            "humanitarian_male", "humanitarian_female",
            "pdi_boys_0_5", "pdi_boys_0_5_dis", "pdi_girls_0_5", "pdi_girls_0_5_dis",
            "pdi_boys_6_14", "pdi_boys_6_14_dis", "pdi_girls_6_14", "pdi_girls_6_14_dis",
            "pdi_boys_15_17", "pdi_boys_15_17_dis", "pdi_girls_15_17", "pdi_girls_15_17_dis",
            "pdi_men_18_24", "pdi_men_18_24_dis", "pdi_women_18_24", "pdi_women_18_24_dis",
            "pdi_men_25_49", "pdi_men_25_49_dis", "pdi_women_25_49", "pdi_women_25_49_dis",
            "pdi_men_50_59", "pdi_men_50_59_dis", "pdi_women_50_59", "pdi_women_50_59_dis",
            "pdi_men_60_plus", "pdi_men_60_plus_dis", "pdi_women_60_plus", "pdi_women_60_plus_dis",
            "ch_boys_0_5", "ch_boys_0_5_dis", "ch_girls_0_5", "ch_girls_0_5_dis",
            "ch_boys_6_14", "ch_boys_6_14_dis", "ch_girls_6_14", "ch_girls_6_14_dis",
            "ch_boys_15_17", "ch_boys_15_17_dis", "ch_girls_15_17", "ch_girls_15_17_dis",
            "ch_men_18_24", "ch_men_18_24_dis", "ch_women_18_24", "ch_women_18_24_dis",
            "ch_men_25_49", "ch_men_25_49_dis", "ch_women_25_49", "ch_women_25_49_dis",
            "ch_men_50_59", "ch_men_50_59_dis", "ch_women_50_59", "ch_women_50_59_dis",
            "ch_men_60_plus", "ch_men_60_plus_dis", "ch_women_60_plus", "ch_women_60_plus_dis",
            "leaflets_adults", "leaflets_children",
        ]

        for field_name in numeric_fields:
            value = cleaned_data.get(field_name)
            if value is not None and value < 0:
                self.add_error(field_name, "Cette valeur ne peut pas être négative.")

        total = 0
        for field_name in numeric_fields:
            total += cleaned_data.get(field_name) or 0

        if total == 0:
            raise forms.ValidationError(
                "Veuillez renseigner au moins un participant ou un support distribué."
            )

        return cleaned_data


class EREESessionForm(BaseEREESessionForm):
    pass


class EREESessionEditForm(BaseEREESessionForm):
    comment = forms.CharField(
        required=False,
        label="Commentaire de modification",
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
    )

class EREEEditForm(forms.ModelForm):
    class Meta:
        model = EREESession
        fields = "__all__"