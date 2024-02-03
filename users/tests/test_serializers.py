from rest_framework.test import APITestCase

from users.models import User
from users.serializers import UserRegistSerializer


class SerializersUsersAPITest(APITestCase):
    def setUp(self):
        """data for test db"""

        self.user_1 = User.objects.create_user(
            phone_number="+79136757877", password="nik140406"
        )
        self.user_2 = User.objects.create_user(
            phone_number="+79136557877", password="nik140406"
        )

    # def test_user_serializer(self):
    #     """This test covers UserSerializer"""

    #     data = UserSerializer([self.user_1, self.user_2], many=True).data
    #     expected_data = [
    #         {
    #             "id": self.user_1.id,
    #             "username": self.user_1.username,
    #             "photo": self.user_1.photo,
    #         },
    #         {
    #             "id": self.user_2.id,
    #             "username": self.user_2.username,
    #             "photo": self.user_2.photo,
    #         },
    #     ]
    #     self.assertEqual(expected_data, data)

    def test_user_register_serializer(self):
        """This test covers register serializer"""

        data = UserRegistSerializer(self.user_1).data
        expected_data = (
            {
                "id": self.user_1.id,
                "phone_number": "+79136757877",
            },
        )
        self.assertEqual(expected_data[0], data)
