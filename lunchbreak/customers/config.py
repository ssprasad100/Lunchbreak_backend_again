from .signals import *  # NOQA

ORDER_STATUS_PLACED = 0
ORDER_STATUS_DENIED = 1
ORDER_STATUS_RECEIVED = 2
ORDER_STATUS_STARTED = 3
ORDER_STATUS_WAITING = 4
ORDER_STATUS_COMPLETED = 5
ORDER_STATUS_NOT_COLLECTED = 6
ORDER_STATUSES = (
    (ORDER_STATUS_PLACED, 'Geplaatst'),
    (ORDER_STATUS_DENIED, 'Afgewezen'),
    (ORDER_STATUS_RECEIVED, 'Ontvangen'),
    (ORDER_STATUS_STARTED, 'Aan begonnen'),
    (ORDER_STATUS_WAITING, 'Ligt klaar'),
    (ORDER_STATUS_COMPLETED, 'Voltooid'),
    (ORDER_STATUS_NOT_COLLECTED, 'Niet opgehaald')
)
ORDER_STATUSES_ENDED = [
    ORDER_STATUS_COMPLETED,
    ORDER_STATUS_DENIED,
    ORDER_STATUS_NOT_COLLECTED
]
ORDER_STATUSES_ACTIVE = [
    ORDER_STATUS_PLACED,
    ORDER_STATUS_RECEIVED,
    ORDER_STATUS_STARTED,
    ORDER_STATUS_WAITING
]

ORDER_STATUS_SIGNALS = {
    ORDER_STATUS_PLACED: order_created,
    ORDER_STATUS_DENIED: order_denied,
    ORDER_STATUS_RECEIVED: order_received,
    ORDER_STATUS_STARTED: order_started,
    ORDER_STATUS_WAITING: order_waiting,
    ORDER_STATUS_COMPLETED: order_completed,
    ORDER_STATUS_NOT_COLLECTED: order_not_collected
}

RESERVATION_STATUS_PLACED = 0
RESERVATION_STATUS_DENIED = 1
RESERVATION_STATUS_ACCEPTED = 2
RESERVATION_STATUS_CANCELLED = 3
RESERVATION_STATUS_COMPLETED = 4
RESERVATION_STATUS_NO_SHOW = 5

RESERVATION_STATUSES = (
    (RESERVATION_STATUS_PLACED, 'Geplaatst'),
    (RESERVATION_STATUS_DENIED, 'Afgewezen'),
    (RESERVATION_STATUS_ACCEPTED, 'Aanvaard'),
    (RESERVATION_STATUS_CANCELLED, 'Geannuleerd'),
    (RESERVATION_STATUS_COMPLETED, 'Voltooid'),
    (RESERVATION_STATUS_NO_SHOW, 'Niet gekomen'),
)

RESERVATION_STATUS_USER_CHANGE = (
    (RESERVATION_STATUS_PLACED, 'Geplaatst'),
    (RESERVATION_STATUS_ACCEPTED, 'Aanvaard'),
)

RESERVATION_STATUS_USER = (
    (RESERVATION_STATUS_CANCELLED, 'Geannuleerd'),
)

RESERVATION_STATUS_EMPLOYEE = (
    (RESERVATION_STATUS_DENIED, 'Afgewezen'),
    (RESERVATION_STATUS_ACCEPTED, 'Aanvaard'),
    (RESERVATION_STATUS_COMPLETED, 'Voltooid'),
    (RESERVATION_STATUS_NO_SHOW, 'Niet gekomen'),
)

DEMO_PHONE = '+32411111111'

PAYMENT_METHOD_CASH = 0
PAYMENT_METHOD_GOCARDLESS = 1

PAYMENT_METHODS = (
    (PAYMENT_METHOD_CASH, 'Cash'),
    (PAYMENT_METHOD_GOCARDLESS, 'Online (veilig via GoCardless)'),
)

PAYMENTLINK_COMPLETION_REDIRECT_URL = 'lunchbreak://gocardless/redirectflow/'
