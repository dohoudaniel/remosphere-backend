from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail

signer = TimestampSigner()

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
    subject = "Verify your RemoSphere email"
    message = f"Hi {user.first_name},\n\nClick the link to verify your email:\n\n{verify_url}\n\nIf you didn't create an account, ignore this."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

