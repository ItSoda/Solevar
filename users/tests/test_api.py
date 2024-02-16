from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import PhoneNumberVerifySMS, Schedule, User


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


class ScheduleAndCoachAPITestCase(APITestCase):
    def setUp(self):
        """data for test schedule db"""

        self.coach_1 = User.objects.create_user(
            phone_number="+79136757878",
            password="nik140406",
            role="Coach",
        )

        self.coach_2 = User.objects.create_user(
            phone_number="+79136757879",
            password="nik140406",
            role="Coach",
        )

        self.schedule_1 = Schedule.objects.create(
            time=timezone.now(),
            is_selected="False",
        )
        self.schedule_1.coach.add(self.coach_1)

        self.schedule_3 = Schedule.objects.create(
            time=timezone.now(),
            is_selected="False",
        )
        self.schedule_3.coach.add(self.coach_1)

        self.schedule_2 = Schedule.objects.create(
            time=timezone.now(),
            is_selected="False",
        )
        self.schedule_2.coach.add(self.coach_2)

        self.access_token = str(RefreshToken.for_user(self.coach_1).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_trainer_panel_schedule_list(self):
        """This test covers schedule list"""

        url = f"{settings.DOMAIN_NAME}/api/schedules/"
        response = self.client.get(url)
        expected_data = 2

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), expected_data)

    def test_individual_event_schedule_list_with_trainer(self):
        """This test covers schedule list with trainer"""

        url = (
            f"{settings.DOMAIN_NAME}/api/individual_event_schedules/{self.coach_1.id}/"
        )
        response = self.client.get(url)
        expected_data = 2

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), expected_data)

    def test_individual_event_schedule_list_without_trainer(self):
        """This test covers schedule list with trainer"""

        url = f"{settings.DOMAIN_NAME}/api/individual_event_schedules/"
        response = self.client.get(url)
        expected_data = 3

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), expected_data)

    def test_schedule_create(self):
        """This test covers schedule create"""

        url = f"{settings.DOMAIN_NAME}/api/schedule/"
        data = {
            "time": "2024-02-02 18:00",
            "coach": [self.coach_1.id],
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["time"], "2024-02-02 18:00")

    def test_schedule_update(self):
        """This test covers schedule update"""

        url = f"{settings.DOMAIN_NAME}/api/schedule/{self.schedule_1.id}/"
        data = {
            "time": "2024-02-04 19:00",
        }
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["time"], "2024-02-04 19:00")

    def test_schedule_destroy(self):
        """This test covers schedule destroy"""

        url = f"{settings.DOMAIN_NAME}/api/schedule/{self.schedule_1.id}/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Schedule.objects.count(), 3)

    def test_coaches_list(self):
        """This test covers schedules list"""

        url = f"{settings.DOMAIN_NAME}/api/coaches/"
        response = self.client.get(url)
        expected_data = 2

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), expected_data)

    def test_coaches_list_with_time(self):
        """This test covers coaches list with time"""

        url = f"{settings.DOMAIN_NAME}/api/coaches/{self.schedule_1.time}/"
        response = self.client.get(url)
        expected_data = 1

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), expected_data)
