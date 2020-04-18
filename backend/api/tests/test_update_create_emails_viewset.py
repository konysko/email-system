from io import BytesIO

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from api.factories import EmailFactory, RecipientFactory
from api.models import Email


class EmailCreateUpdateViewSetTestCase(APITestCase):
    def test_should_create_email(self):
        payload = {
            'recipients': ['mail@test.pl'],
            'sender': 'iamsender@test.pl',
            'subject': 'testsubject',
            'priority': 4
        }

        url = reverse('email-list')
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_email = Email.objects.get(pk=response.json()['id'])

        self.assertEqual(list(created_email.recipients.values_list('email', flat=True)), payload['recipients'])
        self.assertEqual(created_email.sender.email, payload['sender'])
        self.assertEqual(created_email.subject, payload['subject'])
        self.assertEqual(created_email.priority, payload['priority'])

    def test_should_get_existing_recipient_during_update_if_it_exist(self):
        email = EmailFactory()
        sender = RecipientFactory()
        recipient = RecipientFactory()
        payload = {
            'recipients': [recipient.email],
            'sender': sender.email
        }

        url = reverse('email-detail', args=[email.pk])
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        email.refresh_from_db()
        self.assertEqual(email.sender.pk, sender.pk)
        self.assertEqual(email.recipients.count(), 1)
        self.assertEqual(email.recipients.all()[0].pk, recipient.pk)

    def test_should_raise_if_wrong_mail_format_of_sender(self):
        payload = {
            'sender': 'wrongmail'
        }

        url = reverse('email-list')
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'sender': ['Enter a valid email address.']})

    def test_should_raise_if_wrong_mail_format_of_recipient(self):
        payload = {
            'sender': 'test@test.pl',
            'recipients': ['wrongmail']
        }

        url = reverse('email-list')
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'recipients': ['Enter a valid email address.']})

    def test_should_raise_if_priority_not_in_range(self):
        email = EmailFactory()
        payload = {
            'priority': 6
        }

        url = reverse('email-detail', args=[email.pk])
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'priority': ['Priority has to be in range 1-5']})

    def test_should_add_attachment_to_email(self):
        email = EmailFactory()
        binary_data = BytesIO(b'somebinaryattachment')

        url = reverse('email-add-attachment', args=[email.pk])
        response = self.client.put(url, binary_data)

        self.assertEqual(response.status_code, 200)
        email.referesh_from_db()
        self.assertEqual(email.attachment, binary_data)
