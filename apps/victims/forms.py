from django import forms

from .models import Victim


class VictimForm(forms.ModelForm):
    report_date = forms.DateField(
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date", "class": "form-control"},
        ),
        label="Date du rapport",
    )

    birth_date = forms.DateField(
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date", "class": "form-control"},
        ),
        label="Date de naissance",
    )

    class Meta:
        model = Victim
        exclude = [
            "accident",
            "status",
            "submitted_at",
            "tech_validated_at",
            "program_validated_at",
            "approved_at",
            "tech_validated_by",
            "program_validated_by",
            "approved_by",
            "rejection_reason",
            "correction_comment",
            "kobo_submission_id",
            "kobo_uuid",
            "raw_payload",
            "created_at",
            "updated_at",
        ]
        widgets = {
            "no_consent_reason": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
            "injury_description": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
            "address": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
            "location_details": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        checkbox_fields = {
            "consentement",
            "birth_date_known",
            "main_breadwinner",
            "urgent_medical_evac",
            "knew_danger_zone",
            "saw_object",
            "received_er_before",
            "received_er_after",
            "pre_existing_disability",
            "medical_care",
            "non_medical_care",
        }

        for field_name, field in self.fields.items():
            if field_name in checkbox_fields:
                field.widget.attrs["class"] = "form-check-input"
            else:
                existing = field.widget.attrs.get("class", "")
                if (
                    "form-control" not in existing
                    and not isinstance(field.widget, forms.CheckboxInput)
                ):
                    field.widget.attrs["class"] = (existing + " form-control").strip()


class VictimEditForm(forms.ModelForm):
    report_date = forms.DateField(
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date", "class": "form-control"},
        ),
        label="Date du rapport",
    )

    birth_date = forms.DateField(
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date", "class": "form-control"},
        ),
        label="Date de naissance",
    )

    comment = forms.CharField(
        required=False,
        label="Commentaire de modification",
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
    )

    class Meta:
        model = Victim
        exclude = [
            "accident",
            "status",
            "submitted_at",
            "tech_validated_at",
            "program_validated_at",
            "approved_at",
            "tech_validated_by",
            "program_validated_by",
            "approved_by",
            "rejection_reason",
            "correction_comment",
            "kobo_submission_id",
            "kobo_uuid",
            "raw_payload",
            "created_at",
            "updated_at",
        ]
        widgets = {
            "no_consent_reason": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
            "injury_description": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
            "address": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
            "location_details": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        checkbox_fields = {
            "consentement",
            "birth_date_known",
            "main_breadwinner",
            "urgent_medical_evac",
            "knew_danger_zone",
            "saw_object",
            "received_er_before",
            "received_er_after",
            "pre_existing_disability",
            "medical_care",
            "non_medical_care",
        }

        for field_name, field in self.fields.items():
            if field_name == "comment":
                continue

            if field_name in checkbox_fields:
                field.widget.attrs["class"] = "form-check-input"
            else:
                existing = field.widget.attrs.get("class", "")
                if (
                    "form-control" not in existing
                    and not isinstance(field.widget, forms.CheckboxInput)
                ):
                    field.widget.attrs["class"] = (existing + " form-control").strip()

class VictimEditForm(forms.ModelForm):
    class Meta:
        model = Victim
        fields = "__all__"