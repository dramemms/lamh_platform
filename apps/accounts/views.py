from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from apps.geo.models import Region

from .forms import (
    AdminUserCreateForm,
    AdminUserEditForm,
    LAMHAccessGroupForm,
)

from .models import (
    generate_temp_password,
    LAMHAccessGroup,
)

User = get_user_model()


# =========================================================
# HELPERS
# =========================================================

def admin_required(view_func):
    return login_required(
        user_passes_test(
            lambda u: u.is_authenticated and u.role == "ADMIN",
            login_url="login"
        )(view_func)
    )


# =========================================================
# PASSWORD EXPIRED
# =========================================================

def temporary_password_expired(request):

    return render(
        request,
        "accounts/password_expired.html"
    )


# =========================================================
# USERS DASHBOARD
# =========================================================

@admin_required
def admin_users(request):

    users = User.objects.all().select_related(
        "region",
        "cercle",
        "commune"
    )

    q = request.GET.get("q")
    role = request.GET.get("role")
    status = request.GET.get("status")
    region = request.GET.get("region")

    if q:
        users = users.filter(
            Q(username__icontains=q)
            | Q(email__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
        )

    if role:
        users = users.filter(role=role)

    if region:
        users = users.filter(region_id=region)

    if status == "active":
        users = users.filter(is_active=True)

    elif status == "inactive":
        users = users.filter(is_active=False)

    elif status == "must_change":
        users = users.filter(must_change_password=True)

    elif status == "locked":
        users = users.filter(
            account_locked_until__gt=timezone.now()
        )

    context = {
        "users": users.order_by("username"),
        "regions": Region.objects.all().order_by("name"),
        "role_choices": User.ROLE_CHOICES,

        "total_active": User.objects.filter(
            is_active=True
        ).count(),

        "total_locked": User.objects.filter(
            account_locked_until__gt=timezone.now()
        ).count(),

        "total_must_change": User.objects.filter(
            must_change_password=True
        ).count(),

        "total_admins": User.objects.filter(
            role=User.ROLE_ADMIN
        ).count(),
    }

    return render(
        request,
        "accounts/admin_users.html",
        context
    )


# =========================================================
# CREATE USER
# =========================================================

@admin_required
def admin_user_create(request):

    if request.method == "POST":

        form = AdminUserCreateForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            temp_password = generate_temp_password()

            user.set_password(temp_password)

            user.must_change_password = True

            user.temporary_password_created_at = timezone.now()

            user.save()

            if user.email:

                send_mail(
                    subject="Votre compte LAMH Platform",
                    message=f"""
Bonjour {user.first_name or user.username},

Votre compte LAMH Platform a été créé.

Nom d'utilisateur : {user.username}

Mot de passe temporaire :
{temp_password}

⚠️ Ce mot de passe expire dans 24 heures.

Vous devrez changer ce mot de passe lors de votre première connexion.

Cordialement,
LAMH Platform
""",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )

            messages.success(
                request,
                f"Utilisateur {user.username} créé avec succès."
            )

            return redirect("admin_users")

    else:

        form = AdminUserCreateForm()

    return render(
        request,
        "accounts/user_create.html",
        {
            "form": form
        }
    )


# =========================================================
# EDIT USER
# =========================================================

@admin_required
def admin_user_edit(request, user_id):

    user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":

        form = AdminUserEditForm(
            request.POST,
            instance=user
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                f"Utilisateur {user.username} modifié avec succès."
            )

            return redirect("admin_users")

    else:

        form = AdminUserEditForm(instance=user)

    return render(
        request,
        "accounts/user_edit.html",
        {
            "form": form,
            "user_obj": user,
        }
    )


# =========================================================
# RESET PASSWORD
# =========================================================

@admin_required
def admin_user_reset_password(request, user_id):

    user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":

        temp_password = generate_temp_password()

        user.set_password(temp_password)

        user.must_change_password = True

        user.temporary_password_created_at = timezone.now()

        user.failed_login_attempts = 0

        user.account_locked_until = None

        user.save()

        if user.email:

            send_mail(
                subject="Réinitialisation compte LAMH",
                message=f"""
Bonjour {user.first_name or user.username},

Votre mot de passe LAMH a été réinitialisé.

Nom d'utilisateur : {user.username}

Mot de passe temporaire :
{temp_password}

⚠️ Ce mot de passe expire dans 24 heures.

Vous devrez le changer lors de votre prochaine connexion.

Cordialement,
LAMH Platform
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

        messages.success(
            request,
            f"Mot de passe réinitialisé pour {user.username}."
        )

        return redirect("admin_users")

    return render(
        request,
        "accounts/user_reset_password.html",
        {
            "user_obj": user
        }
    )


# =========================================================
# ACTIVATE USER
# =========================================================

@admin_required
def admin_user_activate(request, user_id):

    user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":

        user.is_active = True

        user.save()

        messages.success(
            request,
            f"Utilisateur {user.username} activé."
        )

        return redirect("admin_users")

    return render(
        request,
        "accounts/user_activate.html",
        {
            "user_obj": user
        }
    )


# =========================================================
# DEACTIVATE USER
# =========================================================

@admin_required
def admin_user_deactivate(request, user_id):

    user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":

        user.is_active = False

        user.save()

        messages.warning(
            request,
            f"Utilisateur {user.username} désactivé."
        )

        return redirect("admin_users")

    return render(
        request,
        "accounts/user_deactivate.html",
        {
            "user_obj": user
        }
    )


# =========================================================
# CHANGE PASSWORD
# =========================================================

@login_required
def change_password(request):

    if request.method == "POST":

        form = PasswordChangeForm(
            request.user,
            request.POST
        )

        if form.is_valid():

            user = form.save()

            user.must_change_password = False

            user.temporary_password_created_at = None

            user.last_password_change = timezone.now()

            user.save()
            
            if user.email:
                send_mail(
                    subject="LAMH Platform - Mot de passe modifié",
                    message=(
                       f"Bonjour {user.get_full_name() or user.username},\n\n"
                       "Votre mot de passe LAMH Platform vient d'être modifié avec succès.\n\n"
                       "Si vous n'êtes pas à l'origine de cette action, veuillez contacter immédiatement l'administrateur.\n\n"
                       "LAMH Platform - DCA Mali"
        ),
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=[user.email],
        fail_silently=True,
    )

            update_session_auth_hash(
                request,
                user
            )

            messages.success(
                request,
                "Mot de passe modifié avec succès."
            )

            return redirect("dashboard")

    else:

        form = PasswordChangeForm(request.user)

    return render(
        request,
        "accounts/change_password.html",
        {
            "form": form
        }
    )


# =========================================================
# GROUPS DASHBOARD
# =========================================================

@admin_required
def admin_groups(request):

    groups = LAMHAccessGroup.objects.select_related(
        "group"
    ).all()

    return render(
        request,
        "accounts/admin_groups.html",
        {
            "groups": groups
        }
    )


# =========================================================
# CREATE GROUP
# =========================================================

@admin_required
def admin_group_create(request):

    if request.method == "POST":

        form = LAMHAccessGroupForm(request.POST)

        if form.is_valid():

            group_name = form.cleaned_data["group_name"]

            group = Group.objects.create(
                name=group_name
            )

            access_group = form.save(commit=False)

            access_group.group = group

            access_group.save()

            form.save_m2m()

            for user in form.cleaned_data["users"]:
                user.groups.add(group)

            messages.success(
                request,
                "Groupe créé avec succès."
            )

            return redirect("admin_groups")

    else:

        form = LAMHAccessGroupForm()

    return render(
        request,
        "accounts/group_create.html",
        {
            "form": form
        }
    )

@admin_required
def admin_group_edit(request, group_id):

    access_group = get_object_or_404(
        LAMHAccessGroup,
        pk=group_id
    )

    if request.method == "POST":

        form = LAMHAccessGroupForm(
            request.POST,
            instance=access_group
        )

        if form.is_valid():

            group_name = form.cleaned_data["group_name"]

            access_group = form.save(commit=False)
            access_group.group.name = group_name
            access_group.group.save()
            access_group.save()

            form.save_m2m()

            # Réinitialiser les utilisateurs du groupe Django
            access_group.group.user_set.clear()

            for user in form.cleaned_data["users"]:
                user.groups.add(access_group.group)

            messages.success(
                request,
                "Groupe modifié avec succès."
            )

            return redirect("admin_groups")

    else:

        form = LAMHAccessGroupForm(
            instance=access_group,
            initial={
                "group_name": access_group.group.name,
                "users": access_group.group.user_set.all(),
            }
        )

    return render(
        request,
        "accounts/group_edit.html",
        {
            "form": form,
            "access_group": access_group,
        }
    )

@admin_required
def admin_group_delete(request, group_id):

    access_group = get_object_or_404(
        LAMHAccessGroup,
        pk=group_id
    )

    group = access_group.group

    if request.method == "POST":

        group_name = group.name

        access_group.delete()
        group.delete()

        messages.success(
            request,
            f"Groupe {group_name} supprimé avec succès."
        )

        return redirect("admin_groups")

    return render(
        request,
        "accounts/group_delete.html",
        {
            "access_group": access_group
        }
    )