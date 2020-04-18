from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from api.factories import RecipientFactory, EmailFactory
from api.models import Email


class EmailGetViewSetTestCase(APITestCase):
    def test_should_list_all_email_in_the_system(self):
        emails = EmailFactory.create_batch(3)
        recipients = RecipientFactory.create_batch(2)
        emails[0].recipients.add(*recipients)
        emails[1].recipients.add(RecipientFactory())

        url = reverse('email-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_response = [
            self.transform_email(email)
            for email in emails
        ]
        self.assertListEqual(response.json(), expected_response)

    def test_should_retrieve_detail_of_email(self):
        email = EmailFactory()
        email.recipients.add(RecipientFactory())

        url = reverse('email-detail', args=[email.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_response = self.transform_email(email)
        self.assertDictEqual(response.json(), expected_response)

    def test_should_raise_404_if_email_doesnt_exist(self):
        url = reverse('email-detail', args=[33])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @staticmethod
    def transform_email(email: Email):
        return {
            'id': email.id,
            'status': str(email.status),
            'recipients': list(email.recipients.values_list('email', flat=True)),
            'sender': email.sender.email,
            'subject': email.subject,
            'body': email.body,
            'priority': email.priority,
            'has_attachment': email.has_attachment
        }
