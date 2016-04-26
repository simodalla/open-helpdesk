from django.db import models
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class OrganizationSettingManager(models.Manager):

    def get_from_email(self, email):
        try:
            validate_email(email)
            domain = email.split('@')[1]
            return self.get(email_domain=domain)
        except Exception as e:
            raise e

    def get_color_from_email(self, email):
        try:
            validate_email(email)
            return self.get_fied_from_email(
                email, 'email_background_color').lower().strip()
        except Exception:
            return ''

    def get_fied_from_email(self, email, field):
        try:
            validate_email(email)
            obj = self.get_from_email(email)
        except Exception as e:
            raise e
        return getattr(obj, field)

