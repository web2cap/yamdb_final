from api.messages import MESSAGES
from django.core.exceptions import ValidationError
from django.utils import timezone


def validator_year(year):
    if year > timezone.now().year:
        raise ValidationError(MESSAGES["no_valid_year"])
