from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import PhoneNumberVerifySMS, User, Schedule


class UserAPITestCase(APITestCase):
    def setUp(self):
        """data for test db"""

        self.superuser = User.objects.create_superuser(
            phone_number="+79136757877",
            password="admin_password1",
        )
        self.superuser_2 = User.objects.create_superuser(
            phone_number="+79136757878", password="admin_password2"
        )
        self.access_token = str(RefreshToken.for_user(self.superuser).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_create_account(self):
        """This test covers registration"""

        url = f"{settings.DOMAIN_NAME}/auth/users/"
        data = {
            "phone_number": "+79136557877",
            "password": "user_password1",
        }
        response = self.client.post(url, data)
        expected_data = 3

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), expected_data)

    def test_login_account(self):
        """This test covers user account login"""

        url = reverse("token_obtain_pair")
        data = {
            "phone_number": "+79136757877",
            "password": "admin_password1",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_account(self):
        """This test covers user account logout"""

        url = reverse("token_blacklist")
        self.refresh_token = str(RefreshToken.for_user(self.superuser))
        self.access_token = str(RefreshToken.for_user(self.superuser).access_token)
        data = {"refresh": self.refresh_token}
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        invalid_response = self.client.post(reverse("token_blacklist"), data)
        self.assertEqual(invalid_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_account(self):
        """This test covers account profile"""

        url = f"{settings.DOMAIN_NAME}/auth/users/me/"
        response = self.client.get(url)
        expected_data = 1

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["phone_number"], self.superuser.phone_number)
        self.assertEqual(len([response.data]), expected_data)



class ScheduleAPITestCase(APITestCase):
    def setUp(self):
        """data for test schedule db"""

        self.coach = User.objects.create_user(
            phone_number="+79136757878",
            password="nik140406"
        )

        self.schedule_1 = Schedule.objects.create(
            time="2024-02-02 14:50",
            is_selected="False",
            coach=self.coach
        )

        self.access_token = str(RefreshToken.for_user(self.superuser).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_create_account(self):
        """This test covers registration"""

        url = f"{settings.DOMAIN_NAME}/auth/users/"
        data = {
            "phone_number": "+79136557877",
            "password": "user_password1",
        }
        response = self.client.post(url, data)
        expected_data = 3

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), expected_data)