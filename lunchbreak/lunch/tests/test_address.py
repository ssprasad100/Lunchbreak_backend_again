import mock
from Lunchbreak.tests.testcase import LunchbreakTestCase

from ..exceptions import AddressNotFound
from ..models import Store


class AddressTestCase(LunchbreakTestCase):

    @mock.patch('googlemaps.Client.timezone')
    @mock.patch('googlemaps.Client.geocode')
    def test_address_not_found(self, mock_geocode, mock_timezone):
        self.mock_timezone_result(mock_timezone)
        try:
            mock_fail = []
            self.mock_geocode_results(mock_geocode, mock_fail)
            Store.objects.create(
                name='test',
                country='nonexisting',
                province='nonexisting',
                city='nonexisting',
                postcode='nonexisting',
                street='nonexisting',
                number=5
            )
        except AddressNotFound:
            try:
                self.mock_geocode_results(mock_geocode)
                Store.objects.create(
                    name='valid',
                    country='Belgie',
                    province='Oost-Vlaanderen',
                    city='Wetteren',
                    postcode='9230',
                    street='Dendermondesteenweg',
                    number=10
                )
            except AddressNotFound:
                self.fail()
        else:
            self.fail()
