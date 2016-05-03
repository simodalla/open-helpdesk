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
        'managers-autocomplete/$',
        views.ManagersAutocomplete.as_view(),
        name='managers-autocomplete',
    ),
]
