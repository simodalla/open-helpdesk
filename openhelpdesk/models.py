# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from future.builtins import str

import six

# from django.contrib.auth import get_user_model
from django.contrib.admin.templatetags.admin_urls import admin_urlname
try:
    from django.contrib.contenttypes import generic
except ImportError:
    from django.contrib.contenttypes import fields as generic
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
try:
    from django.db.transaction import atomic
except ImportError:  # pragma: no cover
    from django.db.transaction import commit_on_success as atomic
from django.template.defaultfilters import truncatewords, truncatechars, safe, mark_safe
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags, format_html, format_html_join
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.core.models import RichText, SiteRelated, TimeStamped
from mezzanine.utils.email import send_mail_template, subject_template

from model_utils.models import StatusModel
from model_utils import Choices

from tinymce.models import HTMLField

from .core import (TICKET_STATUSES, TicketIsNotNewError, TicketIsNotOpenError,
                   TicketIsClosedError,
                   TicketIsNotPendingError,
                   ACTIONS_ON_TICKET, DEFAULT_ACTIONS, TicketIsNewError,
                   HelpdeskUser)
from .managers import EmailOrganizationSettingManager


# User = get_user_model()
user_model_name = settings.AUTH_USER_MODEL


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



@python_2_unicode_compatible
class SiteConfiguration(models.Model):
    site = models.OneToOneField('sites.Site', primary_key=True,
                                verbose_name=_('Site'))
    _email_addr_from = models.EmailField(_('Email from'), blank=True)
    _email_addr_to_1 = models.EmailField(_('Email to - 1'), blank=True)
    _email_addr_to_2 = models.EmailField(_('Email to - 2'), blank=True)
    _email_addr_to_3 = models.EmailField(_('Email to - 3'), blank=True)

    class Meta:
        verbose_name = _('Site Configuration')
        verbose_name_plural = _('Site Configurations')
        ordering = ('site',)

    def __str__(self):
        return '{}'.format(self.site)

    @property
    def email_addrs_to(self):
        emails = {getattr(self, '_email_addr_to_%s' % i, None)
                  for i in [1, 2, 3]}
        return [email for email in emails if len(email)]

    @property
    def email_addr_from(self):
        return (self._email_addr_from if self._email_addr_from
                else self.get_no_site_email_addr_from())

    @staticmethod
    def get_no_site_email_addr_from():
        return settings.DEFAULT_FROM_EMAIL

    @staticmethod
    def get_no_site_email_addrs_to():
        return []

    def get_usernames_by_group(self, group_name):
        helpdesk_users = HelpdeskUser.filter_by_group(group_name)
        return self.site.sitepermission_set.filter(
            user__in=helpdesk_users).values_list('user__username', flat=True)


@python_2_unicode_compatible
class OrganizationSetting(TimeStamped):
    title = models.CharField(_('Title'), max_length=500, unique=True)
    email_domain = models.CharField(_('Email Domain'), max_length=100,
                                    unique=True)
    active = models.BooleanField(_('Active'), default=True)
    filter_label = models.CharField(_('Filter label'), max_length=20,
                                    blank=True)
    email_background_color = models.CharField(max_length=20,
                                              default='lightskyblue',
                                              blank=True)

    objects = models.Manager()
    email_objects = EmailOrganizationSettingManager()

    class Meta:
        get_latest_by = 'created'
        ordering = ('title',)
        verbose_name = _('Organization Setting')
        verbose_name_plural = _('Organization Settings')
        unique_together = ('email_domain', 'active',)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Category(TimeStamped):
    title = models.CharField(_('Title'), max_length=500, unique=True)
    enable_on_organizations = models.ManyToManyField(
        OrganizationSetting, blank=True, related_name='categories_enabled',
        verbose_name=_('Enable on organizations'))

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

    def admin_enable_on_organizations(self):
        return format_html_join(
            mark_safe('<br>'),
            '<a href="{}?id={}" class="view_tipology">{}</a>',
            ((reverse(admin_urlname(obj._meta, 'changelist')),
              obj.pk,
              obj.title)
             for obj in self.enable_on_organizations.all()))
    admin_enable_on_organizations.short_description = _(
        'Enable on organizations')


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
                                   related_name='helpdesk_tipologies')
    priority = models.IntegerField(_('Priority'), choices=PRIORITIES,
                                   default=PRIORITY_LOW)
    disable_on_organizations = models.ManyToManyField(
        OrganizationSetting, blank=True, related_name='tipologies_disabled',
        verbose_name=_('Disable on organizations'))

    class Meta:
        verbose_name = _('Tipology')
        verbose_name_plural = _('Tipologies')
        ordering = ('category__title', 'title',)
        unique_together = ('title', 'category',)

    def __str__(self):
        return '[{self.category.title}] {self.title}'.format(self=self)

    def admin_disable_on_organizations(self):
        return format_html_join(
            mark_safe('<br>'),
            '<a href="{}?id={}" class="view_tipology">{}</a>',
            ((reverse(admin_urlname(obj._meta, 'changelist')),
              obj.pk,
              obj.title)
             for obj in self.disable_on_organizations.all()))
    admin_disable_on_organizations.short_description = _(
        'Disable on organizations')


