import itertools

from django.db import models
from django.core.validators import validate_email

from . import models as op_models


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
        try:
            obj = self.get(email)
            # get pks of enabled tipologies of enabled categories of this obj
            # organization
            tipology_pks = set(
                itertools.chain(*[c.tipologies.values_list('pk', flat=True)
                                  for c in obj.categories_enabled.all()]))
            # differenze with pks of disabled
            tipology_pks = tipology_pks.difference(
                    set(obj.tipologies_disabled.values_list('pk', flat=True)))
            return op_models.Tipology.objects.filter(pk__in=tipology_pks)
        except Exception as e:
            raise e


