# -*- coding: utf-8 -*-

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from django import test
from django.contrib.auth.models import AnonymousUser
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.contrib.admin.templatetags.admin_urls import admin_urlname


def to_list(value):
    """
    Puts value into a list if it's not already one.
    Returns an empty list if value is None.
    """
    if value is None:
        value = []
    elif not isinstance(value, list):
        value = [value]
    return value


class AdminTestMixin(object):

    def get_url(self, model, viewname, *args, **kwargs):
        return reverse(admin_urlname(model._meta, viewname), *args, **kwargs)

    def get_admin_form_error(self, response):
        return response.context['adminform'].form

    def assertAdminFormError(self, response, field, errors, msg_prefix=''):
        if msg_prefix:
            msg_prefix += ": "
        form = self.get_admin_form_error(response)
        # Put error(s) into a list to simplify processing.
        errors = to_list(errors)
        for err in errors:
            if field:
                if field in form.errors:
                    field_errors = form.errors[field]
                    self.assertTrue(err in field_errors,
                                    msg_prefix + "The field '%s' on form '%s'"
                                                 " does not contain the error"
                                                 " '%s' (actual errors: %s)" %
                                    (field, form, err, repr(field_errors)))
                elif field in form.fields:
                    self.fail(msg_prefix + "The field '%s' on form '%s'"
                                           "contains no errors" % (field,
                                                                   form))
                else:
                    self.fail(msg_prefix + "The form '%s' does not contain the"
                                           " field '%s'" % (form, field))
            else:
                non_field_errors = form.non_field_errors()
                self.assertTrue(err in non_field_errors,
                                msg_prefix + "The form '%s' does not"
                                             " contain the non-field error "
                                             " '%s' (actual errors: %s)" %
                                (form, err, non_field_errors))


def get_mock_helpdeskuser(requester=False, operator=False, admin=False,
                          superuser=False):
    mock_helpdesk_user = Mock()
    mock_helpdesk_user.is_superuser = superuser
    mock_helpdesk_user.is_requester.return_value = requester
    mock_helpdesk_user.is_operator.return_value = operator
    mock_helpdesk_user.is_admin.return_value = admin
    return mock_helpdesk_user


def get_mock_request(user_pk=1):
    request_mock = Mock(user=Mock(pk=user_pk))
    return request_mock


class TestViewHelper(object):
    """
    Helper class for unit-testing class based views.
    """
    view_class = None
    request_factory_class = test.RequestFactory

    def setUp(self):
        super(TestViewHelper, self).setUp()
        self.factory = self.request_factory_class()

    def build_request(self, method='GET', path='/test/', user=None, **kwargs):
        """
        Creates a request using request factory.
        """
        fn = getattr(self.factory, method.lower())
        if user is None:
            user = AnonymousUser()

        req = fn(path, **kwargs)
        req.user = user
        return req

    def build_view(self, request, args=None, kwargs=None, view_class=None,
                   **viewkwargs):
        """
        Creates a `view_class` view instance.
        """
        if not args:
            args = ()
        if not kwargs:
            kwargs = {}
        if view_class is None:
            view_class = self.view_class

        return view_class(
            request=request, args=args, kwargs=kwargs, **viewkwargs)

    def dispatch_view(self, request, args=None, kwargs=None, view_class=None,
                      **viewkwargs):
        """
        Creates and dispatches `view_class` view.
        """
        view = self.build_view(request, args, kwargs, view_class, **viewkwargs)
        return view.dispatch(request, *view.args, **view.kwargs)


class SetJSONEncoder(DjangoJSONEncoder):
    """
    A custom JSONEncoder extending `DjangoJSONEncoder` to handle serialization
    of `set`.
    """
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return super(DjangoJSONEncoder, self).default(obj)
