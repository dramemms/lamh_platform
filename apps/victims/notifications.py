from django.conf import settings
from django.core.mail import send_mail


def _send_notification(subject, message, recipients):
    recipients = [email for email in recipients if email]
    if not recipients:
        return

    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=recipients,
        fail_silently=False,
    )


def notify_tech_on_victim_submission(victim):
    recipients = []

    # à adapter selon ton modèle User / logique de rôles
    if victim.accident and victim.accident.created_by and victim.accident.created_by.email:
        recipients.append(victim.accident.created_by.email)

    subject = f"[LAMH] Nouvelle fiche victime soumise - {victim.victim_id}"
    message = (
        f"Une fiche victime a été soumise.\n\n"
        f"ID victime : {victim.victim_id}\n"
        f"Nom : {victim.victim_full_name}\n"
        f"Référence accident : {victim.accident_reference or getattr(victim.accident, 'reference', '-')}\n"
        f"Statut : {victim.status}\n"
    )

    _send_notification(subject, message, recipients)


def notify_program_on_victim_tech_validation(victim):
    recipients = []

    subject = f"[LAMH] Fiche victime validée techniquement - {victim.victim_id}"
    message = (
        f"La fiche victime a été validée techniquement.\n\n"
        f"ID victime : {victim.victim_id}\n"
        f"Nom : {victim.victim_full_name}\n"
        f"Référence accident : {victim.accident_reference or getattr(victim.accident, 'reference', '-')}\n"
        f"Statut : {victim.status}\n"
    )

    _send_notification(subject, message, recipients)


def notify_submitter_on_victim_return(victim):
    recipients = []

    if victim.accident and victim.accident.created_by and victim.accident.created_by.email:
        recipients.append(victim.accident.created_by.email)

    subject = f"[LAMH] Fiche victime retournée pour correction - {victim.victim_id}"
    message = (
        f"La fiche victime a été retournée pour correction.\n\n"
        f"ID victime : {victim.victim_id}\n"
        f"Nom : {victim.victim_full_name}\n"
        f"Référence accident : {victim.accident_reference or getattr(victim.accident, 'reference', '-')}\n"
        f"Commentaire : {victim.correction_comment or '-'}\n"
        f"Statut : {victim.status}\n"
    )

    _send_notification(subject, message, recipients)


def notify_tech_on_victim_program_return(victim):
    recipients = []

    if victim.tech_validated_by and victim.tech_validated_by.email:
        recipients.append(victim.tech_validated_by.email)

    subject = f"[LAMH] Fiche victime retournée à la validation technique - {victim.victim_id}"
    message = (
        f"La fiche victime a été retournée à la validation technique.\n\n"
        f"ID victime : {victim.victim_id}\n"
        f"Nom : {victim.victim_full_name}\n"
        f"Référence accident : {victim.accident_reference or getattr(victim.accident, 'reference', '-')}\n"
        f"Statut : {victim.status}\n"
    )

    _send_notification(subject, message, recipients)


def notify_submitter_on_victim_approval(victim):
    recipients = []

    if victim.accident and victim.accident.created_by and victim.accident.created_by.email:
        recipients.append(victim.accident.created_by.email)

    subject = f"[LAMH] Fiche victime approuvée - {victim.victim_id}"
    message = (
        f"La fiche victime a été approuvée.\n\n"
        f"ID victime : {victim.victim_id}\n"
        f"Nom : {victim.victim_full_name}\n"
        f"Référence accident : {victim.accident_reference or getattr(victim.accident, 'reference', '-')}\n"
        f"Statut : {victim.status}\n"
    )

    _send_notification(subject, message, recipients)