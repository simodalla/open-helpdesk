from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        'requester-autocomplete/$',
        views.RequesterAutocomplete.as_view(),
        name='requester-autocomplete',
    ),
    url(
        'ticket-autocomplete/$',
        views.TicketAutocomplete.as_view(),
        name='ticket-autocomplete',
    ),
    url(
        'manager-autocomplete/$',
        views.ManagersAutocomplete.as_view(),
        name='manager-autocomplete',
    ),
    url(
        'organization-autocomplete/$',
        views.OrganizationSettingAutocomplete.as_view(),
        name='organization-autocomplete',
    ),
    url(
        'site-autocomplete/$',
        views.SitesSettingAutocomplete.as_view(),
        name='site-autocomplete',
    ),
    url(
        'category-autocomplete/$',
        views.CategoryAutocomplete.as_view(),
        name='category-autocomplete',
    ),
    url(
        'subteam-autocomplete/$',
        views.SubteamAutocomplete.as_view(),
        name='subteam-autocomplete',
    ),
]
