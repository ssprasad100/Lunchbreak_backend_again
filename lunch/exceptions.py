from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework import status

from opbeat.contrib.django.models import logger


LUNCH_MESSAGING_UNAVAILABLE = 501
LUNCH_SERVICE_UNAVAILABLE = 503

LUNCH_BAD_REQUEST = 400
LUNCH_ADDRESS_NOT_FOUND = 401
LUNCH_DOES_NOT_EXIST = 402
LUNCH_COSTCHECK_FAILED = 403

LUNCH_AUTHENTICATION_FAILED = 300

DIGITS_LEGACY_ERROR = 0
DIGITS_INVALID_PHONE = 32
DIGITS_APP_AUTH_ERROR = 89
DIGITS_GUEST_AUTH_ERROR = 239
DIGITS_PIN_INCORRECT = 236
DIGITS_ALREADY_REGISTERED_ERROR = 285

DIGITS_EXCEPTIONS = {
	DIGITS_LEGACY_ERROR: 'Digits legacy error.',
	DIGITS_INVALID_PHONE: ['Digits invalid phone number.', status.HTTP_400_BAD_REQUEST],
	DIGITS_APP_AUTH_ERROR: 'Digits app authorization failed.',
	DIGITS_GUEST_AUTH_ERROR: 'Digits guest authorization failed.',
	DIGITS_PIN_INCORRECT: ['Incorrect pin.', status.HTTP_400_BAD_REQUEST],
	DIGITS_ALREADY_REGISTERED_ERROR: 'User already in the Digits database.'
}


def lunchbreakExceptionHandler(exception):
	response = Response()
	response.data = {'error': {}}
	if exception is None:
		return response

	hasDetail = hasattr(exception, 'detail') and exception.detail is not None
	response.data['error']['code'] = exception.code if hasattr(exception, 'code') else -1
	if hasattr(exception, 'information'):
		response.data['error']['information'] = exception.information
		if hasDetail:
			response.data['error']['detail'] = exception.detail
	elif hasDetail:
		response.data['error']['information'] = exception.detail
	else:
		# DEBUG ONLY
		raise

	response.status_code = exception.status_code if hasattr(exception, 'status_code') else status.HTTP_400_BAD_REQUEST
	return response


class LunchbreakException(APIException):

	def __init__(self, detail=None):
		if detail is None:
			super(LunchbreakException, self).__init__()
			self.detail = None
		elif not isinstance(detail, basestring):
			super(LunchbreakException, self).__init__()
			self.detail = detail
		else:
			super(LunchbreakException, self).__init__(detail)


class ServiceUnavailable(LunchbreakException):
	status_code = status.HTTP_503_SERVICE_UNAVAILABLE
	code = LUNCH_SERVICE_UNAVAILABLE
	information = 'Service temporarily unavailable.'


class DigitsException(LunchbreakException):
	status_code = status.HTTP_503_SERVICE_UNAVAILABLE
	code = LUNCH_MESSAGING_UNAVAILABLE
	information = 'Messaging service temporarily unavailable.'

	def __init__(self, code, content):
		detail = None
		if code in DIGITS_EXCEPTIONS:
			info = DIGITS_EXCEPTIONS[code]
			if type(info) is list:
				detail = info[0]
				self.status_code = info[1]
			else:
				detail = info
		else:
			logger.exception('Undocumented Digits exception: %s' % content)
		self.code = code
		super(DigitsException, self).__init__(detail)


class BadRequest(LunchbreakException):
	status_code = status.HTTP_400_BAD_REQUEST
	code = LUNCH_BAD_REQUEST
	information = 'Bad request.'


class AddressNotFound(LunchbreakException):
	status_code = status.HTTP_400_BAD_REQUEST
	code = LUNCH_ADDRESS_NOT_FOUND
	information = 'The address given could not be found.'


class DoesNotExist(LunchbreakException):
	status_code = status.HTTP_400_BAD_REQUEST
	code = LUNCH_DOES_NOT_EXIST
	information = 'Object does not exist.'


class AuthenticationFailed(LunchbreakException):
	status_code = status.HTTP_401_UNAUTHORIZED
	code = LUNCH_AUTHENTICATION_FAILED
	information = 'User authentication failed.'


class CostCheckFailed(LunchbreakException):
	status_code = status.HTTP_409_CONFLICT
	code = LUNCH_COSTCHECK_FAILED
	information = 'Cost check failed.'
