from rest_framework import serializers

from .models import (BaseToken, Food, Menu, FoodType, HolidayPeriod,
                     Ingredient, IngredientGroup, IngredientRelation,
                     OpeningPeriod, Quantity, Store, StoreCategory)


class StoreCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = StoreCategory
        fields = (
            'id',
            'name',
            'icon',
        )
        read_only_fields = (
            'id',
        )


class StoreSerializer(serializers.ModelSerializer):
    categories = StoreCategorySerializer(
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
            'last_modified',
        )
        read_only_fields = (
            'id',
            'latitude',
            'longitude',
            'hearts_count',
            'last_modified',
        )


class StoreDetailSerializer(StoreSerializer):
    categories = StoreCategorySerializer(
        many=True,
        read_only=True
    )

    class Meta(StoreSerializer.Meta):
        fields = StoreSerializer.Meta.fields + (
            'country',
            'province',
            'city',
            'postcode',
            'street',
            'number',
            'wait',
            'preorder_time',
        )


class OpeningPeriodSerializer(serializers.ModelSerializer):

    class Meta:
        model = OpeningPeriod
        fields = (
            'id',
            'day',
            'time',
            'duration',
        )
        read_only_fields = (
            'id',
        )


class HolidayPeriodSerializer(serializers.ModelSerializer):

    class Meta:
        model = HolidayPeriod
        fields = (
            'id',
            'description',
            'start',
            'end',
            'closed',
        )
        read_only_fields = (
            'id',
        )


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


class IngredientDetailSerializer(IngredientSerializer):

    class Meta(IngredientSerializer.Meta):
        fields = IngredientSerializer.Meta.fields + (
            'last_modified',
        )
        read_only_fields = IngredientSerializer.Meta.read_only_fields + (
            'last_modified',
        )


class IngredientRelationSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )

    class Meta:
        model = IngredientRelation
        fields = (
            'id',
            'selected',
        )
        read_only_fields = (
            'id',
        )


class IngredientRelationDetailSerializer(serializers.HyperlinkedModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = IngredientRelation
        fields = (
            'selected',
            'ingredient',
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


class IngredientGroupDetailSerializer(IngredientGroupSerializer):
    ingredients = IngredientSerializer(
        many=True
    )

    class Meta(IngredientGroupSerializer.Meta):
        fields = IngredientGroupSerializer.Meta.fields + (
            'ingredients',
        )


class MenuSerializer(serializers.ModelSerializer):

    class Meta:
        model = Menu
        fields = (
            'id',
            'name',
            'priority',
        )
        read_only_fields = (
            'id',
        )


class MenuDetailSerializer(MenuSerializer):

    class Meta(MenuSerializer.Meta):
        fields = MenuSerializer.Meta.fields + (
            'store',
        )


class FoodTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = FoodType
        fields = (
            'id',
            'name',
            'quantifier',
            'inputtype',
            'customisable',
        )
        read_only_fields = (
            'id',
        )


class QuantitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Quantity
        fields = (
            'id',
            'min',
            'max',
            'last_modified',
        )
        read_only_fields = (
            'id',
            'last_modified',
        )


class QuantityDetailSerializer(QuantitySerializer):

    class Meta:
        model = QuantitySerializer.Meta.model
        fields = QuantitySerializer.Meta.fields + (
            'foodtype',
        )
        read_only_fields = QuantitySerializer.Meta.read_only_fields


class BaseFoodSerializer(serializers.ModelSerializer):
    """This serializer is not meant to be returned!"""

    foodtype = FoodTypeSerializer(
        many=False
    )
    menu = MenuSerializer(
        many=False
    )
    quantity = QuantitySerializer(
        many=False
    )

    class Meta:
        model = Food
        fields = (
            'id',
            'name',
            'amount',
            'cost',
            'menu',
            'foodtype',
            'priority',
            'has_ingredients',
            'quantity',
            'preorder_days',
        )
        read_only_fields = (
            'id',
            'has_ingredients',
        )


class FoodSerializer(BaseFoodSerializer):

    class Meta(BaseFoodSerializer.Meta):
        fields = BaseFoodSerializer.Meta.fields + (
            'has_ingredients',
        )
        read_only_fields = BaseFoodSerializer.Meta.read_only_fields + (
            'has_ingredients',
        )


class FoodDetailSerializer(BaseFoodSerializer):
    ingredientgroups = IngredientGroupSerializer(
        many=True,
        read_only=True
    )
    ingredients = IngredientRelationDetailSerializer(
        source='ingredientrelation_set',
        many=True
    )

    class Meta(BaseFoodSerializer.Meta):
        fields = BaseFoodSerializer.Meta.fields + (
            'description',
            'commentable',
            'ingredients',
            'store',
            'last_modified',
            'ingredientgroups',
        )
        read_only_fields = BaseFoodSerializer.Meta.read_only_fields + (
            'ingredientgroups',
            'last_modified',
        )

    def to_representation(self, obj):
        result = super().to_representation(obj)

        ingredientrelations_added = []
        ingredientgroups = obj.ingredientgroups.all().prefetch_related(
            'ingredient_set'
        )
        obj_ingredients = obj.ingredients.all()

        for ingredientgroup in ingredientgroups:
            ingredients = ingredientgroup.ingredient_set.all()
            for ingredient in ingredients:
                if ingredient not in obj_ingredients:
                    ingredientrelations_added.append(
                        IngredientRelation(
                            ingredient=ingredient
                        )
                    )

        serializer = IngredientRelationDetailSerializer(
            many=True
        )
        relation_representation = serializer.to_representation(
            ingredientrelations_added
        )

        result['ingredients'] += relation_representation

        return result


class TokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = BaseToken
        fields = (
            'id',
            'device',
            'service',
            'registration_id',
            'active',
        )
        read_only_fields = (
            'id',
            'device',
            'service',
            'active',
        )


class TokenDetailSerializer(TokenSerializer):

    class Meta(TokenSerializer.Meta):
        fields = TokenSerializer.Meta.fields + (
            'identifier',
        )
        read_only_fields = TokenSerializer.Meta.read_only_fields + (
            'identifier',
        )
