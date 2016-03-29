from django.conf.urls import patterns, url
from rest_framework.routers import SimpleRouter

from .. import views

router = SimpleRouter()
router.register(r'user', views.UserViewSet)
router.register(r'order', views.OrderViewSet)
router.register(r'store', views.StoreViewSet)
urlpatterns = router.urls + patterns(
    '',
    url(
        r'^food/(?P<pk>\d+)/?$',
        views.FoodRetrieveView.as_view()
    ),
    url(
        r'^food/category/(?P<foodcategory_id>\d+)/?$',
        views.StoreViewSet.as_view(
            {
                'get': 'food'
            }
        )
    ),

    url(
        r'^foodcategory/(?P<pk>\d+)/?$',
        views.FoodCategoryRetrieveView.as_view()
    ),

    url(
        r'^group/?$',
        views.GroupView.as_view()
    ),

    url(
        r'^invite/?$',
        views.InviteMultiView.as_view()
    ),
    url(
        r'^invite/(?P<pk>\d+)/?$',
        views.InviteSingleView.as_view()
    ),

    url(
        r'^reservation/?$',
        views.ReservationMultiView.as_view(),
        name='user-reservation'
    ),
    url(
        r'^reservation/(?P<pk>\d+)/?$',
        views.ReservationSingleView.as_view(),
        name='reservation'
    ),

    url(
        r'^store/(?P<store_id>\d+)/header/(?P<width>\d+)/(?P<height>\d+)/?$',
        views.StoreHeaderView.as_view()
    ),
    url(
        r'^store/(?P<pk>\d+)/holidayperiods/?$',
        views.HolidayPeriodListView.as_view()
    ),
    url(
        r'^store/(?P<pk>\d+)/hours/?$',
        views.StoreHoursView.as_view()
    ),
    url(
        r'^store/(?P<pk>\d+)/openinghours/?$',
        views.OpeningHoursListView.as_view()
    ),
    url(
        r'^store/nearby'
        r'/(?P<latitude>-?\d+.?\d*)'
        r'/(?P<longitude>-?\d+.?\d*)/?$',
        views.StoreViewSet.as_view(
            {
                'get': 'list'
            }
        )
    ),
    url(
        r'^store/nearby'
        r'/(?P<latitude>-?\d+.?\d*)'
        r'/(?P<longitude>-?\d+.?\d*)'
        r'/(?P<proximity>\d+.?\d*)/?$',
        views.StoreViewSet.as_view(
            {
                'get': 'list'
            }
        )
    ),
    url(
        r'^store/recent/?$',
        views.StoreViewSet.as_view(
            {
                'get': 'list'
            }
        ),
        {
            'recent': True
        }
    ),
    url(
        r'^storecategory/?$',
        views.StoreCategoryListView.as_view()
    ),
)
