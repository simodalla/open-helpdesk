from django.conf.urls import url

from .views import RequesterAutocomplete, TicketAutocomplete


urlpatterns = [
    url(
        'requester-autocomplete/$',
        RequesterAutocomplete.as_view(),
        name='requester-autocomplete',
    ),
    url(
        'ticket-autocomplete/$',
        TicketAutocomplete.as_view(),
        name='ticket-autocomplete',
    ),
]
