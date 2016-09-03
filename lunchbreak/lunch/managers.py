import copy

from django.core.exceptions import MultipleObjectsReturned
from django.db import models
from push_notifications.models import DeviceManager

from .config import random_token


class StoreManager(models.Manager):

    def nearby(self, latitude, longitude, proximity):
        # Haversine formule is het beste om te gebruiken bij korte afstanden.
        # d = 2 * r * asin(
        #   sqrt(
        #       sin^2(
        #           ( lat2-lat1 ) / 2
        #       ) + cos(lat1)*cos(lat2)*sin^2(
        #           (lon2-lon1) / 2
        #       )
        #   )
        # )
        haversine = '''
        (
            (2*6371)
            * ASIN(
                SQRT(
                    POW(
                        SIN( (RADIANS(%s) - RADIANS(latitude)) / 2 )
                    , 2)
                    + (
                        COS(RADIANS(latitude))
                        * COS(RADIANS(%s))
                        * POW(
                            SIN(
                                (RADIANS(%s) - RADIANS(longitude)) / 2
                            )
                        , 2
                        )
                    )
                )
            )
        )
        '''
        haversine_where = "{} < %s".format(haversine)
        return self.get_queryset().exclude(
            latitude=None
        ).exclude(
            longitude=None
        ).extra(
            select={
                'distance': haversine
            },
            select_params=[
                latitude,
                latitude,
                longitude
            ],
            where=[
                haversine_where
            ],
            params=[
                latitude,
                latitude,
                longitude,
                proximity
            ],
            order_by=[
                'distance'
            ]
        )


class FoodManager(models.Manager):

    def closest(self, ingredients, original):
        if not original.foodtype.customisable:
            return original

        ingredients_in = '-1' if len(ingredients) == 0 else '''
            CASE WHEN lunch_ingredient.id IN (%s)
                THEN
                    1
                ELSE
                    -1
                END''' % ','.join([str(i.id) for i in ingredients])

        return self.model.objects.raw('''
            SELECT
                lunch_food.*,
                SUM(
                    CASE WHEN lunch_ingredient.id IS NULL
                        THEN
                            0
                        ELSE
                            ''' + ingredients_in + '''
                        END
                ) as score
            FROM
                `lunch_food`
                LEFT JOIN
                    `lunch_ingredientrelation` ON lunch_food.id = lunch_ingredientrelation.food_id
                    AND lunch_ingredientrelation.typical = 1
                LEFT JOIN
                    `lunch_ingredient` ON lunch_ingredientrelation.ingredient_id = lunch_ingredient.id
            WHERE
                lunch_food.foodtype_id = %s AND
                lunch_food.store_id = %s
            GROUP BY
                lunch_food.id
            ORDER BY
                score DESC,
                lunch_food.id = %s DESC,
                lunch_food.cost ASC;
            ''', [
            original.foodtype.id,
            original.store.id,
            original.id
        ])[0]


class BaseTokenManager(DeviceManager):

    def create_token(self, arguments, defaults, clone=False):
        identifier_raw = random_token()
        defaults['identifier'] = identifier_raw

        try:
            token, created = self.update_or_create(
                defaults=defaults,
                **arguments
            )
        except MultipleObjectsReturned:
            self.filter(**arguments).delete()
            token, created = self.update_or_create(
                defaults=defaults,
                **arguments
            )

        if clone:
            token_copy = copy.copy(token)
            token_copy.identifier = identifier_raw
            return (token_copy, created,)
        return (token, created,)
