from django.apps import apps
from django.db import models
from lunch.models import Food, IngredientGroup

from .exceptions import OrderedFoodNotOriginal


class OrderManager(models.Manager):

    def create_with_orderedfood(self, orderedfood, **kwargs):
        self.model.is_valid(orderedfood, **kwargs)

        instance = self.model.objects.create(**kwargs)
        OrderedFood = apps.get_model('customers.OrderedFood')

        try:
            for f in orderedfood:
                if isinstance(f, dict):
                    OrderedFood.objects.create_for_order(
                        order=instance,
                        **f
                    )
                elif isinstance(f, OrderedFood):
                    f.order = instance
                    f.save()
        except:
            instance.delete()
            raise

        instance.save()
        return instance


class OrderedFoodManager(models.Manager):

    def create_for_order(self, original, amount, cost, ingredients=None, save=True, **kwargs):
        original.foodtype.is_valid_amount(
            amount=amount,
            quantity=original.quantity
        )

        # It's still the original if the ingredients are the same
        is_original = ingredients is None
        if not is_original:
            selected_ingredientrelations = original.ingredientrelation_set.filter(
                selected=True
            ).select_related(
                'ingredient'
            )
            original_ingredients = {
                rel.ingredient for rel in selected_ingredientrelations
            }
            if set(ingredients) == original_ingredients:
                is_original = True

        if not is_original:
            IngredientGroup.check_ingredients(
                ingredients=ingredients,
                food=original
            )

            closest_food = Food.objects.closest(
                ingredients=ingredients,
                original=original
            )

            if closest_food != original:
                raise OrderedFoodNotOriginal()

            base_cost = self.model.calculate_cost(
                ingredients=ingredients,
                food=original
            )
            self.model.check_cost(
                base_cost=base_cost,
                food=original,
                amount=amount,
                given_cost=cost
            )
            instance = self.model(
                amount=amount,
                original=original,
                cost=base_cost,
                is_original=False,
                **kwargs
            )
        else:
            self.model.check_cost(
                base_cost=original.cost,
                food=original,
                amount=amount,
                given_cost=cost
            )
            instance = self.model(
                amount=amount,
                original=original,
                cost=cost,
                is_original=True,
                **kwargs
            )

        if save:
            instance.save()

        return instance
