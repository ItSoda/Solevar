from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from gym_management.models import Event, Tag
from users.models import User
from django.utils import timezone


class EventAPITestCase(APITestCase):
    def setUp(self):
        """data for test db"""

        self.superuser = User.objects.create_superuser(
            phone_number="+79136757877",
            password="admin_password1",
            balance=100000,
        )

        self.access_token = str(RefreshToken.for_user(self.superuser).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        self.coach_1 = User.objects.create_user(
            phone_number="+79136757878",
            password="nik140406",
            role="Coach",
        )

        self.user = User.objects.create_user(
            phone_number="+79136757879",
            password="nik140406",
            role="Coach",
        )   

        self.tag = Tag.objects.create(
            name="Предварительная запись"
        )

        self.event = Event.objects.create(
            title="ЙОГА",
            content="ЙОГА РЕКОРД",
            limit_of_participants=6,
            start_date=timezone.now(),
            duration=50,
            created_by=self.coach_1,
            club="RECORD",
            price=1000,
            status="WAITING"
        )

        self.event.tags.add(self.tag)
        self.event.participants.add(self.user)
        self.event.participants.add(self.coach_1)

        self.event_2 = Event.objects.create(
            title="ЙОГА2",
            content="ЙОГА РЕКОРД2",
            limit_of_participants=8,
            start_date=timezone.now(),
            duration=70,
            created_by=self.coach_1,
            club="RECORD2",
            price=2000,
            status="PASSED"
        )

        self.event.tags.add(self.tag)
        self.event.participants.add(self.user)
        self.event.participants.add(self.coach_1)


    def test_events_list(self):
        """This test covers events list"""

        url = f"{settings.DOMAIN_NAME}/api/events/"
        response = self.client.get(url)
        expected_data = 1

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), expected_data)

    def test_add_or_remove_participant(self):
        """This test covers events add or remove participant"""

        url = f"{settings.DOMAIN_NAME}/api/join_event/"
        data = {
            "pk": self.event.id,
        }
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Participant added")
        self.assertEqual(self.event.participants.count(), 3)

        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Participant removed and funds returned")
        self.assertEqual(self.event.participants.count(), 2)


    def test_my_events_list(self):
        """This test covers my events list"""

        self.event.participants.add(self.superuser)

        url = f"{settings.DOMAIN_NAME}/api/my_events/"
        response = self.client.get(url)
        expected_data = 1

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), expected_data)

    def test_history_events_list(self):
        """This test covers events list"""

        self.event.status = "PASSED"

        url = f"{settings.DOMAIN_NAME}/api/events/"
        response = self.client.get(url)
        expected_data = 1

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), expected_data)