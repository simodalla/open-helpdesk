from unittest.mock import patch
import pytest

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group

from openhelpdesk.ldap_backends import OpenHelpdeskLDAPBackend

from .factories import UserFactory, GroupFactory


backend_module = 'openhelpdesk.ldap_backends.'


@pytest.fixture
def ohldapbackend():
    return OpenHelpdeskLDAPBackend()


@pytest.fixture
def ldap_user():
    class _LDAPUser:
        def __init__(self):
            self.group_names = set()
            self.attrs = {'foo': ['bar']}
            self.dn = 'cn=foo,dn=exmpla.com'
            self.group_dns = {'foo', 'bar'}
    return _LDAPUser()


@pytest.mark.parametrize("ldap_groups,group_names,expected", [
    (['foo'], set(), False),
    (list(), set(), False),
    (list(), {'foo'}, False),
    (['foo'], {'foo'}, True),
    (['FOO'], {'foo'}, True),
    (['FOO'], {'FOO'}, True),
    (['domain admins'], {'domain Admins'}, True),
    (['domain'], {'domain admins'}, False),
    (['foo', 'bar'], {'xxx', 'yyy'}, False),
    (['foo', 'bar'], {'foo', 'yyy'}, True),
    (['foo', 'bar'], {'foo', 'bar'}, True),
])
def test_check_validitt_group(ldap_groups, group_names, expected,
                              ohldapbackend, ldap_user):
    ldap_user.group_names = group_names
    result = ohldapbackend._check_validity_group(ldap_groups, ldap_user)
    assert result is expected


@pytest.mark.parametrize("setting_groups,group_names,expected", [
    ('foo', set(), False),
    ('', set(), False),
    ('', {'foo'}, False),
    ('foo', {'foo'}, True),
    ('FOO', {'foo'}, True),
    ('FOO', {'FOO'}, True),
    ('domain admins', {'domain Admins'}, True),
    ('domain', {'domain admins'}, False),
    ('foo,bar', {'xxx', 'yyy'}, False),
    ('foo,bar', {'foo', 'yyy'}, True),
    ('foo,bar', {'foo', 'bar'}, True),
    (' foo,bar', {'foo', 'bar'}, True),
    ('foo, bar', {'foo', 'bar'}, True),
    ('foo,  bar  ', {'foo', 'bar'}, True),
    ('  foo,  bar  ', {'foo', 'bar'}, True),
])
@pytest.mark.django_db
def test_check_validity_for_requesters(
        setting_groups, group_names, expected, monkeypatch, ohldapbackend):
    monkeypatch.setattr(
        "mezzanine.conf.settings.OPENHELPDESK_LDAP_REQUESTER_GROUPS",
        setting_groups)
    ldap_user.group_names = group_names
    result = ohldapbackend._check_validity_group(
        ohldapbackend.ldap_requester_groups, ldap_user)
    assert result is expected


@pytest.mark.parametrize("setting_groups,group_names,expected", [
    ('foo', set(), False),
    ('', set(), False),
    ('', {'foo'}, False),
    ('foo', {'foo'}, True),
    ('FOO', {'foo'}, True),
    ('FOO', {'FOO'}, True),
    ('domain admins', {'domain Admins'}, True),
    ('domain', {'domain admins'}, False),
    ('foo,bar', {'xxx', 'yyy'}, False),
    ('foo,bar', {'foo', 'yyy'}, True),
    ('foo,bar', {'foo', 'bar'}, True),
    (' foo,bar', {'foo', 'bar'}, True),
    ('foo, bar', {'foo', 'bar'}, True),
    ('foo,  bar  ', {'foo', 'bar'}, True),
    ('  foo,  bar  ', {'foo', 'bar'}, True),
])
@pytest.mark.django_db
def test_check_validity_for_operators(
        setting_groups, group_names, expected, monkeypatch, ohldapbackend):
    monkeypatch.setattr(
        'mezzanine.conf.settings.OPENHELPDESK_LDAP_OPERATOR_GROUPS',
        setting_groups)
    ldap_user.group_names = group_names
    result = ohldapbackend._check_validity_group(
        ohldapbackend.ldap_operator_groups, ldap_user)
    assert result is expected


