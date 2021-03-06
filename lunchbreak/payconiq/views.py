import json
import logging

from customers.models import Order
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from payconiq.resources import Transaction as TransactionResource
from rest_framework import status

from .models import Transaction
from .utils import is_signature_valid

logger = logging.getLogger('lunchbreak')


class WebhookView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(WebhookView, self).dispatch(*args, **kwargs)

    def is_valid(self, request, merchant_id):
        signature = request.META.get('HTTP_X_SECURITY_SIGNATURE')
        timestamp = request.META.get('HTTP_X_SECURITY_TIMESTAMP')
        key = request.META.get('HTTP_X_SECURITY_KEY')
        algorithm = request.META.get('HTTP_X_SECURITY_ALGORITHM')

        if signature is None \
                or merchant_id is None \
                or timestamp is None \
                or key is None \
                or algorithm is None:
            return False

        return is_signature_valid(
            signature=signature,
            merchant_id=merchant_id,
            timestamp=timestamp,
            algorithm=algorithm,
            body=request.body
        )

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode('utf-8'))

            if not isinstance(data, dict):
                logger.exception(
                    'JSON was not a dictionary.',
                    extra={
                        'request': request,
                        'extra_args': args,
                        'extra_kwargs': kwargs,
                    }
                )
                return HttpResponseBadRequest(
                    'JSON must be a dictionary.'
                )
        except json.JSONDecodeError as e:
            logger.exception(
                'Invalid JSON sent.',
                extra={
                    'request': request,
                    'extra_args': args,
                    'extra_kwargs': kwargs,
                }
            )
            return HttpResponseBadRequest(
                'Invalid JSON: ' + str(e)
            )

        transaction_remote_id = data.get('_id')
        transaction_status = data.get('status')

        if transaction_remote_id is None or transaction_status is None:
            logger.exception(
                'JSON must contain an _id and status key.',
                extra={
                    'request': request,
                    'extra_args': args,
                    'extra_kwargs': kwargs,
                }
            )
            return HttpResponseBadRequest(
                'JSON must contain an _id and status key.'
            )

        order = None
        try:
            transaction = Transaction.objects.select_related(
                'merchant'
            ).get(
                remote_id=transaction_remote_id
            )
            merchant = transaction.merchant
        except Transaction.DoesNotExist:
            webhook_id = request.GET.get('webhookId')
            if webhook_id is not None:
                try:
                    order = get_object_or_404(
                        Order.objects.select_related(
                            'store__staff__payconiq'
                        ),
                        pk=webhook_id
                    )
                except Exception as e:
                    logger.exception(
                        str(e),
                        exc_info=True,
                        extra={
                            'request': request,
                            'extra_args': args,
                            'extra_kwargs': kwargs,
                        }
                    )
                    raise
                merchant = order.store.staff.payconiq
            else:
                logger.exception(
                    'No webhook id provided in Payconiq POST request.',
                    exc_info=True,
                    extra={
                        'request': request,
                        'extra_args': args,
                        'extra_kwargs': kwargs,
                    }
                )
                raise Http404()

        if not self.is_valid(request, merchant.remote_id):
            logger.exception(
                'Invalid request signature used.',
                extra={
                    'request': request,
                    'extra_args': args,
                    'extra_kwargs': kwargs,
                    'merchant.remote_id': merchant.remote_id,
                }
            )
            raise Http404()

        if order is not None:
            transaction_data = TransactionResource.get(
                id=transaction_remote_id,
                merchant_token=merchant.access_token
            )
            transaction = Transaction.objects.create(
                remote_id=transaction_remote_id,
                amount=transaction_data['amount'],
                currency=transaction_data['currency'],
                merchant=merchant
            )
            order.transaction = transaction
            order.save()
            # This is separated in order to trigger transaction_succeeded signal
            # Order.transaction_succeeded also needs the order to already be
            # linked to an existing transaction.
            transaction.status = transaction_status
            transaction.save()
        else:
            transaction.status = transaction_status
            transaction.save()

        return HttpResponse(
            status=status.HTTP_200_OK
        )
