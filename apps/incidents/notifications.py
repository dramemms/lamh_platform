from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

User = get_user_model()


def send_workflow_email(subject, message, recipients):
    recipients = list({email.strip() for email in recipients if email and email.strip()})

    print("=== EMAIL WORKFLOW ===")
    print("Sujet :", subject)
    print("Destinataires :", recipients)
    print("From :", getattr(settings, "DEFAULT_FROM_EMAIL", None))

    if not recipients:
        print("Aucun destinataire valide. Email non envoyé.")
        return

    result = send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=False,
    )

    print("Résultat send_mail :", result)


def get_users_by_group_and_region(group_name, region):
    if region is None:
        print(f"Aucune région fournie pour le groupe {group_name}.")
        return User.objects.none()

    users = User.objects.filter(
        groups__name__iexact=group_name,
        is_active=True,
        region=region,
    ).exclude(email="").distinct()

    print(f"Utilisateurs trouvés pour groupe={group_name}, région={region} :", list(users.values_list("username", "email")))
    return users


def notify_tech_on_submission(accident):
    print(f"notify_tech_on_submission() appelé pour accident #{accident.pk}")

    tech_users = get_users_by_group_and_region("Technique", accident.region)
    recipients = [u.email for u in tech_users]

    subject = f"[LAMH] Nouveau rapport à valider techniquement - {accident.reference}"
    message = (
        f"Bonjour,\n\n"
        f"Un accident a été soumis et attend une validation technique.\n\n"
        f"Référence : {accident.reference}\n"
        f"Titre : {accident.title}\n"
        f"Région : {accident.region}\n"
        f"Date de l'accident : {accident.accident_date}\n\n"
        f"Merci de vous connecter à la plateforme LAMH pour traitement."
    )
    send_workflow_email(subject, message, recipients)


def notify_program_on_tech_validation(accident):
    print(f"notify_program_on_tech_validation() appelé pour accident #{accident.pk}")

    program_users = get_users_by_group_and_region("Programme", accident.region)
    recipients = [u.email for u in program_users]

    subject = f"[LAMH] Rapport à valider au niveau programme - {accident.reference}"
    message = (
        f"Bonjour,\n\n"
        f"Le rapport suivant a été validé techniquement et attend votre validation programme.\n\n"
        f"Référence : {accident.reference}\n"
        f"Titre : {accident.title}\n"
        f"Région : {accident.region}\n\n"
        f"Merci de vous connecter à la plateforme LAMH."
    )
    send_workflow_email(subject, message, recipients)


def notify_submitter_on_tech_reject(accident):
    print(f"notify_submitter_on_tech_reject() appelé pour accident #{accident.pk}")
    print("Submitter email :", accident.submitter_email)

    recipients = [accident.submitter_email]

    subject = f"[LAMH] Rapport retourné pour correction - {accident.reference}"
    message = (
        f"Bonjour,\n\n"
        f"Votre rapport a été retourné pour correction.\n\n"
        f"Référence : {accident.reference}\n"
        f"Titre : {accident.title}\n"
        f"Région : {accident.region}\n"
        f"Motif : {accident.rejection_reason or '-'}\n\n"
        f"Merci de corriger puis de resoumettre le rapport."
    )
    send_workflow_email(subject, message, recipients)


def notify_tech_on_program_reject(accident):
    print(f"notify_tech_on_program_reject() appelé pour accident #{accident.pk}")

    recipients = []

    if (
        accident.tech_validated_by
        and accident.tech_validated_by.email
        and accident.tech_validated_by.region == accident.region
    ):
        recipients.append(accident.tech_validated_by.email)

    tech_users = get_users_by_group_and_region("Technique", accident.region)
    recipients.extend([u.email for u in tech_users])

    subject = f"[LAMH] Rapport retourné à la validation technique - {accident.reference}"
    message = (
        f"Bonjour,\n\n"
        f"Le rapport a été retourné par le niveau programme.\n\n"
        f"Référence : {accident.reference}\n"
        f"Titre : {accident.title}\n"
        f"Région : {accident.region}\n"
        f"Motif : {accident.rejection_reason or '-'}\n\n"
        f"Merci de revoir le dossier."
    )
    send_workflow_email(subject, message, recipients)


def notify_submitter_on_approval(accident):
    print(f"notify_submitter_on_approval() appelé pour accident #{accident.pk}")
    print("Submitter email :", accident.submitter_email)

    recipients = [accident.submitter_email]

    subject = f"[LAMH] Rapport approuvé - {accident.reference}"
    message = (
        f"Bonjour,\n\n"
        f"Votre rapport a été approuvé avec succès.\n\n"
        f"Référence : {accident.reference}\n"
        f"Titre : {accident.title}\n"
        f"Région : {accident.region}\n\n"
        f"Merci."
    )
    send_workflow_email(subject, message, recipients)