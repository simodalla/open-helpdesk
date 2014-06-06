# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
try:
    from django.db.transaction import atomic
except ImportError:  # pragma: no cover
    from django.db.transaction import commit_on_success as atomic

from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from mezzanine.conf import settings
from mezzanine.core.models import RichText, Slugged, TimeStamped
from mezzanine.utils.models import (upload_to, get_user_model_name,
                                    get_user_model)

from .managers import HeldeskableManager


User = get_user_model()
user_model_name = get_user_model_name()


PRIORITY_URGENT = 8
PRIORITY_HIGH = 4
PRIORITY_NORMAL = 2
PRIORITY_LOW = 1

PRIORITIES = (
    (PRIORITY_URGENT, _('Urgent')),
    (PRIORITY_HIGH, _('High')),
    (PRIORITY_NORMAL, _('Normal')),
    (PRIORITY_LOW, _('Low')),
)


class HelpdeskUser(User):
    class Meta:
        proxy = True

    @property
    def group_names(self):
        return self.groups.values_list('name', flat=True)

    def is_requester(self):
        if settings.HELPDESK_REQUESTERS in self.group_names:
            return True
        return False

    def is_operator(self):
        if settings.HELPDESK_OPERATORS in self.group_names:
            return True
        return False

    def is_admin(self):
        if settings.HELPDESK_ADMINS in self.group_names:
            return True
        return False


