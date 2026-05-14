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
    ])


# =========================================
# VALIDATEURS TECHNIQUES
# =========================================

def get_tech_validator_emails():
    return get_emails_by_roles([
        "TECH_VALIDATOR",
    ])


# =========================================
# ANCIEN ALIAS COMPATIBILITE
# =========================================

def get_tech_emails():
    return get_tech_validator_emails()


# =========================================
# PROJECT / PROGRAM MANAGER
# =========================================

def get_project_emails():
    return get_emails_by_roles([
        "PROJECT_MANAGER",
    ])


def get_program_emails():
    return get_project_emails()


# =========================================
# ADMIN FINAL
# =========================================

def get_admin_emails():
    return get_emails_by_roles([
        "ADMIN",
    ])


# =========================================
# SOUMISSIONNAIRE / CREATEUR
# =========================================

def get_submitter_email(obj):
    """
    Retourne l'email du soumissionnaire/créateur si disponible.
    Compatible avec plusieurs noms de champs possibles.
    """

    possible_user_fields = [
        "submitted_by",
        "created_by",
        "created_user",
        "user",
        "author",
    ]

    for field in possible_user_fields:
        user = getattr(obj, field, None)
        if user and getattr(user, "email", None):
            return [user.email]

    possible_email_fields = [
        "submitter_email",
        "created_by_email",
        "email",
    ]

    for field in possible_email_fields:
        email = getattr(obj, field, None)
        if email:
            return [email]

    return []


# =========================================
# DESTINATAIRE SELON ETAPE WORKFLOW
# =========================================

def get_next_approver_emails(status):
    """
    Retourne uniquement les emails des personnes qui doivent agir
    à l'étape suivante du workflow.
    """

    if status == "SUBMITTED":
        return get_tech_verifier_emails()

    if status == "TECH_VERIFIED":
        return get_tech_validator_emails()

    if status == "TECH_VALIDATED":
        return get_program_emails()

    if status == "PROGRAM_VALIDATED":
        return get_admin_emails()

    return []


# =========================================
# DESTINATAIRES POUR RETOUR / REJET
# =========================================

def get_return_recipient_emails(obj):
    """
    En cas de retour ou rejet, on notifie uniquement la personne concernée.
    Priorité : soumissionnaire/créateur.
    """

    return get_submitter_email(obj)


# =========================================
# SUPPRESSION DES DOUBLONS
# =========================================

def unique_emails(emails):
    """
    Nettoie une liste d'emails :
    - supprime les valeurs vides
    - supprime les doublons
    """

    cleaned = []

    for email in emails:
        if email and email not in cleaned:
            cleaned.append(email)

    return cleaned