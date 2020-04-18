from smtplib import SMTPException
from typing import List, Iterable, Tuple
from django.core.mail import get_connection, EmailMessage
from django.core.mail.backends.base import BaseEmailBackend
from django.core.validators import validate_email
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField

from api.models import Recipient, Email


class GetOrCreateSlugRelatedField(SlugRelatedField):
    def to_internal_value(self, data):
        try:
            return self.get_queryset().get_or_create(**{self.slug_field: data})[0]
        except (TypeError, ValueError):
            self.fail('invalid')


class EmailSerializer(serializers.ModelSerializer):
    recipients = GetOrCreateSlugRelatedField(
        queryset=Recipient.objects.all(),
        slug_field='email',
        many=True
    )
    sender = GetOrCreateSlugRelatedField(
        queryset=Recipient.objects.all(),
        slug_field='email',
        many=False
    )

    class Meta:
        model = Email
        fields = ('id', 'status', 'recipients', 'sender', 'subject', 'body', 'priority', 'has_attachment')
        read_only_fields = ('status', 'has_attachment')

    def validate_recipients(self, attrs: List[Recipient]):
        for recipient in attrs:
            validate_email(recipient.email)
        return attrs

    def validate_sender(self, recipient: Recipient):
        validate_email(recipient.email)
        return recipient

    def validate_priority(self, value: int):
        if value not in range(1, 6):
            raise ValidationError('Priority has to be in range 1-5')
        return value


class SMTPSerializer(serializers.Serializer):
    host = serializers.CharField()
    port = serializers.IntegerField()
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)

    def create(self, validated_data: dict):
        connection = self.get_smtp_connection(validated_data)
        pending_emails = Email.get_pending_emails()

        sent_email_ids, failed_email_ids = self.send_emails(connection, pending_emails)
        sent_emails = Email.objects.filter(pk__in=sent_email_ids)
        failed_emails = Email.objects.filter(pk__in=failed_email_ids)

        sent_emails.update(status=Email.Status.SENT)
        failed_emails.update(status=Email.Status.FAILED_SENDING)

        connection.close()

        return EmailSerializer(sent_emails.union(failed_emails), many=True).data

    @staticmethod
    def send_emails(connection: BaseEmailBackend, pending_emails: Iterable[Email]) -> Tuple[List[int], List[int]]:
        sent_emails = []
        failed_emails = []
        for email in pending_emails:
            try:
                email.send(connection=connection)
            except SMTPException:
                failed_emails.append(email.id)
            else:
                sent_emails.append(email.id)

        return sent_emails, failed_emails

    @staticmethod
    def get_smtp_connection(connection_data: dict) -> BaseEmailBackend:
        connection = get_connection(
            backend=settings.EMAIL_BACKEND,
            **connection_data
        )
        try:
            connection.open()
        except (SMTPException, OSError):
            raise ValidationError({'connection': ['Failed connecting to SMTP server']})
        else:
            return connection
