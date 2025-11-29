from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail
from celery import shared_task
import logging
from users.models import User
from django.conf import settings
import jwt
import logging
from datetime import datetime, timedelta


signer = TimestampSigner()

logger = logging.getLogger(__name__)


def make_verification_token(email):
    # returns a signed token including email; you can also add other claims
    return signer.sign(email)


def verify_verification_token(token, max_age=60 * 60 * 24):  # 1 day
    try:
        email = signer.unsign(token, max_age=max_age)
        return email
    except SignatureExpired:
        return None
    except BadSignature:
        return None


@shared_task  # (bind=True, max_retries=5)
def send_verification_email(user_id, domain):
    """
    Send verification email to user.
    
    Args:
        user_id: ID of the user to send email to
        domain: The domain to use for the verification link
                (e.g., http://localhost:8000 from Swagger, 
                 or http://localhost:8080 from frontend)
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return f"User does not exist."

    token = make_verification_token(user.email)
    
    # Determine the correct path based on the domain
    # If domain is frontend URL, use frontend route
    # If domain is backend URL, use backend API route
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:8080')
    
    if domain.startswith(frontend_url):
        # Frontend URL - use frontend route
        verify_path = '/auth/verify'
    else:
        # Backend URL - use backend API route
        verify_path = reverse("email_verify")
    
    # Build verification URL
    verify_url = f"{domain.rstrip('/')}{verify_path}?token={token}"
    
    subject = "RemoSphere 🌍: Verify your email to continue"
    message = f"""Hi {user.first_name},
Welcome to RemoSphere 🌍, the best job board out there :)

Click the link below to verify your email, and start using RemoSphere:

{verify_url}

If you didn't create an account, ignore this."""
    
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


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
            "Your email has been successfully verified. 🎉\n"
            "You can now login to access all of our features!\n"
            "Welcome to RemoSphere!\n\n"
            "Cheers,\nThe RemoSphere Team"
        )
    else:
        message = (
            "Hi,\n\n"
            "Your email has been successfully verified. 🎉\n"
            "You can now login to access all of our features!\n"
            "Welcome to RemoSphere!\n\n"
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


def make_password_reset_token(user_id):
    """
    Create a short-lived JWT for password reset.
    """
    now = datetime.utcnow()
    exp = now + timedelta(minutes=getattr(settings,
                          "PASSWORD_RESET_TOKEN_LIFETIME_MINUTES", 30))
    payload = {
        "sub": int(user_id),
        "type": "password_reset",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(
        payload,
        settings.PASSWORD_RESET_SIGNING_KEY,
        algorithm=settings.PASSWORD_RESET_ALGORITHM)
    # PyJWT returns str in modern versions; ensure str
    return token if isinstance(token, str) else token.decode()


def verify_password_reset_token(token):
    """
    Return user_id if token valid, else None.
    Raises descriptive errors as needed.
    """
    try:
        payload = jwt.decode(
            token, settings.PASSWORD_RESET_SIGNING_KEY, algorithms=[
                settings.PASSWORD_RESET_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return {"error": "expired"}
    except jwt.InvalidTokenError:
        return {"error": "invalid"}

    if payload.get("type") != "password_reset":
        return {"error": "invalid_type"}

    user_id = payload.get("sub")
    if not user_id:
        return {"error": "invalid_payload"}

    return {"user_id": int(user_id)}


@shared_task(bind=True, max_retries=3)
def send_password_reset_email(self, user_email, reset_token, domain):
    """
    Sends password reset email (async).
    Arguments are primitives so Celery can serialize.
    """
    try:
        # optional: frontend path name; or build custom
        reset_path = reverse("password_reset_frontend")
    except Exception:
        reset_path = "/reset-password"

    # domain should already be absolute (e.g., request.build_absolute_uri("/"))
    # Build final URL:
    if domain.endswith("/"):
        base = domain[:-1]
    else:
        base = domain
    reset_url = f"{base}{reset_path}?token={reset_token}"

    subject = "RemoSphere — Password reset instructions"
    message = (
        f"Hi,\n\n"
        "We received a request to reset your RemoSphere password.\n"
        f"Click the link below to reset it (valid for {settings.PASSWORD_RESET_TOKEN_LIFETIME_MINUTES} minutes):\n\n"
        f"{reset_url}\n\n"
        "If you didn't request this, you can safely ignore this email.\n"
    )

    try:
        logger.info("Sending password reset email to %s", user_email)
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False)
        logger.info("Password reset email sent to %s", user_email)
        return True
    except Exception as exc:
        logger.exception(
            "Failed sending password reset email to %s: %s",
            user_email,
            exc)
        # retry with exponential backoff
        raise self.retry(exc=exc, countdown=10)
