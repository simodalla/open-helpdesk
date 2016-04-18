import pytest

from openhelpdesk.ldap_backends import OpenHelpdeskLDAPBackend

from .factories import UserFactory, GroupFactory


@pytest.fixture
def ohldapbackend():
    return OpenHelpdeskLDAPBackend()


@pytest.fixture
def ldap_user():
    class _LDAPUser:
        def __init__(self):
            self.group_names = set()
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

@pytest.mark.parametrize("p_create,p_check, expected", [
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
        'requesters')
    monkeypatch.setattr(
        'openhelpdesk.ldap_backends.MezzanineLDAPBackend.get_or_create_user',
        lambda s, u, v: (fuser, p_create))
    monkeypatch.setattr(
        'openhelpdesk.ldap_backends.OpenHelpdeskLDAPBackend.check_validity_operator',
        lambda s, lu: p_check)
    user, create = ohldapbackend.get_or_create_user('foo', ldap_user)
    assert user.pk == fuser.pk
    assert create == p_create
    print("## ", fgroup, user.groups.all(), expected)
    assert (fgroup in user.groups.all()) is expected
    # print("-->", user, create)
