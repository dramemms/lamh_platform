from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

from .recipients import (
    get_tech_verifier_emails,
    get_tech_validator_emails,
    get_program_emails,
    get_admin_emails,
)


def build_url(path):
    base_url = getattr(settings, "SITE_URL", "http://127.0.0.1:8000")
    return f"{base_url}{path}"


def unique_emails(emails):
    return list(dict.fromkeys([email for email in (emails or []) if email]))


def get_submitter_recipients(obj):
    recipients = []

    if getattr(obj, "submitter_email", None):
        recipients.append(obj.submitter_email)

    submitted_by = getattr(obj, "submitted_by", None)
    if submitted_by and getattr(submitted_by, "email", None):
        recipients.append(submitted_by.email)

    created_by = getattr(obj, "created_by", None)
    if created_by and getattr(created_by, "email", None):
        recipients.append(created_by.email)

    reported_by = getattr(obj, "reported_by", None)
    if reported_by and isinstance(reported_by, str) and "@" in reported_by:
        recipients.append(reported_by)

    return unique_emails(recipients)


def send_notification(subject, message, recipients):
    recipients = unique_emails(recipients)

    print("DEBUG SEND MAIL:", subject, recipients)

    if not recipients:
        print("Aucun destinataire trouvé.")
        return

    send_mail(
        subject,
        message,
        getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@lamh.local"),
        recipients,
        fail_silently=False,
    )


# =============================
# ACCIDENTS
# =============================

def notify_accident_submitted(accident):
    recipients = get_tech_verifier_emails()
    url = build_url(reverse("accident_detail", args=[accident.pk]))

    message = f"""
Bonjour,

Un nouveau rapport d'accident a été soumis et attend une vérification technique.

Référence : {accident.reference or "-"}
Titre : {getattr(accident, "title", None) or "-"}
Organisation : {getattr(accident, "org_name", None) or "-"}
Date accident : {getattr(accident, "accident_date", None) or "-"}
Localité : {getattr(accident, "locality", None) or "-"}

Lien :
{url}

Cordialement,
LAMH Plateforme
"""

    send_notification("Nouvel accident à vérifier", message, recipients)


def notify_accident_tech_verified(accident):
    recipients = get_tech_validator_emails()
    url = build_url(reverse("accident_detail", args=[accident.pk]))

    message = f"""
Bonjour,

Un rapport d'accident a été vérifié techniquement et attend une validation technique.

Référence : {accident.reference or "-"}
Titre : {getattr(accident, "title", None) or "-"}
Organisation : {getattr(accident, "org_name", None) or "-"}
Date accident : {getattr(accident, "accident_date", None) or "-"}
Localité : {getattr(accident, "locality", None) or "-"}

Lien :
{url}

Cordialement,
LAMH Plateforme
"""

    send_notification("Accident vérifié techniquement", message, recipients)


def notify_accident_tech_validated(accident):
    recipients = get_program_emails()
    url = build_url(reverse("accident_detail", args=[accident.pk]))

    message = f"""
Bonjour,

Un rapport d'accident a été validé techniquement et attend une validation programme.

Référence : {accident.reference or "-"}
Titre : {getattr(accident, "title", None) or "-"}
Organisation : {getattr(accident, "org_name", None) or "-"}
Date accident : {getattr(accident, "accident_date", None) or "-"}
Localité : {getattr(accident, "locality", None) or "-"}

Lien :
{url}

Cordialement,
LAMH Plateforme
"""

    send_notification("Accident validé techniquement", message, recipients)


def notify_accident_program_validated(accident):
    recipients = get_admin_emails()
    url = build_url(reverse("accident_detail", args=[accident.pk]))

    message = f"""
Bonjour,

Un rapport d'accident a été validé par le Project Manager et attend une approbation finale.

Référence : {accident.reference or "-"}
Titre : {getattr(accident, "title", None) or "-"}
Organisation : {getattr(accident, "org_name", None) or "-"}
Date accident : {getattr(accident, "accident_date", None) or "-"}
Localité : {getattr(accident, "locality", None) or "-"}

Lien :
{url}

Cordialement,
LAMH Plateforme
"""

    send_notification("Accident validé - Approbation requise", message, recipients)


