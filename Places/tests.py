from TestUtils.models import BaseTestCase
from Places.models import Place, Accept, Rating, PlaceImage


class LocalBaseTestCase(BaseTestCase):
    """
    Базовый класс для тестов в этом файле
    """
    def setUp(self):
        super().setUp()
        self.place = Place.objects.create(name='Test', latitude=10, longitude=10, address='Test',
                                          created_by=self.user.id)
        self.accept = Accept.objects.create(created_by=self.user.id, place=self.place)
        self.rating = Rating.objects.create(created_by=self.user.id, place=self.place, rating=4)
        self.place_image = PlaceImage.objects.create(created_by=self.user.id, place=self.place,
                                                     pic_link='http://wwww.vk.com/')


class AcceptsListTestCase(LocalBaseTestCase):
    """
    Тесты для /accepts/
    """
    def setUp(self):
        super().setUp()
        self.path = self.url_prefix + 'accepts/'
        self.data_201 = {
            'created_by': self.user.id,
            'place_id': self.place.id,
        }
        self.data_400_1 = {
            'created_by': self.user.id,
        }
        self.data_400_2 = {
            'created_by': self.user.id,
            'place_id': self.place.id + 1,
        }

    def testGet200_OK(self):
        response = self.get_response_and_check_status(url=self.path)
        self.fields_test(response, needed_fields=['id', 'place_id', 'created_by'])
        self.list_test(response, Accept)

    def testGet200_WithDeleted(self):
        deleted = Accept.objects.create(created_by=self.user.id, place=self.place, deleted_flg=True)
        response = self.get_response_and_check_status(url=f'{self.path}?with_deleted=True')
        self.assertEqual(len(response), 2, msg='No deleted object in response')

    def testGet200_WithQueryParam(self):
        response = self.get_response_and_check_status(url=f'{self.path}?place_id={self.place.id}')
        self.fields_test(response, needed_fields=['id', 'place_id', 'created_by'])
        self.assertEqual(len(response), 1, msg='More than one accept in response')

    def testGet200_EmptyWrongQueryParam(self):
        response = self.get_response_and_check_status(url=f'{self.path}?place_id={self.place.id+100}',
                                                      expected_status_code=200)
        self.assertEqual(len(response), 0, msg=f'Response must be empty, but len = {len(response)}')

    def testPost201_OK(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_201)

    def testPost400_WrongJSON(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_400_1, expected_status_code=400)

    def testPost400_WrongPlaceId(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_400_2, expected_status_code=400)


class AcceptTestCase(LocalBaseTestCase):
    """
    Тесты для /accepts/<id>/
    """
    def setUp(self):
        super().setUp()
        self.path = self.url_prefix + f'accepts/{self.accept.id}/'
        self.path_404 = self.url_prefix + f'accepts/{self.accept.id+1000}/'

    def testGet200_OK(self):
        response = self.get_response_and_check_status(url=self.path)
        self.fields_test(response, ['id', 'created_by', 'place_id'])

    def testGet200_Deleted(self):
        self.accept.soft_delete()
        _ = self.get_response_and_check_status(url=f'{self.path}?with_deleted=True')

    def testGet404_WrongId(self):
        _ = self.get_response_and_check_status(url=self.path_404, expected_status_code=404)

    def testDelete204_OK(self):
        _ = self.delete_response_and_check_status(url=self.path)

    def testDelete404_WrongId(self):
        _ = self.delete_response_and_check_status(url=self.path_404, expected_status_code=404)
