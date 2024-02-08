from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from gym_management.models import Event, IndividualEvent, Subscription, Tag
from users.models import Schedule, User


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

        self.tag = Tag.objects.create(name="Предварительная запись")

        self.event = Event.objects.create(
            title="ЙОГА",
            content="ЙОГА РЕКОРД",
            limit_of_participants=6,
            start_date=timezone.now(),
            duration=50,
            created_by=self.coach_1,
            club="RECORD",
            price=1000,
            status="WAITING",
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
            status="PASSED",
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
        self.assertEqual(
            response.data["message"], "Participant removed and funds returned"
        )
        self.assertEqual(self.event.participants.count(), 2)

    def test_my_events_list(self):
        """This test covers my events list"""

        self.event.participants.add(self.superuser)

        url = f"{settings.DOMAIN_NAME}/api/my_events/"
        response = self.client.get(url)
        expected_data = 1

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), expected_data)


class SubscriptionAPITestCase(APITestCase):
    def setUp(self):
        """data for test subscriptions"""

        self.superuser = User.objects.create_superuser(
            phone_number="+79136757877",
            password="admin_password1",
            balance=1000,
        )
        self.user = User.objects.create_user(
            phone_number="+79136757873",
            password="user_password1",
            balance=1000,
        )

        self.access_token = str(RefreshToken.for_user(self.superuser).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        self.subscription_1 = Subscription.objects.create(
            number="1111111",
            user=self.user,
            duration=1,
        )

        self.subscription_2 = Subscription.objects.create(
            number="1111112",
            user=self.superuser,
            duration=1,
        )

    def test_buy_subscription(self):
        """This test covers buy subscription"""

        # Positive test
        url = f"{settings.DOMAIN_NAME}/api/buy_subscription/"
        data = {
            "price": 1000,
            "duration": 1,
        }
        response = self.client.post(url, data)
        expected_data = 2

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Buy Subscription success")
        self.assertEqual(
            Subscription.objects.filter(user=self.superuser).count(), expected_data
        )

        # Negative test
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Insufficient balance")
        self.assertEqual(
            Subscription.objects.filter(user=self.superuser).count(), expected_data
        )

    def test_subscription_list(self):
        """This test covers my subscriptions list"""

        url = f"{settings.DOMAIN_NAME}/api/my_subscriptions/"

        response = self.client.get(url)
        expected_data = 1

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Subscription.objects.filter(user=self.superuser).count(), expected_data
        )


class IndividualEventAPITestCase(APITestCase):
    def setUp(self):
        """data for test individual event"""

        self.superuser = User.objects.create_superuser(
            phone_number="+79136757877",
            password="admin_password1",
            balance=1000,
        )

        self.access_token = str(RefreshToken.for_user(self.superuser).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        self.user = User.objects.create_superuser(
            phone_number="+79136757833",
            password="user_password1",
            balance=1000,
        )

        self.coach = User.objects.create_user(
            phone_number="+79136757873",
            password="user_password1",
            balance=1000,
            role="Coach",
        )

        self.schedule = Schedule.objects.create(
            time="2024-02-02 14:00",
        )
        self.schedule.coach.add(self.coach)

        self.individual_event = IndividualEvent.objects.create(
            coach=self.coach,
            participant=self.user,
            training_date=timezone.now(),
            duration=60,
            quantity=1,
            price=1000,
        )

    def test_buy_individual_event(self):
        """This test covers buy individual_event"""

        # Positive test
        url = f"{settings.DOMAIN_NAME}/api/create/individual_events/"
        data = {
            "coach": self.coach.id,
            "training_date": "2024-02-02 14:00",
            "duration": 60,
            "quantity": 1,
            "price": 1000,
        }

        response = self.client.post(url, data)
        expected_data = 1

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Success buy individual event")
        self.assertEqual(
            IndividualEvent.objects.filter(participant=self.superuser).count(),
            expected_data,
        )

        # Negative test
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"],
            "Not enough money or individual event already create",
        )
        self.assertEqual(
            IndividualEvent.objects.filter(participant=self.superuser).count(),
            expected_data,
        )

    def test_individual_event_list(self):
        """This test covers individual event list"""

        url = f"{settings.DOMAIN_NAME}/api/my_individual_events/"
        response = self.client.get(url)
        expected_data = 1

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            IndividualEvent.objects.filter(participant=self.user).count(), expected_data
        )


class TrainerPanelAPITestCase(APITestCase):
    def setUp(self):
        """data for test trainer panel"""

        self.coach = User.objects.create_user(
            phone_number="+79136757877",
            password="admin_password1",
            balance=1000,
            role="COACH",
        )

        self.access_token = str(RefreshToken.for_user(self.coach).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        self.user = User.objects.create_superuser(
            phone_number="+79136757833",
            password="user_password1",
            balance=1000,
        )

        self.schedule = Schedule.objects.create(
            time="2024-02-02 14:00",
        )
        self.schedule.coach.add(self.coach)

        self.individual_event = IndividualEvent.objects.create(
            coach=self.coach,
            participant=self.user,
            training_date=timezone.now(),
            duration=60,
            quantity=1,
            price=1000,
        )

        self.tag = Tag.objects.create(name="Предварительная запись")

        self.event = Event.objects.create(
            title="ЙОГА",
            content="ЙОГА РЕКОРД",
            limit_of_participants=6,
            start_date=timezone.now(),
            duration=50,
            created_by=self.coach,
            club="RECORD",
            price=1000,
            status="WAITING",
        )

        self.event.tags.add(self.tag)
        self.event.participants.add(self.user)
        self.event.participants.add(self.coach)

    def test_trainer_event_list(self):
        """This test covers trainer event list"""

        url = f"{settings.DOMAIN_NAME}/api/trainer_events/"

        response = self.client.get(url)
        expected_data = 1

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), expected_data)

    def test_trainer_individual_event_list(self):
        """This test covers trainer individual event list"""

        url = f"{settings.DOMAIN_NAME}/api/trainer_list_individual_event/"

        response = self.client.get(url)
        expected_data = 1

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), expected_data)

    def test_trainer_event_create(self):
        """This test covers trainer event create"""

        url = f"{settings.DOMAIN_NAME}/api/trainer_events/"
        data = {
            "title": "ЙОГА2",
            "content": "ЙОГА РЕКОРД2",
            "limit_of_participants": 12,
            "start_date": timezone.now(),
            "duration": 100,
            "price": 2000,
            "tags": [self.tag.id],
        }
        response = self.client.post(url, data)
        expected_data = 2

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), expected_data)

    def test_trainer_event_update(self):
        """This test covers trainer event update"""

        url = f"{settings.DOMAIN_NAME}/api/trainer_events/{self.event.id}/"
        data = {
            "status": "passed",
        }
        response = self.client.patch(url, data)
        expected_data = 1
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Event.objects.count(), expected_data)

    def test_trainer_event_delete(self):
        """This test covers trainer event delete"""

        url = f"{settings.DOMAIN_NAME}/api/trainer_events/{self.event.id}/"

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Event.objects.count(), 0)