class Attachment(TimeStamped):
    f = models.FileField(verbose_name=_('File'),
                         upload_to='openhelpdesk/attachments/%Y/%m/%d')
    description = models.CharField(_('Description'), max_length=500,
                                   blank=True)
    content_type = models.ForeignKey('contenttypes.ContentType')
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('Attachment')
        verbose_name_plural = _('Attachments')
        ordering = ('-created',)


@python_2_unicode_compatible
class Source(TimeStamped):
    code = models.CharField(_('code'), max_length=30, unique=True)
    title = models.CharField(_('Title'), max_length=30, unique=True)
    sites = models.ManyToManyField('sites.Site', blank=True,
                                   verbose_name=_('Enable on Sites'),
                                   related_name='helpdesk_sources')
    awesome_icon = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = _('Source')
        verbose_name_plural = _('Sources')
        ordering = ('title',)

    def __str__(self):
        return self.title

    @classmethod
    def get_default_obj(cls):
        try:
            return cls.objects.get(code='web_site')
        except cls.DoesNotExist as dne:
            raise dne

    @property
    def icon(self):
        return self.awesome_icon

    @icon.setter
    def icon(self, icon_name):
        self.awesome_icon = icon_name


@python_2_unicode_compatible
class Ticket(SiteRelated, TimeStamped, StatusModel):
    STATUS = Choices(*TICKET_STATUSES)
    content = HTMLField(_("Content"))
    tipologies = models.ManyToManyField(
        'Tipology', verbose_name=_('Tipologies'),
        help_text=
        _("You can select a maximum of %(max)s %(tipologies)s.") % {
            # 'max': settings.OPENHELPDESK_MAX_TIPOLOGIES_FOR_TICKET,
            'max': 3,
            'tipologies': Tipology._meta.verbose_name_plural})
    priority = models.IntegerField(_('Priority'), choices=PRIORITIES,
                                   default=PRIORITY_LOW)
    insert_by = models.ForeignKey(user_model_name, verbose_name=_('Insert by'),
                                  related_name='inserted_tickets',
                                  editable=False)
    requester = models.ForeignKey(
        user_model_name, verbose_name=_('Requester'),
        related_name='requested_tickets',
        help_text=_("You must insert the Requester of Ticket.  Start to type"
                    " characters for searching into 'username', 'first name'"
                    " 'last name' or 'email' fields of Requester users."))
    assignee = models.ForeignKey(user_model_name, verbose_name=_('Assignee'),
                                 related_name="assigned_tickets",
                                 blank=True, null=True)
    related_tickets = models.ManyToManyField(
        'self', verbose_name=_('Related tickets'), blank=True,
        help_text=_("You can insert one or more related Tickets. Start to type"
                    " digits for searching into 'id' or 'content' fields of"
                    " your other Tickets previously inserted."))
    source = models.ForeignKey('Source', verbose_name=_('Source'),
                               blank=True, null=True)
    pending_ranges = generic.GenericRelation('PendingRange')

    class Meta:
        get_latest_by = 'created'
        ordering = ('-created',)
        verbose_name = _('Ticket')
        verbose_name_plural = _('Tickets')
        default_manager_name = 'objects'

    def __str__(self):
        return str(self.pk)

    def save(self, update_site=False, *args, **kwargs):
        if not self.id and not self.insert_by_id:
            self.insert_by_id = self.requester_id
        super(Ticket, self).save(update_site, *args, **kwargs)

    def get_clean_content(self, words=10, max_word_length=30):
        """
        Return self.content with html tags stripped and truncate after a
        "words" number of words with use of django template filter
        'truncatewords'.

        :param words: Number of words to truncate after
        :param max_word_length: Max number of chars to truncate the single word
        """
        return safe(' '.join(
            [truncatechars(w, max_word_length) for w in truncatewords(
                strip_tags(self.content), words).split(' ')]))

    def _is_in_status(self, status):
        return True if self.status == status else False

    def is_new(self):
        return self._is_in_status(self.STATUS.new)

    def is_open(self):
        return self._is_in_status(self.STATUS.open)

    def is_pending(self):
        return self._is_in_status(self.STATUS.pending)

    def is_closed(self):
        return self._is_in_status(self.STATUS.closed)

    @atomic
    def change_state(self, before, after, user):
        """Change status of ticket an record changelog for this.

        :param before: Ticket.STATUS, status that will be
        :param after: Ticket.STATUS, status before changing
        :param user: django.contrib.auth.get_user_model
        :return: StatusChangesLog created
        """
        self.status = after
        self.save()
        return self.status_changelogs.create(before=before,
                                             after=after,
                                             changer=user)
        # return True

    def initialize(self):
        """On inserting set status of ticket an record changelog for this."""
        if self.id:
            before = ''
            after = self.STATUS.new
            user = self.requester
            self.status_changelogs.create(before=before,
                                          after=after,
                                          changer=user)

    @atomic
    def opening(self, assignee):
        """Logic 'open' ticket operation.

        Opening the ticket. Set status to open, assignee user and create an
        StatusChangesLog.

        :param assignee: user to set 'assignee' field
        :type assignee: django.contrib.auth.get_user_model
        """
        if not self.is_new():
            raise TicketIsNotNewError()
        self.change_state(Ticket.STATUS.new, Ticket.STATUS.open, assignee)
        self.assignee = assignee
        self.save()

    @atomic
    def put_on_pending(self, user, estimated_end_date=None):
        """Logic 'put_on_pending' ticket operation.

        Set status to pending and create an StatusChangesLog object.

        :param user: user to set into status_changelogs related object
        :type user: django.contrib.auth.User
        :param estimated_end_date: "date" into format (yyyy-mm-dd) for
                                   an estimated date of end pending
        :type estimated_end_date: string
        """
        if self.status != Ticket.STATUS.open:
            raise TicketIsNotOpenError()
        statuschangelog = self.change_state(
            Ticket.STATUS.open, Ticket.STATUS.pending, user)
        if estimated_end_date:
            now = timezone.now()
            estimated_end_date = parse_datetime('{} {}:{}'.format(
                estimated_end_date, now.hour, now.minute)).replace(
                    tzinfo=timezone.utc)
        PendingRange.objects.create(start=statuschangelog.created,
                                    estimated_end=estimated_end_date,
                                    content_object=self)

    @atomic
    def remove_from_pending(self, user):
        """Logic 'remove from pending' ticket operation.

        Remove the pending status setting status to open, create an
        StatusChangesLog object for this, and .

        :param user: user to set 'user' field
        :type user: User
        :raises TicketIsNotPendingError: if the ticket not in pending status
        """
        if self.status != Ticket.STATUS.pending:
            raise TicketIsNotPendingError()
        statuschangelog = self.change_state(
            self.status, Ticket.STATUS.open, user)
        pending_range = self.pending_ranges.get(end__isnull=True)
        pending_range.end = statuschangelog.updated
        pending_range.save()
        return statuschangelog

    @atomic
    def closing(self, user):
        """Logic 'closing' ticket operation.

        Closing the ticket. Set status to closed and create an
        StatusChangesLog object.

        :param user: user to set 'user' field
        :type user: django.contrib.auth.get_user_model
        """
        if self.is_closed():
            raise TicketIsClosedError()
        if self.is_new():
            raise TicketIsNewError()
        pre_change_is_pending = self.is_pending()
        statuschangelog = self.change_state(
            self.status, Ticket.STATUS.closed, user)
        if pre_change_is_pending:
            pending_range = self.pending_ranges.get(end__isnull=True)
            pending_range.end = statuschangelog.updated
            pending_range.save()
        return statuschangelog

    @classmethod
    def get_actions_for_report(cls, ticket=None):
        """
        Return a tuple of strings representatives the possible actions,
        according to status of ticket parameter.

        :param ticket:
        :type ticket: Ticket or None
        :return: tuple of strings
        :rtype: tuple
        """
        result = tuple((k, ACTIONS_ON_TICKET[k]) for k in DEFAULT_ACTIONS)
        if ticket and isinstance(ticket, cls):
            if ticket.is_open():
                return result + tuple((k, ACTIONS_ON_TICKET[k])
                                      for k in ['put_on_pending', 'close'])
            elif ticket.is_pending():
                return result + tuple((k, ACTIONS_ON_TICKET[k])
                                      for k in ['remove_from_pending',
                                                'close'])
        return result

    @property
    def organization(self):
        try:
            return OrganizationSetting.email_objects.get(self.requester.email)
        except OrganizationSetting.DoesNotExist:
            return None



    def send_email_to_operators_on_adding(self, request):
        template = "openhelpdesk/email/ticket/ticket_operators_creation"
        requester_name = _('no personal info assigned')
        if self.requester.last_name and self.requester.first_name:
            requester_name = '{} {}'.format(self.requester.first_name,
                                            self.requester.last_name)
        subject = subject_template(
            "{}_subject.html".format(template),
            {'ticket_name': self._meta.verbose_name.lower(),
             'username': self.requester.email or self.requester.username})
        try:
            site_conf = SiteConfiguration.objects.get(site=self.site)
            addr_from = site_conf.email_addr_from
            addr_to = site_conf.email_addrs_to
        except SiteConfiguration.DoesNotExist:
            addr_from = SiteConfiguration.get_no_site_email_addr_from()
            addr_to = SiteConfiguration.get_no_site_email_addrs_to()
        change_url = reverse(admin_urlname(self._meta, 'change'),
                             args=(self.pk,))

        email_background_color = (
            OrganizationSetting.email_objects.get_color(
                self.requester.email))
        context = {'ticket_name': self._meta.verbose_name, 'ticket': self,
                   'request': request, 'change_url': change_url,
                   'requester_username': self.requester.username,
                   'requester_email': self.requester.email or _(
                       'no email assigned'),
                   'requester_name': requester_name,
                   'email_background_color': email_background_color}
        send_mail_template(subject, template, addr_from, addr_to,
                           context=context, attachments=None)


