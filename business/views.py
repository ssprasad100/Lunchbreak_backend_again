from business.authentication import StaffAuthentication
from business.exceptions import InvalidEmail
from business.models import Employee, Staff
from business.serializers import EmployeeSerializer, StaffSerializer
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import send_mail, BadHeaderError
from django.core.validators import validate_email
from lunch.models import tokenGenerator
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from lunch.exceptions import BadRequest


class StaffListView(generics.ListAPIView):
    '''
    List the staff.
    '''

    serializer_class = StaffSerializer

    def get_queryset(self):
        if 'id' in self.kwargs:
            return Staff.objects.filter(id=self.kwargs['id'])
        return Staff.objects.all()


class StaffRequestReset(APIView):
    '''
    Send password reset mail.
    '''

    def get(self, request, email, format=None):
        try:
            validate_email(email)
        except ValidationError:
            raise InvalidEmail()

        try:
            staff = Staff.objects.get(email=email)
        except ObjectDoesNotExist:
            raise InvalidEmail('Email address not found.')

        staff.passwordReset = tokenGenerator()
        staff.save()
        url = 'http://api.lunchbreakapp.be/v1/business/reset/%s/%s' % (email, staff.passwordReset,)

        message = '''A password reset has been requested for this staff account.

Please visit %s or ignore this email if you did not request this.
        ''' % url
        try:
            send_mail('Lunchbreak password reset', message, 'hello@cloock.be', [email], fail_silently=False)
        except BadHeaderError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)


class StaffResetView(APIView):
    '''
    Reset password.
    '''
    def post(self, request, email, passwordReset, format=None):
        try:
            validate_email(email)
            staff = Staff.objects.get(email=email)
        except ValidationError:
            raise InvalidEmail()
        except ObjectDoesNotExist:
            raise InvalidEmail('Email address not found.')

        if staff.passwordReset is None or 'password' not in request.data:
            raise BadRequest()
        elif staff.passwordReset != passwordReset:
            staff.passwordReset = None
            staff.save()
            raise BadRequest()
        else:
            staff.passwordReset = None
            staff.setPassword(request.data['password'])
            staff.save()
            return Response(status=status.HTTP_200_OK)


class EmployeeListView(generics.ListAPIView):
    '''
    List the employees.
    '''

    authentication_classes = (StaffAuthentication,)
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        if 'id' in self.kwargs:
            return Employee.objects.filter(id=self.kwargs['id'], staff=self.request.user)
        return Employee.objects.filter(staff=self.request.user)
