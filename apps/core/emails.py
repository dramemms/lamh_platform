from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_workflow_email(subject, recipients, template, context):
    if not recipients:
        return 0

    text_body = render_to_string(template + ".txt", context)
    html_body = render_to_string(template + ".html", context)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
    )

    email.attach_alternative(html_body, "text/html")
    email.send()