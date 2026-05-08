from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import LAMHAccessGroup

User = get_user_model()


class AdminUserCreateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "region",
            "cercle",
            "commune",
            "is_active",
        ]


class AdminUserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "role",
            "region",
            "cercle",
            "commune",
            "is_active",
            "is_staff",
        ]

class GroupForm(forms.ModelForm):

    class Meta:
        model = Group

        fields = [
            "name"
        ]

        labels = {
            "name": "Nom du groupe",
        }

class LAMHAccessGroupForm(forms.ModelForm):
    group_name = forms.CharField(
        label="Nom du groupe",
        max_length=150
    )

    users = forms.ModelMultipleChoiceField(
        label="Utilisateurs du groupe",
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple
    )

    class Meta:
        model = LAMHAccessGroup
        fields = [
            "group_name",
            "users",
            "regions",
            "cercles",
            "communes",
            "can_view_all_regions",
            "can_access_accidents",
            "can_access_victims",
            "can_access_eree",
            "can_access_reporting",
        ]