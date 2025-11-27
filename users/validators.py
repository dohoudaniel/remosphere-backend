import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class StrongPasswordValidator:
    """
    Validates password strength based on standard security rules.
    Provides detailed error messages for each rule that fails.
    """

    def validate(self, password, user=None):
        errors = []

        # Minimum length
        if len(password) < 8:
            errors.append(_("Password must be at least 8 characters long."))

        # Uppercase
        if not re.search(r"[A-Z]", password):
            errors.append(
                _("Password must contain at least one uppercase letter."))

        # Lowercase
        if not re.search(r"[a-z]", password):
            errors.append(
                _("Password must contain at least one lowercase letter."))

        # Digit
        if not re.search(r"\d", password):
            errors.append(_("Password must contain at least one digit."))

        # Special character
        if not re.search(r"[^\w]", password):
            errors.append(
                _("Password must contain at least one special character (!@#$%^&* etc)."))

        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return _(
            "Your password must contain: at least 8 characters, "
            "one uppercase letter, one lowercase letter, one number, "
            "and one special character."
        )
