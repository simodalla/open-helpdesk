from django.db import models
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class EmailOrganizationSettingManager(models.Manager):

    def get(self, email):
        try:
            validate_email(email)
            domain = email.split('@')[1]
            return super(EmailOrganizationSettingManager, self).get(
                email_domain=domain)
        except Exception as e:
            raise e

    def get_field(self, email, field):
        try:
            validate_email(email)
            obj = self.get(email)
        except Exception as e:
            raise e
        return getattr(obj, field)

    def get_color(self, email):
        try:
            validate_email(email)
            return self.get_field(
                email, 'email_background_color').lower().strip()
        except Exception:
            return ''

    def get_tipologies(self, email):
        from .models import Tipology
        try:
            obj = self.get(email)
            return Tipology.objects.filter(
                category__in=obj.categories.values_list('pk', flat=True))
        except Exception as e:
            raise e