def notify_accident_returned(accident):
    recipients = get_submitter_recipients(accident)
    url = build_url(reverse("accident_detail", args=[accident.pk]))

    message = f"""
Bonjour,

Votre rapport d'accident a été retourné pour correction.

Référence : {accident.reference or "-"}
Titre : {getattr(accident, "title", None) or "-"}
Organisation : {getattr(accident, "org_name", None) or "-"}

Motif du retour :
{getattr(accident, "rejection_reason", None) or "-"}

Lien :
{url}

Cordialement,
LAMH Plateforme
"""

    send_notification("Accident retourné pour correction", message, recipients)


def notify_accident_approved(accident):
    recipients = get_submitter_recipients(accident)
    url = build_url(reverse("accident_detail", args=[accident.pk]))

    message = f"""
Bonjour,

Votre rapport d'accident a été approuvé définitivement.

Référence : {accident.reference or "-"}
Titre : {getattr(accident, "title", None) or "-"}
Organisation : {getattr(accident, "org_name", None) or "-"}
Date accident : {getattr(accident, "accident_date", None) or "-"}
Localité : {getattr(accident, "locality", None) or "-"}

Lien :
{url}

Cordialement,
LAMH Plateforme
"""

    send_notification("Accident approuvé définitivement", message, recipients)


# =============================
# VICTIMES
# =============================

def notify_victim_submitted(victim):
    recipients = get_tech_verifier_emails()
    url = build_url(reverse("victim_detail", args=[victim.pk]))

    message = f"""
Bonjour,

Une nouvelle fiche victime a été soumise et attend une vérification technique.

ID victime : {victim.victim_id or "-"}
Accident : {victim.accident_reference or "-"}
Nom : {victim.victim_last_name or "-"} {victim.victim_first_name or "-"}
Organisation : {victim.reporting_org or "-"}

Lien :
{url}

Cordialement,
LAMH Plateforme
"""

    send_notification("Nouvelle victime à vérifier", message, recipients)


def notify_victim_tech_verified(victim):
    recipients = get_tech_validator_emails()
    url = build_url(reverse("victim_detail", args=[victim.pk]))

    message = f"""
Bonjour,

Une fiche victime a été vérifiée techniquement et attend une validation technique.

ID victime : {victim.victim_id or "-"}
Accident : {victim.accident_reference or "-"}
Nom : {victim.victim_last_name or "-"} {victim.victim_first_name or "-"}
Organisation : {victim.reporting_org or "-"}

Lien :
{url}

Cordialement,
LAMH Plateforme
"""

    send_notification("Victime vérifiée techniquement", message, recipients)


def notify_victim_tech_validated(victim):
    recipients = get_program_emails()
    url = build_url(reverse("victim_detail", args=[victim.pk]))

    message = f"""
Bonjour,

Une fiche victime a été validée techniquement et attend une validation programme.

ID victime : {victim.victim_id or "-"}
Accident : {victim.accident_reference or "-"}
Nom : {victim.victim_last_name or "-"} {victim.victim_first_name or "-"}
Organisation : {victim.reporting_org or "-"}

Lien :
{url}

Cordialement,
LAMH Plateforme
"""

    send_notification("Validation technique effectuée", message, recipients)


def notify_victim_program_validated(victim):
    recipients = get_admin_emails()
    url = build_url(reverse("victim_detail", args=[victim.pk]))

    message = f"""
Bonjour,

Une fiche victime a été validée par le Project Manager et attend une approbation finale.

ID victime : {victim.victim_id or "-"}
Accident : {victim.accident_reference or "-"}
Nom : {victim.victim_last_name or "-"} {victim.victim_first_name or "-"}
Organisation : {victim.reporting_org or "-"}

Lien :
{url}

Cordialement,
LAMH Plateforme
"""

    send_notification("Validation Programme - Approbation finale requise", message, recipients)


