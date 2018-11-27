# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.template.loader import select_template
from django.utils.translation import get_language_from_request
from cms.models.pagemodel import Page
from rest_framework.serializers import CharField
from rest_auth import serializers
from shop.conf import app_settings
from shop.forms.auth import PasswordResetRequestForm


class PasswordResetRequestSerializer(serializers.PasswordResetSerializer):
    password_reset_form_class = PasswordResetRequestForm

    def save(self):
        subject_template = select_template([
            '{}/email/password-reset-subject.txt'.format(app_settings.APP_LABEL),
            'shop/email/password-reset-subject.txt',
        ])
        body_text_template = select_template([
            '{}/email/password-reset-body.txt'.format(app_settings.APP_LABEL),
            'shop/email/password-reset-body.txt',
        ])
        body_html_template = select_template([
            '{}/email/password-reset-body.html'.format(app_settings.APP_LABEL),
            'shop/email/password-reset-body.html',
        ])
        try:
            page = Page.objects.select_related('node').get(reverse_id='password-reset-confirm', publisher_is_draft=False)
        except Page.DoesNotExist:
            pass
        else:
            language = get_language_from_request(self.context['request'])
            extra_email_context = {
                'password_reset_confirm_url': page.get_absolute_url(language)
            }
        opts = {
            'use_https': self.context['request'].is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': self.context['request'],
            'subject_template_name': subject_template.template.name,
            'email_template_name': body_text_template.template.name,
            'html_email_template_name': body_html_template.template.name,
            'extra_email_context': extra_email_context,
        }
        self.reset_form.save(**opts)


class PasswordResetConfirmSerializer(serializers.PasswordResetConfirmSerializer):
    new_password1 = CharField(min_length=6, max_length=128)
    new_password2 = CharField(min_length=6, max_length=128)
