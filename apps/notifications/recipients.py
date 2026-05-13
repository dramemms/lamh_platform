from django.contrib.auth import get_user_model

User = get_user_model()


def get_emails_by_roles(roles):
    return list(
        User.objects.filter(
            role__in=roles,
            is_active=True,
        )
        .exclude(email__isnull=True)
        .exclude(email="")
        .values_list("email", flat=True)
    )


# =========================================
# VERIFICATEURS TECHNIQUES
# =========================================

def get_tech_verifier_emails():
    return get_emails_by_roles([
        "TECH_VERIFIER",
        "ADMIN",
    ])


# =========================================
# VALIDATEURS TECHNIQUES
# =========================================

def get_tech_validator_emails():
    return get_emails_by_roles([
        "TECH_VALIDATOR",
        "ADMIN",
    ])


# =========================================
# ANCIEN ALIAS (compatibilité)
# =========================================

def get_tech_emails():
    return get_tech_validator_emails()


# =========================================
# PROJECT MANAGER
# =========================================

def get_project_emails():
    return get_emails_by_roles([
        "PROJECT_MANAGER",
        "ADMIN",
    ])


# =========================================
# ALIAS PROGRAM
# =========================================

def get_program_emails():
    return get_project_emails()


# =========================================
# ADMIN
# =========================================

def get_admin_emails():
    return get_emails_by_roles([
        "ADMIN",
    ])