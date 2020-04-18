from django.test import TestCase

from api.factories import EmailFactory
from api.models import Email


class EmailModelTestCase(TestCase):
    def test_should_filter_by_pending_emails(self):
        EmailFactory(status=Email.Status.SENT)
        EmailFactory(status=Email.Status.FAILED_SENDING)
        expected_pending_emails = EmailFactory.create_batch(5)

        pending_emails = Email.get_pending_emails()

        self.assertListEqual(
            list(pending_emails.values_list('pk', flat=True)),
            list(map(lambda n: n.pk, expected_pending_emails))
        )

    def test_should_get_nonempty_headers(self):
        email = EmailFactory()

        self.assertFalse(email.get_headers())

        priority = 1
        email.priority = priority
        email.save()

        headers = email.get_headers()

        self.assertEqual(headers.get('X-Priority'), priority)