def notify_victim_returned(victim):
    recipients = get_submitter_recipients(victim)
    url = build_url(reverse("victim_detail", args=[victim.pk]))

    message = f"""
Bonjour,

Votre fiche victime a été retournée pour correction.

ID victime : {victim.victim_id or "-"}
Accident : {victim.accident_reference or "-"}
Nom : {victim.victim_last_name or "-"} {victim.victim_first_name or "-"}
Organisation : {victim.reporting_org or "-"}

Motif :
{victim.rejection_reason or "-"}

Lien :
{url}

Cordialement,
LAMH Plateforme
"""

    send_notification("Fiche victime retournée pour correction", message, recipients)


def notify_victim_approved(victim):
    recipients = get_submitter_recipients(victim)
    url = build_url(reverse("victim_detail", args=[victim.pk]))

    message = f"""
Bonjour,

Votre fiche victime a été approuvée définitivement.

ID victime : {victim.victim_id or "-"}
Accident : {victim.accident_reference or "-"}
Nom : {victim.victim_last_name or "-"} {victim.victim_first_name or "-"}
Organisation : {victim.reporting_org or "-"}

Lien :
{url}

Cordialement,
LAMH Plateforme
"""

    send_notification("Victime approuvée définitivement", message, recipients)


# =============================
# EREE
# =============================

def notify_eree_submitted(eree):
    recipients = get_tech_verifier_emails()
    url = build_url(reverse("eree_detail", args=[eree.pk]))

    message = f"""
Bonjour,

Une session EREE a été soumise et attend une vérification technique.

Référence : {eree.reference or "-"}
Titre : {eree.title or "-"}
Organisation : {eree.organisation or "-"}

Lien :
{url}

Cordialement,
LAMH Plateforme
"""

    send_notification("Nouvelle session EREE à vérifier", message, recipients)


def notify_eree_tech_verified(eree):
    recipients = get_tech_validator_emails()
    url = build_url(reverse("eree_detail", args=[eree.pk]))

    message = f"""
Bonjour,

Une session EREE a été vérifiée techniquement et attend une validation technique.

Référence : {eree.reference or "-"}
Titre : {eree.title or "-"}
Organisation : {eree.organisation or "-"}

Lien :
{url}

Cordialement,
LAMH Plateforme
"""

    send_notification("EREE vérifiée techniquement", message, recipients)


def notify_eree_tech_validated(eree):
    recipients = get_program_emails()
    url = build_url(reverse("eree_detail", args=[eree.pk]))

    message = f"""
Bonjour,

Une session EREE a été validée techniquement et attend une validation programme.

Référence : {eree.reference or "-"}
Titre : {eree.title or "-"}
Organisation : {eree.organisation or "-"}

Lien :
{url}

Cordialement,
LAMH Plateforme
"""

    send_notification("EREE validée techniquement", message, recipients)


def notify_eree_program_validated(eree):
    recipients = get_admin_emails()
    url = build_url(reverse("eree_detail", args=[eree.pk]))

    message = f"""
Bonjour,

Une session EREE a été validée par le Project Manager et attend une approbation finale.

Référence : {eree.reference or "-"}
Titre : {eree.title or "-"}
Organisation : {eree.organisation or "-"}

Lien :
{url}

Cordialement,
LAMH Plateforme
"""

    send_notification("EREE validée - Approbation requise", message, recipients)


def notify_eree_returned(eree):
    recipients = get_submitter_recipients(eree)
    url = build_url(reverse("eree_detail", args=[eree.pk]))

    message = f"""
Bonjour,

Votre session EREE a été retournée pour correction.

Référence : {eree.reference or "-"}
Titre : {eree.title or "-"}
Organisation : {eree.organisation or "-"}

Motif :
{eree.rejection_reason or "-"}

Lien :
{url}

Cordialement,
LAMH Plateforme
"""

    send_notification("EREE retournée pour correction", message, recipients)


def notify_eree_approved(eree):
    recipients = get_submitter_recipients(eree)
    url = build_url(reverse("eree_detail", args=[eree.pk]))

    message = f"""
Bonjour,

Votre session EREE a été approuvée définitivement.

Référence : {eree.reference or "-"}
Titre : {eree.title or "-"}
Organisation : {eree.organisation or "-"}

Lien :
{url}

Cordialement,
LAMH Plateforme
"""

    send_notification("EREE approuvée définitivement", message, recipients)