@python_2_unicode_compatible
class Message(TimeStamped):
    content = models.TextField(_('Content'))
    sender = models.ForeignKey(user_model_name, verbose_name=_('Sender'),
                               related_name='sender_of_messages')
    recipient = models.ForeignKey(user_model_name, verbose_name=_('Recipient'),
                                  blank=True, null=True,
                                  related_name='recipent_of_messages')
    ticket = models.ForeignKey('Ticket', related_name='messages',
                               blank=True, null=True, verbose_name=_('Ticket'))

    class Meta:
        get_latest_by = 'created'
        ordering = ('created',)
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')

    def __str__(self):
        return self.content

    def notify_to_operator(self, request):
        template = "openhelpdesk/email/message/notify_to_operator"
        context = {#'message': self,
                   'message_verbose_name': self._meta.verbose_name.lower(),
                   'message_from': '{} {}'.format(self.sender.last_name.capitalize(),
                                                  self.sender.first_name.capitalize()),
                   'email_background_color': (
                       OrganizationSetting.email_objects.get_color(
                           self.sender.email))}

        try:
            site_conf = SiteConfiguration.objects.get(site=self.ticket.site)
            addr_from = site_conf.email_addr_from
        except (SiteConfiguration.DoesNotExist, Ticket.DoesNotExist):
            addr_from = SiteConfiguration.get_no_site_email_addr_from()

        print(context)
        subject = subject_template("{}_subject.html".format(template), context)
        addr_to = [self.ticket.assignee.email or 'ced@unionerenolavinosamoggia.bo.it']
        ticket_url = 'http://{}{}'.format(
            request.get_host(),
            reverse(admin_urlname(self.ticket._meta, 'change'), args=(self.ticket_id,)))
        context.update({'request': request,
                        'ticket_url': ticket_url,
                        'message_url': ticket_url + "#tab_messages",
                        'ticket_id': self.ticket.id,
                        'content': self.content,
                        'message_from_email': self.sender.email})
        print(context)
        send_mail_template(subject, template, addr_from, addr_to,
                           context=context, attachments=None)


