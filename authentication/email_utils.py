from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail
from celery import shared_task
import logging

signer = TimestampSigner()

logger = logging.getLogger(__name__)

def make_verification_token(email):
    # returns a signed token including email; you can also add other claims
    return signer.sign(email)

def verify_verification_token(token, max_age=60*60*24):  # 1 day
    try:
        email = signer.unsign(token, max_age=max_age)
        return email
    except SignatureExpired:
        return None
    except BadSignature:
        return None

def send_verification_email(user, request=None):
    token = make_verification_token(user.email)
    verify_path = reverse("email_verify")  # map to the view name below
    # build absolute url (if request provided)
    domain = request.build_absolute_uri(verify_path) if request else settings.SITE_URL + verify_path
    # ensure token appended
    verify_url = f"{domain}?token={token}"
    subject = "RemoSphere 🌍: Verify your email to continue"
    message = f"Hi {user.first_name},\nWelcome to RemoSphere 🌍, the best job board out there :)\n\nClick the link below to verify your email, and start using RemoSphere:\n\n{verify_url}\n\nIf you didn't create an account, ignore this."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


# def send_welcome_email(user):
#     subject = "Welcome to RemoSphere! 🌎"
#     message = (
#         f"Hi {user.first_name or user.username},\n\n"
#         "Your email has been successfully verified.\n"
#         "You now have access to all of RemoSphere's features.\n"
#         "Welcome aboard!"
#     )
# 
#     try:
#         send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
#         return f"Email sent to {email}"
# 
#     except Exception as exc:
#         raise self.retry(exc=exc, countdown=10)  # retry after 10 seconds

@shared_task(bind=True, max_retries=5)
def send_welcome_email(self, email, first_name=None):
    """
    Sends a welcome email asynchronously.
    Retries up to 5 times on failure.
    """
    subject = "Welcome to RemoSphere!"
    if first_name:
        message = (
            f"Hi {first_name},\n\n"
            "Your email has been successfully verified. Welcome to RemoSphere!\n\n"
            "Cheers,\nThe RemoSphere Team"
        )
    else:
        message = (
            "Hi,\n\n"
            "Your email has been successfully verified. Welcome to RemoSphere!\n\n"
            "Cheers,\nThe RemoSphere Team"
        )

    try:
        logger.info("send_welcome_email: sending to %s", email)
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        logger.info("send_welcome_email: sent to %s", email)
        return f"Email sent to {email}"

    except Exception as exc:
        logger.exception("send_welcome_email failed for %s", email)
        # retry with exponential backoff
        raise self.retry(exc=exc, countdown=10)
