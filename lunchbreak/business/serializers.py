from customers import serializers as customers_serializers
from customers.config import RESERVATION_STATUS_EMPLOYEE
from customers.models import Order, OrderedFood, Reservation
from lunch import serializers as lunch_serializers
from lunch.config import TOKEN_IDENTIFIER_LENGTH
from lunch.fields import CurrentUserAttributeDefault
from lunch.models import (Food, Ingredient, IngredientGroup,
                          IngredientRelation, Store)
from rest_framework import serializers

from .models import (AbstractPassword, Employee, EmployeeToken, Staff,
                     StaffToken)


class StoreDetailSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = Store
        fields = (
            'id',
            'name',
            'city',
            'street',
            'latitude',
            'longitude',
            'categories',
            'hearts_count',
            'country',
            'province',
            'city',
            'postcode',
            'street',
            'number',
            'wait',
            'preorder_time',
            'enabled',
        )
        read_only_fields = (
            'id',
            'latitude',
            'longitude',
            'hearts_count',
            'categories',
        )


class StoreMerchantSerializer(serializers.BaseSerializer):

    def to_representation(self, url):
        return {
            'authorisation_link': url
        }


class EmployeePasswordRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ('id',)
        write_only_fields = fields


class StaffPasswordRequestSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=255
    )

    class Meta:
        model = Staff
        fields = ('email',)
        write_only_fields = fields


class PasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=255,
        write_only=True
    )
    password_reset = serializers.CharField(
        max_length=TOKEN_IDENTIFIER_LENGTH,
        write_only=True
    )

    class Meta:
        model = AbstractPassword
        fields = (
            'password',
            'password_reset',
            'email',
        )
        write_only_fields = fields


class EmployeePasswordSerializer(PasswordSerializer):

    class Meta(PasswordSerializer.Meta):
        model = Employee


class StaffPasswordSerializer(PasswordSerializer):

    class Meta(PasswordSerializer.Meta):
        model = Staff


class BusinessTokenSerializer(lunch_serializers.TokenDetailSerializer):
    password = serializers.CharField(
        max_length=255,
        write_only=True
    )

    class Meta(lunch_serializers.TokenDetailSerializer.Meta):
        fields = lunch_serializers.TokenDetailSerializer.Meta.fields + (
            'password',
        )
        write_only_fields = (
            'password',
        )
        read_only_fields = (
            'id',
            'identifier',
            'active',
        )


class StaffSerializer(serializers.ModelSerializer):
    store = StoreDetailSerializer()

    class Meta:
        model = Staff
        fields = (
            'id',
            'store',
        )
        read_only_fields = (
            'id',
        )


class StaffTokenSerializer(BusinessTokenSerializer):

    class Meta(BusinessTokenSerializer.Meta):
        model = StaffToken
        fields = BusinessTokenSerializer.Meta.fields + (
            'staff',
        )


class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = (
            'id',
            'name',
            'owner',
        )
        read_only_fields = (
            'id',
        )


class EmployeeTokenSerializer(BusinessTokenSerializer):

    class Meta(BusinessTokenSerializer.Meta):
        model = EmployeeToken
        fields = BusinessTokenSerializer.Meta.fields + (
            'employee',
        )


class OrderedFoodSerializer(serializers.ModelSerializer):
    cost = serializers.DecimalField(
        decimal_places=2,
        max_digits=7
    )

    class Meta:
        model = OrderedFood
        fields = (
            'id',
            'ingredients',
            'amount',
            'original',
            'cost',
            'is_original',
            'comment',
        )
        read_only_fields = fields


class OrderSpreadSerializer(serializers.BaseSerializer):
    amount = serializers.IntegerField(
        read_only=True
    )
    average = serializers.DecimalField(
        decimal_places=2,
        max_digits=7
    )
    # 'sum' is a built-in function in Python, use 'sm' in code and return 'sum'
    sm = serializers.DecimalField(
        decimal_places=2,
        max_digits=7
    )
    unit = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        fields = (
            'amount',
            'average',
            'sm',
            'unit',
        )
        read_only_fields = fields

    def to_representation(self, obj):
        return {
            'amount': obj.amount,
            'average': obj.average,
            'sum': obj.sm,
            'unit': obj.unit
        }


