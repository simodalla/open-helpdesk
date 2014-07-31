# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import pytest
from django.template import Context

from openhelpdesk.templatetags.helpdesk_tags import format_ticket_message
from openhelpdesk.models import Message, Report


@pytest.fixture
def message():
    obj = Message()
    return obj


@pytest.fixture
def report(operator):
    obj = Report()
    obj.content = "bla"
    obj.sender = operator
    obj.save()
    return Message.objects.get(pk=obj.pk)


class TestFormatTicketTag(object):

    def test_format_ticket_raise_exception_if_not_message_subclass(self):
        """
        Test that format_ticket_message is called with an object that not an
        Message or a subclass of object class, raise an ValueError eception
        """
        class Foo(object):
            pass
        with pytest.raises(TypeError):
            format_ticket_message(Context({}), Foo())

    def test_keys_item_in_dict_returned(self, message):
        assert ({'css_style', 'message', 'css_class', 'model',
                 'can_view_report'} ==
                set(format_ticket_message(Context({}), Message()).keys()))

    def test_message_item_in_dict_returned(self, message):
        context = format_ticket_message(Context({}), Message())
        assert 'message' in context.keys()
        assert context['message'] == message

    def test_model_item_in_dict_returned(self, message):
        context = format_ticket_message(Context({}), Message())
        assert 'model' in context.keys()
        assert context['model'] == getattr(
            message._meta, 'model_name', message._meta.module_name)

    def test_css_style_item_in_dict_returned(self, message):
        context = format_ticket_message(Context({}), message)
        assert 'css_style' in context.keys()
        assert context['css_style'] == ''

    @pytest.mark.django_db
    def test_css_style_item_in_dict_returned_and_setted_if_report_obj(
            self, report):
        context = format_ticket_message(Context({}), report)
        assert 'css_style' in context.keys()
        assert 'text-align: right' in context['css_style']

    @pytest.mark.django_db
    def test_report_model_item_in_dict_returned(self, report):
        context = format_ticket_message(Context({}), report)
        assert 'model' in context.keys()
        assert context['model'] == getattr(
            Report._meta, 'model_name', Report._meta.module_name)

    def test_css_class_item_in_dict_returned_and_default_value(self, message):
        context = format_ticket_message(Context({}), message)
        assert 'css_class' in context.keys()
        assert context['css_class'] == 'form-row'

    def test_css_class_item_in_dict_returned_and_update_if_is_kwargs(
            self, message):
        context = format_ticket_message(Context({}), message, css_class='foo')
        assert 'css_class' in context.keys()
        assert context['css_class'] == 'foo'
