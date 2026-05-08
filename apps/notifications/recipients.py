from django.contrib.auth import get_user_model

User = get_user_model()


def get_emails_by_roles(roles):
    return list(
        User.objects.filter(role__in=roles, is_active=True)
        .exclude(email__isnull=True)
        .exclude(email="")
        .values_list("email", flat=True)
    )


# 🔹 TECH + SUPERVISOR + ADMIN
def get_tech_emails():
    return get_emails_by_roles([
        "TECH_VALIDATOR",
        "SUPERVISOR",
        "ADMIN",
    ])


# 🔹 PROJECT MANAGER + ADMIN
def get_project_emails():
    return get_emails_by_roles([
        "PROJECT_MANAGER",
        "ADMIN",
    ])


# 🔹 ALIAS (IMPORTANT pour compatibilité ancienne)
def get_program_emails():
    return get_project_emails()


# 🔹 ADMIN
def get_admin_emails():
    return get_emails_by_roles([
        "ADMIN",
    ])