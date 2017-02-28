import pytest

# from .factories import OrganizationSettingF
from openhelpdesk.models import OrganizationSetting

@pytest.mark.django_db
def test_ticket_fake(requester, new_ticket):
    assert 1==1

    print(OrganizationSetting.objects.all())
    print(new_ticket.organization)

    # os = OrganizationSettingF()
    # print(os.pk, os.email_domain, os.title)
    # os = OrganizationSettingF()
    # print(os.pk, os.email_domain, os.title)
    # os = OrganizationSettingF(email_domain='cocco.it')
    # print(os.pk, os.email_domain, os.title)

