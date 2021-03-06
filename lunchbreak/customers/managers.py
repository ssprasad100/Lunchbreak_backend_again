from decimal import Decimal

from django.apps import apps
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from lunch.models import Ingredient
from payconiq.models import Transaction
from pendulum import Pendulum

from .config import (ORDER_STATUS_COMPLETED, ORDER_STATUS_NOT_COLLECTED,
                     ORDER_STATUS_PLACED, ORDER_STATUS_RECEIVED,
                     ORDER_STATUS_STARTED, ORDER_STATUS_WAITING,
                     ORDER_STATUSES_ACTIVE, PAYMENT_METHOD_CASH,
                     PAYMENT_METHOD_GOCARDLESS, PAYMENT_METHOD_PAYCONIQ)


class UserManager(BaseUserManager):

    def get_by_natural_key(self, username):
        return self.get(
            phone__phone=username
        )

    def _create_user(self, phone, name, password=None, **kwargs):
        user = self.model(
            phone_id=phone,
            name=name,
            **kwargs
        )
        user.set_password(password)
        user.save()
        return user

    def create_user(self, phone, name, password=None, **kwargs):
        kwargs.setdefault('is_staff', False)
        kwargs.setdefault('is_superuser', False)

        return self._create_user(
            phone=phone,
            name=name,
            password=password,
            **kwargs
        )

    def create_superuser(self, phone, name, password=None, **kwargs):
        kwargs['is_staff'] = True
        kwargs['is_superuser'] = True

        return self._create_user(
            phone=phone,
            name=name,
            password=password,
            **kwargs
        )


class OrderManager(models.Manager):

    def create_with_orderedfood(self, orderedfood, group=None, save=True,
                                create_transaction=True, **kwargs):
        if save:
            self.model.is_valid(orderedfood, **kwargs)

        group_order = None
        group_order_created = False
        receipt = kwargs.get('receipt')
        store = kwargs.get('store')
        if group is not None:
            receipt = Pendulum.instance(
                receipt
            ).at(
                hour=group.receipt_time.hour,
                minute=group.receipt_time.minute,
                second=group.receipt_time.second
            ).timezone_(
                store.timezone
            )._datetime
            kwargs['receipt'] = receipt

            GroupOrder = apps.get_model('customers.GroupOrder')

            group_order_kwargs = {
                'group': group,
                'date': receipt.date()
            }
            if not save:
                group_order = GroupOrder(
                    **group_order_kwargs
                )
            else:
                group_order, group_order_created = GroupOrder.objects.get_or_create(
                    **group_order_kwargs
                )
            kwargs['group_order'] = group_order

        Order = apps.get_model('customers.Order')

        try:
            if not save:
                instance = Order(**kwargs)
            elif self.model == Order:
                instance = self.create(**kwargs)
            else:
                instance, created = self.get_or_create(**kwargs)
                if not created:
                    instance.orderedfood.all().delete()
        except Exception:
            if save and group_order_created and group_order is not None:
                group_order.delete()
            raise

        if save:
            OrderedFood = apps.get_model('customers.OrderedFood')
            try:
                for f in orderedfood:
                    if isinstance(f, dict):
                        OrderedFood.objects.create_for_order(
                            order=instance,
                            **f
                        )
                    elif isinstance(f, OrderedFood):
                        # Clone the OrderedFood so the TemporaryOrder remains intact.
                        old_pk = f.pk
                        f.pk = None
                        f.order = instance
                        f.save()
                        f.ingredients.add(
                            *Ingredient.objects.filter(
                                orderedfood__pk=old_pk
                            )
                        )

            except Exception:
                if instance.group_order is not None \
                        and instance.group_order.orders.count() == 1:
                    instance.group_order.delete()
                instance.delete()
                raise

            instance.save()

            payment_method = kwargs.get('payment_method')
            if payment_method == PAYMENT_METHOD_PAYCONIQ and create_transaction:
                instance.transaction = Transaction.start(
                    amount=instance.total,
                    merchant=store.staff.payconiq
                )

            instance.save()
        return instance


class ConfirmedOrderManager(OrderManager):

    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset().filter(
            models.Q(
                status__in=[
                    ORDER_STATUS_PLACED,
                    ORDER_STATUS_RECEIVED,
                    ORDER_STATUS_STARTED,
                    ORDER_STATUS_WAITING,
                    ORDER_STATUS_COMPLETED,
                    ORDER_STATUS_NOT_COLLECTED,
                ]
            ),
            models.Q(
                payment_method__in=[
                    PAYMENT_METHOD_CASH,
                    PAYMENT_METHOD_GOCARDLESS
                ]
            ) | models.Q(
                payment_method=PAYMENT_METHOD_PAYCONIQ,
                transaction__status=Transaction.SUCCEEDED
            )
        )


class OrderedFoodManager(models.Manager):

    def active_with(self, food=None, ingredient=None, ingredients=[], menu=None):
        """Active OrderedFood with given food or ingredients.

        Args:
            food: Food used (default: {None})
            ingredient: Ingredient used (default: {None})
            ingredients: Ingredients used (default: {[]})

        Returns:
            Active OrderedFood items with the given food or ingredients.
            QuerySet

        Raises:
            ValueError: Food or ingredients need to be given.
        """
        if food is None and ingredient is None and not ingredients and menu is None:
            raise ValueError(
                'Either food or ingredients need to be given.'
            )

        result = self.filter(
            placed_order__status__in=ORDER_STATUSES_ACTIVE
        )

        or_queries = models.Q()
        if food is not None:
            or_queries |= models.Q(original=food)

        if ingredient is not None:
            ingredients.append(ingredient)
        if ingredients:
            query = models.Q(ingredients__in=ingredients)
            or_queries |= query

        if menu is not None:
            or_queries |= models.Q(original__menu=menu)

        return result.filter(or_queries)

    def create_for_order(self, original, amount, total, ingredients=None, **kwargs):
        if not isinstance(amount, Decimal):
            amount = Decimal(amount).quantize(Decimal('1.' + ('0' * 3)))

        original.foodtype.is_valid_amount(
            amount=amount,
            quantity=original.quantity
        )

        if ingredients is not None and len(ingredients) > 0 \
                and not isinstance(ingredients[0], Ingredient):
            ingredients = Ingredient.objects.filter(
                id__in=ingredients
            )

        # It's still the original if the ingredients are the same
        is_original = ingredients is None
        if not is_original:
            selected_ingredientrelations = original.ingredientrelations.filter(
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
            original.check_ingredients(
                ingredients=ingredients
            )

            base_cost = self.model.calculate_cost(
                ingredients=ingredients,
                food=original
            )
            # self.model.check_total(
            #     base_cost=base_cost,
            #     food=original,
            #     amount=amount,
            #     given_total=total
            # )
            instance = self.create(
                amount=amount,
                original=original,
                cost=base_cost,
                is_original=False,
                **kwargs
            )
            instance.ingredients = ingredients
        else:
            # self.model.check_total(
            #     base_cost=original.cost,
            #     food=original,
            #     amount=amount,
            #     given_total=total
            # )
            instance = self.model(
                amount=amount,
                original=original,
                cost=original.cost,
                is_original=True,
                **kwargs
            )

        instance.save()

        return instance


class GroupManager(models.Manager):
    pass
