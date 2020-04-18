from django.core.mail import EmailMessage
from django.core.mail.backends.base import BaseEmailBackend
from django.db import models


class Recipient(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


class Email(models.Model):
    class Status(models.TextChoices):
        PENDING = 'Pending'
        SENT = 'Sent'
        FAILED_SENDING = 'Failed Sending'

    status = models.CharField(
        max_length=256,
        choices=Status.choices,
        default=Status.PENDING
    )
    recipients = models.ManyToManyField(
        Recipient,
        related_name='+'
    )
    sender = models.ForeignKey(
        Recipient,
        on_delete=models.PROTECT,
        related_name='emails_sent'
    )
    subject = models.TextField(blank=True)
    body = models.TextField(blank=True)
    priority = models.IntegerField(null=True)
    attachment = models.FileField()

    def __str__(self):
        return self.subject

    @property
    def has_attachment(self):
        return bool(self.attachment)

    @classmethod
    def get_pending_emails(cls):
        return cls.objects.filter(status=cls.Status.PENDING)

    def get_headers(self):
        header_fields = {
            'X-Priority': self.priority
        }
        return dict(filter(lambda item: item[1], header_fields.items()))

    def send(self, connection: BaseEmailBackend) -> bool:
        message = EmailMessage(
            subject=self.subject,
            body=self.body,
            from_email=self.sender.email,
            to=self.recipients.values_list('email', flat=True),
            headers=self.get_headers(),
            connection=connection
        )
        if self.attachment:
            message.attach(filename=self.attachment.name, content=self.attachment.read())

        return message.send()
