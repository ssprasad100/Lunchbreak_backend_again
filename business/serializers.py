from business.models import Employee, Staff, StaffToken, EmployeeToken
from customers.models import Order
from customers.serializers import OrderedFoodSerializer
from lunch.serializers import StoreSerializer, TokenSerializer
from rest_framework import serializers


class BusinessTokenSerializer(TokenSerializer):
    password = serializers.CharField(max_length=128, write_only=True)
    device = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        fields = TokenSerializer.Meta.fields + ('password', 'device',)
        write_only_fields = ('password', 'device',)
        read_only_fields = ()


class StaffSerializer(serializers.ModelSerializer):
    store = StoreSerializer()

    class Meta:
        model = Staff
        fields = ('id', 'store', 'password',)
        read_only_fields = ('id',)
        write_only_fields = ('password',)


class StaffTokenSerializer(BusinessTokenSerializer):

    class Meta:
        model = StaffToken
        fields = BusinessTokenSerializer.Meta.fields + ('staff',)
        read_only_fields = BusinessTokenSerializer.Meta.read_only_fields + ('staff',)


class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ('id', 'name', 'password',)
        read_only_fields = ('id',)
        write_only_fields = ('password',)


class EmployeeTokenSerializer(BusinessTokenSerializer):

    class Meta:
        model = EmployeeToken
        fields = BusinessTokenSerializer.Meta.fields + ('employee',)
        read_only_fields = BusinessTokenSerializer.Meta.read_only_fields + ('employee',)


class OrderSerializer(serializers.ModelSerializer):
    food = OrderedFoodSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'orderedTime', 'pickupTime', 'status', 'paid', 'food', 'total',)
        read_only_fields = ('id', 'user', 'orderedTime', 'pickupTime', 'paid', 'food', 'total',)
