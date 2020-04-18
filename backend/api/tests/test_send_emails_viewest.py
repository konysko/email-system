from io import BytesIO
from unittest.mock import patch, Mock
from django.core import mail
from django.core.mail import EmailMessage
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.factories import EmailFactory, RecipientFactory
from api.models import Email
from api.tests.test_get_emails_viewset import EmailGetViewSetTestCase


class SendEmailViewSetTestCase(APITestCase):
    def test_should_send_pending_emails(self):
        recipient = RecipientFactory()
        pending_emails = EmailFactory.create_batch(3)
        EmailFactory(status=Email.Status.SENT)
        for email in pending_emails:
            email.recipients.add(recipient)
        payload = {
            'host': 'testhost',
            'port': 66,
            'username': 'testusername',
            'password': 'testpassword'
        }

        url = reverse('email-send')
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_sent_mails = Email.objects.filter(pk__in=map(lambda n: n.pk, pending_emails))
        expected_response = [
            EmailGetViewSetTestCase.transform_email(email)
            for email in expected_sent_mails
        ]
        self.assertListEqual(response.json(), expected_response)

        for sent_email, expected_mail in zip(mail.outbox, expected_sent_mails):
            self.assertMailEqual(sent_email, expected_mail)

    @patch('api.serializers.get_connection')
    def test_should_raise_if_wrong_smtp_data(self, get_connection_mock):
        EmailFactory()
        payload = {
            'host': 'testhost',
            'port': 66,
            'username': 'testusername',
            'password': 'testpassword'
        }
        connection_mock = Mock()
        connection_mock.open.side_effect = OSError()
        get_connection_mock.return_value = connection_mock

        url = reverse('email-send')
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'connection': ['Failed connecting to SMTP server']})

    def test_should_send_email_with_attachment(self):
        recipient = RecipientFactory()
        pending_email = EmailFactory(attachment=BytesIO(b'somebinaryattachment'))
        pending_email.recipients.add(recipient)
        payload = {
            'host': 'testhost',
            'port': 66,
            'username': 'testusername',
            'password': 'testpassword'
        }

        url = reverse('email-send')
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        pending_email.refresh_from_db()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].attachments), 1)

    def test_should_send_email_with_priority(self):
        recipient = RecipientFactory()
        pending_email = EmailFactory(priority=3)
        pending_email.recipients.add(recipient)
        payload = {
            'host': 'testhost',
            'port': 66,
            'username': 'testusername',
            'password': 'testpassword'
        }

        url = reverse('email-send')
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        pending_email.refresh_from_db()
        expected_response = [EmailGetViewSetTestCase.transform_email(pending_email)]
        self.assertListEqual(response.json(), expected_response)

        self.assertEqual(len(mail.outbox), 1)
        self.assertMailEqual(mail.outbox[0], pending_email)

    def assertMailEqual(self, email: EmailMessage, expected_email: Email):
        self.assertEqual(email.subject, expected_email.subject)
        self.assertEqual(email.body, expected_email.body)
        self.assertEqual(email.from_email, expected_email.sender.email)
        self.assertEqual(email.extra_headers, expected_email.get_headers())
        self.assertEqual(email.to, list(expected_email.recipients.values_list('email', flat=True)))
