# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#from future.builtins import str

from django.db import models
#from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from mezzanine.core.fields import FileField
from mezzanine.core.models import Ownable, RichText, Slugged, TimeStamped
from mezzanine.utils.models import upload_to

from .managers import HeldeskableManager


@python_2_unicode_compatible
class Category(TimeStamped):
    title = models.CharField(_("Title"), max_length=500)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ("title",)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Tipology(TimeStamped):
    title = models.CharField(_("Title"), max_length=500)
    category = models.ManyToManyField("Category", blank=True,
                                      verbose_name=_("Categories"),
                                      related_name="tipologies")
    sites = models.ManyToManyField("sites.Site", blank=True,
                                   verbose_name=_("Sites"))

    class Meta:
        verbose_name = _("Tipology")
        verbose_name_plural = _("Tipologies")
        ordering = ("title",)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Attachment(TimeStamped):
    f = models.FileField(verbose_name=_("File"),
                  upload_to=upload_to("helpdesk.Issue.attachments",
                                      "helpdesk/attachments"),)
    description = models.CharField(_("Description"), max_length=500)
    issue = models.ForeignKey("Issue")

    class Meta:
        verbose_name = _("Attachment")
        verbose_name_plural = _("Attachments")
        ordering = ("-created",)

    def __str__(self):
        return "attachment"


# ISSUE_STATUS_DRAFT = 1
# CONTENT_STATUS_PUBLISHED = 2
# CONTENT_STATUS_CHOICES = (
#     (CONTENT_STATUS_DRAFT, _("Draft")),
#     (CONTENT_STATUS_PUBLISHED, _("Published")),
# )

class Issue(Slugged, TimeStamped, Ownable, RichText):
    """
    A Issue.
    """
    # status = models.IntegerField(_("Status"),
    #                          choices=CONTENT_STATUS_CHOICES,
    #                          default=CONTENT_STATUS_PUBLISHED,
    #                          help_text=_(
    #                              "With Draft chosen, will only be shown for admin users "
    #                              "on the site."))
    tipology = models.ManyToManyField("Tipology",
                                      verbose_name=_("Tipologies"),
                                      related_name="issues")
    related_issues = models.ManyToManyField(
        "self", verbose_name=_("Related issues"), blank=True)

    objects = HeldeskableManager()

    class Meta:
        verbose_name = _("Issue")
        verbose_name_plural = _("Issues")
        ordering = ("-created",)
