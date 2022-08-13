from django.core.exceptions import ValidationError
from django.utils import timezone

from api.messages import MESSAGES


def validator_year(year):
    if year > timezone.now().year:
        raise ValidationError(MESSAGES["no_valid_year"])