ACTIONS_ON_TICKET_CHOICES = tuple((k, ACTIONS_ON_TICKET[k])
                                  for k in ACTIONS_ON_TICKET)


@python_2_unicode_compatible
class Report(Message):
    action_on_ticket = models.CharField(
        _('Action on ticket'), max_length=50,
        choices=ACTIONS_ON_TICKET_CHOICES, default=DEFAULT_ACTIONS[0],
        help_text=_('Select any action to perform on the ticket.'))
    visible_from_requester = models.BooleanField(
        _('Visible from requester'), default=False,
        help_text=_('Check to make visible this report to the requester.'))

    class Meta:
        get_latest_by = 'created'
        ordering = ('created',)
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')

    def __str__(self):
        return self.content

    def send_email_to_requester(self, request):
        template = "openhelpdesk/email/report/info_to_request"
        operator = request.user
        operator_name = operator.username
        if operator.last_name and operator.first_name:
            operator_name = '{} {}'.format(operator.first_name,
                                           operator.last_name)
        context = {'report_name': self._meta.verbose_name.lower(),
                   'operator': operator,
                   'operator_name': operator_name,
                   'ticket_id': self.ticket_id,
                   'email_background_color': (
                       OrganizationSetting.email_objects.get_color(
                           self.ticket.requester.email))}

        try:
            site_conf = SiteConfiguration.objects.get(site=self.ticket.site)
            addr_from = site_conf.email_addr_from
        except (SiteConfiguration.DoesNotExist, Ticket.DoesNotExist):
            addr_from = SiteConfiguration.get_no_site_email_addr_from()

        subject = subject_template("{}_subject.html".format(template), context)
        addr_to = [self.ticket.requester.email]
        change_ticket_url = '{}#tab_messages'.format(
            reverse(admin_urlname(self.ticket._meta, 'change'),
                    args=(self.ticket_id,)))
        context.update({'report': self, 'request': request,
                        'change_ticket_url': change_ticket_url})
        send_mail_template(subject, template, addr_from, addr_to,
                           context=context, attachments=None)


