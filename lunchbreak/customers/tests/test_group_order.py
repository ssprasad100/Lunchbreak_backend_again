from decimal import Decimal

import mock
from lunch.exceptions import LinkingError
from pendulum import Pendulum

from . import CustomersTestCase
from ..config import ORDER_STATUS_COMPLETED, ORDER_STATUS_RECEIVED
from ..models import Group, GroupOrder, Order


class GroupOrderTestCase(CustomersTestCase):

    def setUp(self):
        super().setUp()

        self.group = Group.objects.create(
            name='Test Group',
            store=self.store,
            email='andreas@cloock.be'
        )

    @mock.patch('customers.tasks.send_group_order_email.apply_async')
    @mock.patch('lunch.models.Store.is_open')
    @mock.patch('customers.models.Order.is_valid')
    def test_same_store(self, mock_is_valid, mock_is_open, mock_task):
        """Test whether Order.store == Order.group.store."""

        self.assertRaises(
            LinkingError,
            Order.objects.create_with_orderedfood,
            orderedfood=[],
            store=self.store_other,
            receipt=Pendulum.now()._datetime,
            group=self.group,
            user=self.user
        )

    @mock.patch('customers.tasks.send_group_order_email.apply_async')
    def test_email_task_triggered(self, mock_task):
        """Test whether the Celery emailt ask is triggered on creation."""

        GroupOrder.objects.create(
            group=self.group,
            date=Pendulum.today().date()
        )

        self.assertTrue(mock_task.called)

    @mock.patch('lunch.models.Store.is_open')
    @mock.patch('customers.models.Order.is_valid')
    @mock.patch('customers.tasks.send_group_order_email.apply_async')
    def test_create_group_order(self, mock_task, mock_is_valid, mock_is_open):
        """Test whether creating an Order with a group creates a group Order."""

        order = Order.objects.create_with_orderedfood(
            orderedfood=[],
            store=self.store,
            receipt=Pendulum.now()._datetime,
            group=self.group,
            user=self.user
        )

        # Creating an order with a group should create a GroupOrder
        self.assertIsNotNone(order.group_order)
        self.assertEqual(
            self.group.group_orders.all().count(),
            1
        )
        self.assertEqual(
            order.group_order.date,
            order.receipt.date()
        )

        # It shouldn't create a duplicate for the same date
        order = Order.objects.create_with_orderedfood(
            orderedfood=[],
            store=self.store,
            receipt=Pendulum.now()._datetime,
            group=self.group,
            user=self.user
        )

        self.assertIsNotNone(order.group_order)
        self.assertEqual(
            self.group.group_orders.all().count(),
            1
        )

        # It should create a new GroupOrder if the receipt is for a different date
        order = Order.objects.create_with_orderedfood(
            orderedfood=[],
            store=self.store,
            receipt=Pendulum.tomorrow()._datetime,
            group=self.group,
            user=self.user
        )

        self.assertIsNotNone(order.group_order)
        self.assertEqual(
            self.group.group_orders.all().count(),
            2
        )

    @mock.patch('lunch.models.Store.is_open')
    @mock.patch('customers.models.Order.is_valid')
    @mock.patch('customers.tasks.send_group_order_email.apply_async')
    def test_discount(self, mock_task, mock_is_valid, mock_is_open):
        """Test whether a discount is applied to an order.

        Order.total is calculated including discount, Order.total_confirmed is
        not adjusted with a discount. We assume Order.total_confirmed already
        includes the discount.
        """

        group = Group.objects.create(
            name='Test Discount',
            store=self.store,
            email='test_discount@cloock.be',
            discount=10
        )

        total = Decimal(self.food.cost) * Decimal(self.food.amount)
        order = Order.objects.create_with_orderedfood(
            store=self.store,
            receipt=Pendulum.now()._datetime,
            group=group,
            user=self.user,
            orderedfood=[
                {
                    'original': self.food,
                    'total': total,
                    'amount': self.food.amount
                }
            ]
        )

        total_discounted = Decimal(total * (100 - group.discount) / 100)
        self.assertEqual(
            order.total,
            total_discounted
        )
        self.assertEqual(
            order.discount,
            group.discount
        )

        total_confirmed = Decimal(95)
        order.total_confirmed = total_confirmed
        order.save()
        self.assertEqual(
            order.total,
            total_discounted
        )
        self.assertEqual(
            order.discount,
            group.discount
        )
        # Order.total_confirmed is including discount
        self.assertEqual(
            order.total_confirmed,
            total_confirmed
        )

    @mock.patch('customers.tasks.send_group_order_email.apply_async')
    def test_synced_status(self, mock_task):
        """Test whether changing the status on the GroupOrder changes the statuses on the orders.

        Also test whether changing the status of an Order with a GroupOrder
        doesn't affect the status because that should always be the same as the GroupOrder.
        """

        group_order = GroupOrder.objects.create(
            group=self.group,
            date=Pendulum.now().date()
        )

        def create_order():
            return Order.objects.create(
                store=self.store,
                receipt=Pendulum.now()._datetime,
                group_order=group_order,
                user=self.user
            )

        create_order()
        create_order()
        self.assertEqual(
            group_order.orders.count(),
            2
        )

        def assert_same_status():
            for order in group_order.orders.all():
                self.assertEqual(
                    group_order.status,
                    order.status
                )

        # On creation all of the statuses should be the same
        assert_same_status()

        # Changing the order status of the group order should
        # also change the status on all of the orders.
        group_order.status = ORDER_STATUS_RECEIVED
        group_order.save()
        assert_same_status()

        # Creating a new order should change the status to the one of the GroupOrder.
        order3 = create_order()
        self.assertEqual(
            group_order.orders.count(),
            3
        )
        self.assertEqual(
            group_order.status,
            order3.status
        )
        assert_same_status()

        # Changing the status on an order should be ignored
        order3.status = ORDER_STATUS_COMPLETED
        order3.save()
        self.assertEqual(
            order3.status,
            ORDER_STATUS_RECEIVED
        )
        assert_same_status()