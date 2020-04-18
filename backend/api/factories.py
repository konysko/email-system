import factory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText

from api.models import Email, Recipient


class RecipientFactory(DjangoModelFactory):
    class Meta:
        model = Recipient

    email = factory.Sequence(lambda n: f'mail{n}@mail.pl')


class EmailFactory(DjangoModelFactory):
    class Meta:
        model = Email

    subject = FuzzyText(length=84)
    body = FuzzyText(length=256)
    sender = factory.SubFactory(RecipientFactory)