@python_2_unicode_compatible
class PendingRange(models.Model):
    start = models.DateTimeField(null=True, editable=False)
    end = models.DateTimeField(null=True, editable=False)
    estimated_end = models.DateTimeField(null=True)
    content_type = models.ForeignKey('contenttypes.ContentType')
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        get_latest_by = 'id'
        ordering = ('start', 'end')
        verbose_name = _('Pending Range')
        verbose_name_plural = _('Pending Ranges')

    def __str__(self):
        return super(PendingRange, self).__str__()


@python_2_unicode_compatible
class Activity(TimeStamped, RichText):
    maker = models.ForeignKey(user_model_name, verbose_name=_('Maker'),
                              related_name='maker_of_activities')
    co_maker = models.ManyToManyField(user_model_name,
                                      verbose_name=_('Co Makers'),
                                      blank=True,
                                      related_name='co_maker_of_activities')
    ticket = models.ForeignKey('Ticket', related_name='activities',
                               blank=True, null=True)
    report = models.OneToOneField('Report', blank=True, null=True)
    scheduled_at = models.DateTimeField(blank=True, null=True,
                                        verbose_name=_('Scheduled at'))

    class Meta:
        get_latest_by = 'created'
        ordering = ('-created',)
        verbose_name = _('Activity')
        verbose_name_plural = _('Activities')

    def __str__(self):
        return self.content


@python_2_unicode_compatible
class StatusChangesLog(TimeStamped):
    """
    StatusChangesLog model for record the changes of status of Tickets objects.
    """
    ticket = models.ForeignKey('Ticket', related_name='status_changelogs')
    before = models.CharField(max_length=100, verbose_name=_('Before'))
    after = models.CharField(max_length=100, verbose_name=_('After'))
    changer = models.ForeignKey(user_model_name, verbose_name=_('Changer'))

    class Meta:
        get_latest_by = 'created'
        ordering = ('ticket', 'created')
        verbose_name = _('Status Changelog')
        verbose_name_plural = _('Status Changelogs')

    def __str__(self):
        return ('{self.ticket_id} {created}: {self.before} ==> '
                '{self.after}'.format(self=self,
                                      created=self.created.strftime(
                                          '%Y-%m-%d %H:%M:%S')))


class Subteam(TimeStamped):
    title = models.CharField(
        _('Title'),
        max_length=500,
        unique=True)
    organizations_managed = models.ManyToManyField(
        OrganizationSetting,
        blank=True,
        related_name='managed_from',
        verbose_name=_('organizations managed'))
    teammates = models.ManyToManyField(
        user_model_name,
        blank=True,
        related_name='subteams',
        verbose_name=_('teammates'))
    email = models.EmailField(blank=True)

    class Meta:
        verbose_name = _('Subteam')
        verbose_name_plural = _('Subteams')
        ordering = ('title',)

    def __str__(self):
        return self.title


class TeammateSetting(TimeStamped):
    user = models.OneToOneField(
        user_model_name,
        related_name='oh_teammate')
    default_subteam = models.ForeignKey(
        Subteam,
        blank=True,
        null=True,
        verbose_name=_('default subteam'))

    class Meta:
        verbose_name = _('Teammate Setting')
        verbose_name_plural = _('Teammate Settings')
        ordering = ('user',)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.default_subteam:
            self.default_subteam.teammates.add(self.user)