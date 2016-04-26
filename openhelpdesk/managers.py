from django.db import models
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class OrganizationSettingManager(models.Manager):

    def get_from_email(self, email):
        try:
            validate_email(email)
        except ValidationError as ve:
            raise ve
        domain = email.split('@')[1]
        try:
            obj = self.get(email_domain=domain)
        except Exception as e:
            raise e
        return obj

    def get_color_from_email(self, email):
        try:
            validate_email(email)
            obj = self.get_from_email(email)
        except ValidationError:
            return ''
        except Exception:
            # TODO fare il logging
            return ''
        return obj.email_background_color.lower().strip()