@python_2_unicode_compatible
class Category(TimeStamped):
    title = models.CharField(_('Title'), max_length=500, unique=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ('title',)

    def __str__(self):
        return self.title

    @property
    def tipology_pks(self):
        return [str(pk) for pk in self.tipologies.values_list('pk', flat=True)]

    def admin_tipologies(self):
        return '<br>'.join(
            ['<a href="{}?id={}" class="view_tipology">{}</a>'.format(
                reverse(admin_urlname(t._meta, 'changelist')), t.pk, t.title)
             for t in self.tipologies.all()])
    admin_tipologies.allow_tags = True
    admin_tipologies.short_description = _('Tipologies')


@python_2_unicode_compatible
class Tipology(TimeStamped):
    """
    Model for tipologies of tickets. Field sites is a 'ManyToManyField'
    because one tipology can be visible on more sites.
    """
    title = models.CharField(_('Title'), max_length=500)
    category = models.ForeignKey('Category',
                                 verbose_name=_('Categories'),
                                 related_name='tipologies')
    sites = models.ManyToManyField('sites.Site', blank=True,
                                   verbose_name=_('Enable on Sites'),
                                   related_name='tipologies')
    priority = models.IntegerField(_('Priority'), choices=PRIORITIES,
                                   default=PRIORITY_LOW)

    class Meta:
        verbose_name = _('Tipology')
        verbose_name_plural = _('Tipologies')
        ordering = ('category__title', 'title',)
        unique_together = ('title', 'category',)

    def __str__(self):
        return '[{self.category.title}] {self.title}'.format(self=self)

    def admin_category(self):
        return (
            '<a href="{url}?id={category.pk}" class="view_category">'
            '{category.title}</a>'.format(
                url=reverse('admin:helpdesk_category_changelist'),
                category=self.category))
    admin_category.allow_tags = True
    # TODO set orderable
    # admin_category.order
    admin_category.short_description = _('Enable on Sites')

    def admin_sites(self):
        return '<br>'.join(
            ['<a href="{url}?id={site.pk}" class="view_site">{site.domain}'
             '</a>'.format(url=reverse(admin_urlname(s._meta, 'changelist')),
                           site=s)
             for s in self.sites.all()])
    admin_sites.allow_tags = True
    admin_sites.short_description = _('Enable on Sites')


class Attachment(TimeStamped):
    f = models.FileField(verbose_name=_('File'),
                         upload_to=upload_to('helpdesk.Issue.attachments',
                                             'helpdesk/attachments'), )
    description = models.CharField(_('Description'), max_length=500)
    issue = models.ForeignKey('Ticket')

    class Meta:
        verbose_name = _('Attachment')
        verbose_name_plural = _('Attachments')
        ordering = ('-created',)


TICKET_STATUS_NEW = 1
TICKET_STATUS_OPEN = 2
TICKET_STATUS_PENDING = 3
TICKET_STATUS_SOLVED = 4
TICKET_STATUS = {
    TICKET_STATUS_NEW: _('New'),
    TICKET_STATUS_OPEN: _('Open'),
    TICKET_STATUS_PENDING: _('Pending'),
    TICKET_STATUS_SOLVED: _('Closed'),
}

TICKET_STATUS_CHOICES = tuple((k, v) for k, v in TICKET_STATUS.items())


@python_2_unicode_compatible
class Ticket(Slugged, TimeStamped, RichText):
    status = models.IntegerField(_('Status'),
                                 choices=TICKET_STATUS_CHOICES,
                                 default=TICKET_STATUS_NEW)
    tipologies = models.ManyToManyField('Tipology',
                                        verbose_name=_('Tipologies'))
    priority = models.IntegerField(_('Priority'), choices=PRIORITIES,
                                   default=PRIORITY_LOW)
    requester = models.ForeignKey(user_model_name, verbose_name=_('Requester'),
                                  related_name='requested_tickets')
    assignee = models.ForeignKey(user_model_name, verbose_name=_('Assignee'),
                                 related_name="assigned_tickets",
                                 blank=True, null=True)
    related_tickets = models.ManyToManyField(
        'self', verbose_name=_('Related tickets'), blank=True)

    objects = HeldeskableManager()

    class Meta:
        get_latest_by = 'created'
        ordering = ('-created',)
        verbose_name = _('Ticket')
        verbose_name_plural = _('Tickets')

    def __str__(self):
        return str(self.pk)

    @atomic
    def open(self, assignee):
        """Logic 'open' ticket operation.

        Opening the ticket. Set status to open, assignee user and create an
        StatusChangesLog.

        :param assignee: user to set 'assignee' field
        :type assignee: django.contrib.auth.get_user_model
        """
        if self.status != TICKET_STATUS_NEW:
            raise ValueError(_('Ticket is not "%(status)s"') %
                             {'status': str(TICKET_STATUS[TICKET_STATUS_NEW])})
        self.assignee = assignee
        self.status = TICKET_STATUS_OPEN
        self.save()
        self.status_changelogs.create(status_from=TICKET_STATUS_NEW,
                                      status_to=TICKET_STATUS_OPEN,
                                      changer=assignee)

    def put_on_pending(self, user):
        """Logic 'put_on_pending' ticket operation.

        Put on status 'pending' the ticket.

        :param user: user to set into status_changelogs related object
        :type user: django.contrib.auth.get_user_model
        """
        if self.status != TICKET_STATUS_OPEN:
            raise ValueError(
                _('Ticket is not "%(status)s"') % {
                    'status': str(TICKET_STATUS[TICKET_STATUS_OPEN])
                })


@python_2_unicode_compatible
class StatusChangesLog(TimeStamped):
    """
    StatusChangesLog model for record the changes of status of Tickets objects.
    """
    ticket = models.ForeignKey('Ticket', related_name='status_changelogs')
    status_from = models.IntegerField(choices=TICKET_STATUS_CHOICES)
    status_to = models.IntegerField(choices=TICKET_STATUS_CHOICES)
    changer = models.ForeignKey(user_model_name, verbose_name=_('Changer'))

    class Meta:
        get_latest_by = 'created'
        ordering = ('ticket', 'created')
        verbose_name = _('Status Changelog')
        verbose_name_plural = _('Status Changelogs')

    def __str__(self):
        return ('{ticket.pk} {created}: {status_from} ==> {status_to}'.format(
            ticket=self.ticket,
            created=self.created.strftime('%Y-%m-%d %H:%M:%S'),
            status_from=TICKET_STATUS[self.status_from],
            status_to=TICKET_STATUS[self.status_to]))
