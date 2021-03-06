from django.apps import apps
from django.db import models

from .exceptions import LinkedMerchantDoesNotExist, UnsupportedLinksError

LINKS_MODELS = {
    'mandate': 'Mandate',
    'customer': 'Customer',
    'customer_bank_account': 'CustomerBankAccount',
    'previous_customer_bank_account': 'CustomerBankAccount',
    'new_customer_bank_account': 'CustomerBankAccount',
    'organisation': {
        'model': 'Merchant',
        'id_field': 'organisation_id',
    },
    'payment': 'Payment',
    'subscription': 'Subscription',
    'payout': 'Payout',
    'refund': 'Refund',
}


def model_from_links(links, attr, client=None):
    if attr not in LINKS_MODELS:
        raise UnsupportedLinksError(
            '{attr} is not a supported links model.'.format(
                attr=attr
            )
        )

    merchant = None
    if client is None:
        organisation = None
        if not isinstance(links, dict):
            organisation = links.organisation
        else:
            organisation = links.get('organisation')
        if organisation is not None:
            from .models import Merchant
            try:
                merchant = Merchant.objects.get(
                    organisation_id=organisation
                )
            except Merchant.DoesNotExist:
                raise LinkedMerchantDoesNotExist(
                    'Organisation {organisation}'.format(
                        organisation=organisation
                    )
                )

    identifier = links[attr] if type(links) is dict else getattr(links, attr)
    argument_model = LINKS_MODELS[attr]

    if isinstance(argument_model, dict):
        model_name = argument_model['model']
        where = {
            argument_model['id_field']: identifier
        }
    else:
        model_name = argument_model
        where = {
            'id': identifier
        }

    model_instance = None
    if identifier is not None:
        model = apps.get_model('django_gocardless', model_name)
        try:
            model_instance = model.objects.get(
                **where
            )
        except model.DoesNotExist:
            if merchant is not None:
                client = model.client_from_settings(
                    access_token=merchant.access_token
                )
            model_instance = model.fetch(
                instance=None,
                where=where,
                client=client
            )

    return model_instance


def field_default(field):
    cls = field.__class__

    default = getattr(field, 'default', None)
    default = None if default is models.NOT_PROVIDED else default

    if (default is None and
        (issubclass(cls, models.CharField) or
         issubclass(cls, models.TextField))):
        return ''
    return default