class OrderSerializer(customers_serializers.OrderSerializer):
    user = customers_serializers.UserSerializer(
        read_only=True
    )

    class Meta(customers_serializers.OrderSerializer.Meta):
        fields = (
            'id',
            'user',
            'placed',
            'receipt',
            'status',
            'total',
            'total_confirmed',
        )
        read_only_fields = (
            'id',
            'user',
            'placed',
            'receipt',
            'total',
            'total_confirmed',
        )


class OrderDetailSerializer(OrderSerializer):
    orderedfood = OrderedFoodSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Order
        fields = OrderSerializer.Meta.fields + (
            'orderedfood',
            'description',
        )
        read_only_fields = (
            'id',
            'user',
            'placed',
            'receipt',
            'total',
            'orderedfood',
            'description',
            'paid',
        )


class IngredientGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngredientGroup
        fields = (
            'id',
            'name',
            'maximum',
            'minimum',
            'priority',
            'cost',
            'foodtype',
        )
        read_only_fields = (
            'id',
        )


class IngredientRelationSerializer(serializers.ModelSerializer):
    ingredient = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientRelation
        fields = (
            'ingredient',
            'selected',
        )
        write_only_fields = fields


class FoodSerializer(serializers.ModelSerializer):
    ingredients = lunch_serializers.IngredientRelationSerializer(
        source='ingredientrelation_set',
        many=True,
        required=False,
        read_only=True
    )
    ingredientrelations = IngredientRelationSerializer(
        source='ingredientrelation_set',
        many=True,
        required=False,
        write_only=True
    )
    orderedfood_count = serializers.IntegerField(
        read_only=True
    )
    store = serializers.ModelField(
        model_field=Food()._meta.get_field('store'),
        read_only=True,
        default=serializers.CreateOnlyDefault(
            CurrentUserAttributeDefault('staff.store')
        )
    )

    class Meta:
        model = Food
        fields = (
            'id',
            'name',
            'description',
            'amount',
            'cost',
            'foodtype',
            'preorder_days',
            'commentable',
            'priority',

            'store',
            'menu',
            'ingredients',
            'ingredientgroups',

            'ingredientrelations',
            'orderedfood_count',
            'deleted',
            'last_modified',
        )
        read_only_fields = (
            'id',
            'ingredients',
            'orderedfood_count',
            'store',
            'last_modified',
        )
        write_only_fields = (
            'ingredientrelations',
        )

    def create_or_update(self, validated_data, food=None):
        update = food is not None
        relations = validated_data.pop('ingredientrelation_set', None)

        if not update:
            food = super().create(validated_data)
        else:
            food = super().update(food, validated_data)

        if relations is not None:
            if update:
                IngredientRelation.objects.filter(food=food).delete()
            for relation in relations:
                IngredientRelation.objects.update_or_create(
                    food=food,
                    **relation
                )

        return food

    def create(self, validated_data):
        return self.create_or_update(validated_data)

    def update(self, instance, validated_data):
        return self.create_or_update(validated_data, instance)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'cost',
            'group',
        )
        read_only_fields = (
            'id',
        )


class IngredientGroupDetailSerializer(serializers.ModelSerializer):
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = IngredientGroup
        fields = (
            'id',
            'name',
            'maximum',
            'minimum',
            'ingredients',
            'priority',
            'cost',
            'foodtype',
        )
        read_only_fields = (
            'id',
            'ingredients',
        )


class FoodDetailSerializer(lunch_serializers.FoodDetailSerializer):

    class Meta(lunch_serializers.FoodDetailSerializer.Meta):
        fields = lunch_serializers.FoodDetailSerializer.Meta.fields + (
            'deleted',
        )


class ReservationSerializer(serializers.ModelSerializer):
    user = customers_serializers.UserSerializer(
        read_only=True
    )
    status = serializers.ChoiceField(
        choices=RESERVATION_STATUS_EMPLOYEE
    )

    class Meta:
        model = Reservation
        fields = (
            'id',
            'user',
            'seats',
            'placed',
            'reservation_time',
            'comment',
            'suggestion',
            'response',
            'status',
        )
        read_only_fields = (
            'id',
            'user',
            'placed',
            'reservation_time',
            'comment',
        )