@pytest.mark.parametrize("p_create,p_check,expected", [
    (False, None, False),
    (True, False, False),
    (True, True, True),
])
@pytest.mark.django_db
def test_ldap_new_login_with_a_future_operator(
        p_create, p_check, expected, monkeypatch, ohldapbackend, ldap_user):
    fuser = UserFactory()
    fgroup = GroupFactory(name='operators')
    monkeypatch.setattr(
        "mezzanine.conf.settings.HELPDESK_OPERATORS",
        'operators')
    monkeypatch.setattr(
        '%sMezzanineLDAPBackend.get_or_create_user' % backend_module,
        lambda s, u, v: (fuser, p_create))
    monkeypatch.setattr(
        '%sOpenHelpdeskLDAPBackend.check_validity_operator' % backend_module,
        lambda s, lu: p_check)
    user, create = ohldapbackend.get_or_create_user('foo', ldap_user)
    assert user.pk == fuser.pk
    assert create == p_create
    assert (fgroup in user.groups.all()) is expected


@pytest.mark.parametrize("p_create,p_check,expected", [
    (False, None, False),
    (True, False, False),
    (True, True, True),
])
@pytest.mark.django_db
def test_ldap_new_login_with_a_future_requester(
        p_create, p_check, expected, monkeypatch, ohldapbackend, ldap_user):
    group_name = 'requesters'
    fuser = UserFactory()
    fgroup = GroupFactory(name=group_name)
    monkeypatch.setattr(
        "mezzanine.conf.settings.HELPDESK_{}".format(group_name.upper()),
        group_name)
    monkeypatch.setattr(
        '%sMezzanineLDAPBackend.get_or_create_user' % backend_module,
        lambda s, u, v: (fuser, p_create))
    monkeypatch.setattr(
        '%sOpenHelpdeskLDAPBackend.check_validity_requester' % backend_module,
        lambda s, lu: p_check)
    user, create = ohldapbackend.get_or_create_user('foo', ldap_user)
    assert user.pk == fuser.pk
    assert create == p_create
    assert (fgroup in user.groups.all()) is expected


@patch('%sGroup.objects.get' % backend_module, side_effect=Group.DoesNotExist)
@pytest.mark.django_db
def test_ldap_new_login_with_adding_group_raise_dne_exception(
        mock_get, monkeypatch, ohldapbackend, ldap_user):
    monkeypatch.setattr(
        '%sMezzanineLDAPBackend.get_or_create_user' % backend_module,
        lambda s, u, v: (UserFactory(), True))
    monkeypatch.setattr(
        '%sOpenHelpdeskLDAPBackend.check_validity_operator' % backend_module,
        lambda s, lu: True)
    with patch('%slogger' % backend_module) as mock_logger:
        ohldapbackend.get_or_create_user('foo', ldap_user)
        mock_logger.exception.assert_called_once_with(
            "Openhelpdeks groups error into OpenHelpdeskLDAPBackend")


@patch('%sGroup.objects.get' % backend_module, side_effect=KeyError)
@pytest.mark.django_db
def test_ldap_new_login_with_adding_group_raise_generic_exception(
        mock_get, monkeypatch, ohldapbackend, ldap_user):
    monkeypatch.setattr(
        '%sMezzanineLDAPBackend.get_or_create_user' % backend_module,
        lambda s, u, v: (UserFactory(), True))
    monkeypatch.setattr(
        '%sOpenHelpdeskLDAPBackend.check_validity_operator' % backend_module,
        lambda s, lu: True)
    with patch('%slogger' % backend_module,
               autospec=True) as mock_logger:
        ohldapbackend.get_or_create_user('foo', ldap_user)
        mock_logger.exception.assert_called_once_with(
            "Generic error into OpenHelpdeskLDAPBackend", exc_info=True)


@pytest.mark.django_db
def test_ldap_new_login_with_a_group_added_send_a_report_by_mail(
        monkeypatch, ohldapbackend, ldap_user):
    group_name = 'requesters'
    fuser = UserFactory()
    monkeypatch.setattr(
        "mezzanine.conf.settings.HELPDESK_{}".format(group_name.upper()),
        group_name)
    monkeypatch.setattr(
        '%sMezzanineLDAPBackend.get_or_create_user' % backend_module,
        lambda s, u, v: (fuser, True))
    monkeypatch.setattr(
        '%sOpenHelpdeskLDAPBackend.check_validity_requester' % backend_module,
        lambda s, lu: True)
    with patch('%sOpenHelpdeskLDAPBackend.send_email_report' % backend_module
               ) as mock_ser:
        user, create = ohldapbackend.get_or_create_user('foo', ldap_user)
        mock_ser.assert_called_once_with(user, ldap_user)
    assert user.pk == fuser.pk


@pytest.mark.django_db
def test_send_email_report():
    assert pytest.xfail()
