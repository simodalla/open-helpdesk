# -*- coding: utf-8 -*-

from django import test
from django.contrib.auth.models import AnonymousUser
from django.core.serializers.json import DjangoJSONEncoder

try:
    from unittest.mock import patch, Mock, call
except ImportError:
    from mock import patch, Mock, call


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
