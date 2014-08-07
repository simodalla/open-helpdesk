# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
try:
    from django.db.transaction import atomic
except ImportError:  # pragma: no cover
    from django.db.transaction import commit_on_success as atomic
from django.template.defaultfilters import truncatewords
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.core.models import RichText, SiteRelated, TimeStamped
from mezzanine.utils.models import (get_user_model_name, get_user_model)

from model_utils.models import StatusModel
from model_utils import Choices

from .core import (TICKET_STATUSES, TicketIsNotNewError, TicketIsNotOpenError,
                   TicketIsClosedError,
                   TicketIsNotPendingError,
                   ACTIONS_ON_TICKET, DEFAULT_ACTIONS, TicketIsNewError)


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


@python_2_unicode_compatible
class HelpdeskUser(User):
    class Meta:
        proxy = True

    def __str__(self):
        return ('{} {}'.format(self.last_name.capitalize(),
                               self.first_name.capitalize())
                if (self.last_name and self.first_name) else self.username)

    @property
    def group_names(self):
        return self.groups.values_list('name', flat=True)

    @classmethod
    def get_from_request(cls, request):
        return cls.objects.get(pk=request.user.pk)

    def is_requester(self):
        """Test if user belong to settings.HELPDESK_REQUESTERS group."""
        if settings.HELPDESK_REQUESTERS in self.group_names:
            return True
        return False

    def is_operator(self):
        """Test if user belong to settings.HELPDESK_OPERATORS group."""
        if settings.HELPDESK_OPERATORS in self.group_names:
            return True
        return False

    def is_admin(self):
        """Test if user belong to settings.HELPDESK_ADMINS group."""
        if settings.HELPDESK_ADMINS in self.group_names:
            return True
        return False

    def get_messages_by_ticket(self, ticket_id):
        """
        Returns Messages' queryset filterd by 'ticket_id' parameter and
        ordered by createion date. If user (self) is a requester queryset
        is filtered on Report is only visible by requester and where sender
        or recipient is user (self).

        :param ticket_id: ticket id
        :return: recordset of Message objects
        """
        messages = Message.objects.select_related(
            'sender', 'recipient').filter(ticket_id=ticket_id)
        if self.is_requester():
            messages = messages.exclude(
                report__visible_from_requester=False).filter(
                    Q(sender__id=self.id) | Q(recipient__id=self.id))
        return messages.order_by('created')


# monkey-patch for add __str__ method of HelpdeskUser to system User model
User.__str__ = HelpdeskUser.__str__
if hasattr(User, '__unicode__') and hasattr(HelpdeskUser, '__unicode__'):
    User.__unicode__ = HelpdeskUser.__unicode__


@python_2_unicode_compatible
class SiteConfiguration(TimeStamped):
    site = models.OneToOneField('sites.Site')
    email_addr_from = models.EmailField(blank=True)
    email_addr_to_1 = models.EmailField(blank=True)
    email_addr_to_2 = models.EmailField(blank=True)
    email_addr_to_3 = models.EmailField(blank=True)

    class Meta:
        verbose_name = _('Site Configuration')
        verbose_name_plural = _('Site Configurations')
        ordering = ('site',)

    def __str__(self):
        return '{}'.format(self.site)

    @property
    def email_addrs_to(self):
        emails = {getattr(self, 'email_addr_to_%s' % i, None)
                  for i in [1, 2, 3]}
        return [email for email in emails if len(email)]


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
                                   related_name='helpdesk_tipologies')
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
                url=reverse(admin_urlname(self.category._meta, 'changelist')),
                category=self.category))
    admin_category.allow_tags = True
    admin_category.admin_order_field = 'category'
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


@python_2_unicode_compatible
class Ticket(SiteRelated, TimeStamped, StatusModel):
    STATUS = Choices(*TICKET_STATUSES)
    content = models.TextField(_("Content"))
    tipologies = models.ManyToManyField(
        'Tipology', verbose_name=_('Tipologies'),
        help_text=_("You can select a maximum of %(max)s %(tipologies)s"
                    ".") % {'max': settings.HELPDESK_MAX_TIPOLOGIES_FOR_TICKET,
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

    def __str__(self):
        return str(self.pk)

    def save(self, update_site=False, *args, **kwargs):
        if not self.id and not self.insert_by_id:
            self.insert_by_id = self.requester_id
        super(Ticket, self).save(update_site, *args, **kwargs)

    def get_clean_content(self, words=10):
        """
        Return self.content with html tags stripped and truncate after a
        "words" number of words with use of django template filter
        'truncatewords'.

        :param words: Number of words to truncate after
        """
        return truncatewords(strip_tags(self.content), words)

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


ACTIONS_ON_TICKET_CHOICES = tuple((k, ACTIONS_ON_TICKET[k])
                                  for k in ACTIONS_ON_TICKET)


@python_2_unicode_compatible
class Report(Message):
    action_on_ticket = models.CharField(max_length=50,
                                        choices=ACTIONS_ON_TICKET_CHOICES,
                                        default=DEFAULT_ACTIONS[0])
    visible_from_requester = models.BooleanField(default=False)

    class Meta:
        get_latest_by = 'created'
        ordering = ('created',)
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')

    def __str__(self):
        return self.content


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
                                      blank=True, null=True,
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
