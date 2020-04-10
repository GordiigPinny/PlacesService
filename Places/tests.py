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
        self.place_image = PlaceImage.objects.create(created_by=self.user.id, place=self.place, pic_id=1)


class AcceptsListTestCase(LocalBaseTestCase):
    """
    Тесты для /accepts/
    """
    def setUp(self):
        super().setUp()
        self.path = self.url_prefix + 'accepts/'
        self.new_place = Place.objects.create(name='Test', latitude=10, longitude=10, address='Test',
                                              created_by=self.user.id)
        self.data_201 = {
            'created_by': self.user.id,
            'place_id': self.new_place.id,
        }
        self.data_400_1 = {
            'created_by': self.user.id,
        }
        self.data_400_2 = {
            'created_by': self.user.id,
            'place_id': self.place.id + 10000,
        }
        self.data_400_3 = {
            'place_id': self.place.id,
            'created_by': self.user.id,
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

    def testPost401_403_Anon(self):
        self.token.set_role(self.token.ROLES.ANON)
        _ = self.post_response_and_check_status(url=self.path, data=self.data_201, expected_status_code=[401, 403])

    def testPost400_WrongJSON(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_400_1, expected_status_code=400)

    def testPost400_WrongPlaceId(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_400_2, expected_status_code=400)

    def testPost400_SamePlaceAccept(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_400_3, expected_status_code=400)


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


class RatingsListTestCase(LocalBaseTestCase):
    """
    Тесты для /ratings/
    """
    def setUp(self):
        super().setUp()
        self.path = self.url_prefix + 'ratings/'
        self.data_201 = {
            'created_by': self.user.id,
            'place_id': self.place.id,
            'rating': 5,
        }
        self.data_400_1 = {
            'created_by': self.user.id,
        }
        self.data_400_2 = {
            'created_by': self.user.id,
            'place_id': self.place.id + 1000,
            'rating': 5,
        }
        self.data_400_3 = {
            'created_by': self.user.id,
            'place_id': self.place.id + 1000,
            'rating': 6,
        }

    def testGet200_OK(self):
        response = self.get_response_and_check_status(url=self.path)
        self.fields_test(response, ['id', 'created_by', 'place_id', 'rating', 'current_rating'])
        self.list_test(response, Rating)

    def testGet200_WithDeletedQueryParam(self):
        deleted = Rating.objects.create(created_by=self.user.id, place=self.place, rating=3, deleted_flg=True)
        response = self.get_response_and_check_status(url=f'{self.path}?with_deleted=True')
        self.assertEqual(len(response), 2, msg='No deleted instance in response')

    def testGet200_NoDeletedQueryParam(self):
        deleted = Rating.objects.create(created_by=self.user.id, place=self.place, rating=3, deleted_flg=True)
        response = self.get_response_and_check_status(url=f'{self.path}')
        self.assertEqual(len(response), 1, msg='Deleted instance in response')

    def testPost201_OK(self):
        response = self.post_response_and_check_status(url=self.path, data=self.data_201)
        self.assertEqual(response['current_rating'], self.data_201['rating'],
                         msg='Current_rating is not equal to new rating')

    def testPost400_WrongJSON(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_400_1, expected_status_code=400)

    def testPost400_WrongPlaceId(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_400_2, expected_status_code=400)

    def testPost400_WrongRating(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_400_3, expected_status_code=400)


class RatingTestCase(LocalBaseTestCase):
    """
    Тесты для /ratings/<id>/
    """
    def setUp(self):
        super().setUp()
        self.path = self.url_prefix + f'ratings/{self.rating.id}/'
        self.path_404 = self.url_prefix + f'ratings/{self.rating.id+1000}/'

    def testGet200_OK(self):
        response = self.get_response_and_check_status(url=self.path)
        self.fields_test(response, ['id', 'place_id', 'created_by', 'rating', 'current_rating'])

    def testGet200_WithDeletedQueryParam(self):
        deleted = Rating.objects.create(created_by=self.user.id, place=self.place, rating=3, deleted_flg=True)
        path = self.url_prefix + f'ratings/{deleted.id}/'
        response = self.get_response_and_check_status(url=f'{path}?with_deleted=True')

    def testGet404_WrongId(self):
        _ = self.get_response_and_check_status(url=self.path_404, expected_status_code=404)

    def testGet404_NoDeletedQueryParam(self):
        deleted = Rating.objects.create(created_by=self.user.id, place=self.place, rating=3, deleted_flg=True)
        path = self.url_prefix + f'ratings/{deleted.id}/'
        response = self.get_response_and_check_status(url=f'{path}', expected_status_code=404)

    def testDelete204_OK(self):
        _ = self.delete_response_and_check_status(url=self.path)

    def testDelete404_WrongId(self):
        _ = self.delete_response_and_check_status(url=self.path_404, expected_status_code=404)


class PlaceImagesListTestCase(LocalBaseTestCase):
    """
    Тесты для /place_images/
    """
    def setUp(self):
        super().setUp()
        self.path = self.url_prefix + 'place_images/'
        self.data_201 = {
            'created_by': self.user.id,
            'place_id': self.place.id,
            'pic_id': self.place_image.pic_id,
        }
        self.data_400_1 = {
            'created_by': self.user.id,
        }
        self.data_400_2 = {
            'created_by': self.user.id,
            'place_id': self.place.id + 10000,
            'pic_id': self.place_image.pic_id,
        }

    def testGet200_OK(self):
        response = self.get_response_and_check_status(url=self.path)
        self.fields_test(response, ['id', 'created_by', 'place_id', 'pic_id'])
        self.list_test(response, PlaceImage)

    def testGet200_WithDeletedQueryParam(self):
        deleted = PlaceImage.objects.create(created_by=self.user.id, place=self.place, pic_id=1, deleted_flg=True)
        response = self.get_response_and_check_status(url=f'{self.path}?with_deleted=True')
        self.assertEqual(len(response), 2, msg='No deleted instance in response')

    def testGet200_NoDeletedQueryParam(self):
        deleted = PlaceImage.objects.create(created_by=self.user.id, place=self.place, pic_id=1, deleted_flg=True)
        response = self.get_response_and_check_status(url=f'{self.path}')
        self.assertEqual(len(response), 1, msg='Deleted instance in response')

    def testPost201_OK(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_201)

    def testPost400_WrongJson(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_400_1, expected_status_code=400)

    def testPost400_WrongPlaceId(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_400_2, expected_status_code=400)


class PlaceImageTestCase(LocalBaseTestCase):
    """
    Тесты для /place_images/<id>/
    """
    def setUp(self):
        super().setUp()
        self.path = self.url_prefix + f'place_images/{self.place_image.id}/'
        self.path_404 = self.url_prefix + f'place_images/{self.place_image.id + 10000}/'

    def testGet200_OK(self):
        response = self.get_response_and_check_status(url=self.path)
        self.fields_test(response, ['id', 'created_by', 'place_id', 'pic_id'])

    def testGet200_WithDeletedQueryParam(self):
        deleted = PlaceImage.objects.create(created_by=self.user.id, place=self.place, pic_id=1, deleted_flg=True)
        path = self.url_prefix + f'place_images/{deleted.id}/?with_deleted=True'
        _ = self.get_response_and_check_status(url=path)

    def testGet404_WrongId(self):
        _ = self.get_response_and_check_status(url=self.path_404, expected_status_code=404)

    def testGet404_NoDeletedQueryParam(self):
        deleted = PlaceImage.objects.create(created_by=self.user.id, place=self.place, pic_id=1, deleted_flg=True)
        path = self.url_prefix + f'place_images/{deleted.id}/'
        _ = self.get_response_and_check_status(url=path, expected_status_code=404)

    def testDelete204_OK(self):
        _ = self.delete_response_and_check_status(url=self.path)

    def testDelete404_WrongId(self):
        _ = self.delete_response_and_check_status(url=self.path_404, expected_status_code=404)


class PlacesListTestCase(LocalBaseTestCase):
    """
    Тесты для /places/
    """
    def setUp(self):
        super().setUp()
        self.path = self.url_prefix + 'places/'
        self.data_201 = {
            'name': 'POST',
            'address': 'POST',
            'latitude': 30,
            'longitude': 30,
            'created_by': self.user.id,
        }
        self.data_400_1 = {
            'name': 'Not enough',
        }

    def testGet200_OK(self):
        response = self.get_response_and_check_status(url=self.path)
        self.fields_test(response, ['id', 'name', 'address', 'latitude', 'longitude', 'checked_by_moderator',
                                    'accept_type', 'accepts_cnt', 'rating', 'is_created_by_me'])
        self.list_test(response, Place)

    def testGet200_WithDeletedQueryParam(self):
        deleted = Place.objects.create(name='Test', latitude=10, longitude=10, address='Test',
                                       created_by=self.user.id, deleted_flg=True)
        response = self.get_response_and_check_status(url=f'{self.path}?with_deleted=True')
        self.assertEqual(len(response), 2, msg='No deleted instance in response')

    def testGet200_NoDeletedQueryParam(self):
        deleted = Place.objects.create(name='Test', latitude=10, longitude=10, address='Test',
                                       created_by=self.user.id, deleted_flg=True)
        response = self.get_response_and_check_status(url=f'{self.path}')
        self.assertEqual(len(response), 1, msg='Deleted instance in response')

    def testGet200_OnlyMine(self):
        response = self.get_response_and_check_status(url=f'{self.path}?user_id={self.user.id}&only_mine=True')
        self.assertEqual(len(response), 1, msg='Response is empty')

    def testGet200_EmptyOnlyMine(self):
        response = self.get_response_and_check_status(url=f'{self.path}?user_id={self.user.id+1000}&only_mine=True')
        self.assertEqual(len(response), 0, msg='Response is not empty')

    def testGet400_OnlyMineWithoutUserId(self):
        _ = self.get_response_and_check_status(url=f'{self.path}?only_mine=True', expected_status_code=400)

    def testGet200_MapSector(self):
        lat1, long1, lat2, long2 = self.place.latitude - 10, self.place.longitude - 10, self.place.latitude + 10, \
                                   self.place.longitude + 10
        response = self.get_response_and_check_status(
            url=f'{self.path}?lat1={lat1}&long1={long1}&lat2={lat2}&long2={long2}')
        self.assertEqual(len(response), 1, msg='Response is empty')

    def testGet200_EmptyMapSector(self):
        lat1, long1, lat2, long2 = self.place.latitude + 10, self.place.longitude + 10, self.place.latitude + 20, \
                                   self.place.longitude + 20
        response = self.get_response_and_check_status(
            url=f'{self.path}?lat1={lat1}&long1={long1}&lat2={lat2}&long2={long2}')
        self.assertEqual(len(response), 0, msg='Response is not empty')

    def testGet400_WrongCntOfSectorParams(self):
        lat1, long1 = self.place.latitude - 10, self.place.longitude - 10
        self.get_response_and_check_status(url=f'{self.path}?lat1={lat1}&long1={long1}', expected_status_code=400)

    def testGet400_WrongTypeOfSectorParams(self):
        self.get_response_and_check_status(url=f'{self.path}?lat1=str&long1=None&lat2=str&long2=true',
                                           expected_status_code=400)

    def testPost201_OK(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_201)

    def testPost400_WrongJson(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_400_1, expected_status_code=400)


class PlaceTestCase(LocalBaseTestCase):
    """
    Тесты для /places/<id>/
    """
    def setUp(self):
        super().setUp()
        self.path = self.url_prefix + f'places/{self.place.id}/'
        self.path_404 = self.url_prefix + f'places/{self.place.id + 1000}/'
        self.data_202 = {
            'name': 'PATCH',
            'address': 'PATCH',
            'latitude': 20,
            'longitude': 20,
            'created_by': self.user.id,
        }
        self.data_400_1 = {
            'created_by': -1,
        }

    def testGet200_OK(self):
        response = self.get_response_and_check_status(url=self.path)
        self.fields_test(response, ['id', 'name', 'address', 'latitude', 'longitude', 'checked_by_moderator',
                                    'accept_type', 'accepts_cnt', 'rating', 'is_created_by_me', 'is_accepted_by_me',
                                    'my_rating', 'created_by'])

    def testGet200_WithDeletedQueryParam(self):
        deleted = Place.objects.create(name='Test', latitude=10, longitude=10, address='Test',
                                       created_by=self.user.id, deleted_flg=True)
        path = self.url_prefix + f'places/{deleted.id}/?with_deleted=True'
        _ = self.get_response_and_check_status(url=path)

    def testGet404_WrongId(self):
        _ = self.get_response_and_check_status(url=self.path_404, expected_status_code=404)

    def testGet404_NoDeletedQueryParam(self):
        deleted = Place.objects.create(name='Test', latitude=10, longitude=10, address='Test',
                                       created_by=self.user.id, deleted_flg=True)
        path = self.url_prefix + f'places/{deleted.id}/'
        _ = self.get_response_and_check_status(url=path, expected_status_code=404)

    def testPatch202_OK(self):
        self.patch_response_and_check_status(url=self.path, data=self.data_202)

    def testPatch400_NegativeCreatedBy(self):
        self.patch_response_and_check_status(url=self.path, data=self.data_400_1, expected_status_code=400)

    def testPatch404_WrongId(self):
        self.patch_response_and_check_status(url=self.path_404, data=self.data_202, expected_status_code=404)

    def testDelete204_OK(self):
        self.delete_response_and_check_status(url=self.path)

    def testDelete404_WrongId(self):
        self.delete_response_and_check_status(url=self.path_404, expected_status_code=404)
