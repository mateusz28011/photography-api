import shutil

from core.settings import TEST_DIR
from core.tests_utils import (
    album_image_list_url,
    album_list_url,
    create_user,
    generate_photo_file,
    order_detail_url,
    order_list_url,
    order_note_detail_url,
    order_note_list_url,
)
from rest_framework import status
from rest_framework.test import APITestCase


class TestOrderViewset(APITestCase):
    def setUp(self):
        self.vendor = create_user("test@test.com", is_vendor=True)
        self.user = create_user("user@test.com")
        self.client.force_authenticate(user=self.user)
        self.data = {"vendor": self.vendor.id, "description": "DESC"}
        response = self.client.post(order_list_url, self.data)
        self.order_id = response.json()["id"]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.order_url = order_detail_url(self.order_id)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        try:
            shutil.rmtree(TEST_DIR)
        except OSError:
            pass

    def test_order_create(self):
        self.vendor.is_vendor = False
        self.vendor.save()
        response = self.client.post(order_list_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_client_album_access(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.post(album_list_url, {"name": "NAME"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        album_id = response.json()["id"]
        response = self.client.patch(self.order_url, {"album": album_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(album_image_list_url(album_id), {"image": generate_photo_file()})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.order_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        image_url = response.json()["album"]["images"][0]["url"]
        response = self.client.get(image_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_update_client_status(self):
        for i in range(1, 7):
            response = self.client.patch(self.order_url, {"status": i})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(self.order_url, {"status": 0})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_update_client_forbidden(self):
        response = self.client.patch(self.order_url, {"album": 2})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(self.order_url, {"cost": 1})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(self.order_url, {"currency": 2})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_update_vendor_album(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.post(album_list_url, {"name": "NAME"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        album_id = response.json()["id"]
        response = self.client.patch(self.order_url, {"album": album_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_update_vendor_cost(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.patch(self.order_url, {"cost": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_update_vendor_currency(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.patch(self.order_url, {"currency": 2})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(self.order_url, {"currency": "PLN"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"currency": "EUR"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"currency": "USD"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_update_vendor_status_waiting_for_acceptance_to_rejected(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.patch(self.order_url, {"status": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_update_vendor_status_waiting_for_acceptance_to_accepted(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.patch(self.order_url, {"status": 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_update_vendor_status_waiting_for_acceptance_to_forbidden(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.patch(self.order_url, {"status": 0})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(self.order_url, {"status": 2})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(self.order_url, {"status": 4})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(self.order_url, {"status": 5})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(self.order_url, {"status": 6})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_update_vendor_status_accepted_to_canceled(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.patch(self.order_url, {"status": 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"status": 0})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_update_vendor_status_accepted_to_waiting_for_payment(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.patch(self.order_url, {"status": 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"status": 4})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(self.order_url, {"status": 4, "cost": 100})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_update_vendor_status_accepted_to_waiting_for_finished(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.patch(self.order_url, {"status": 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"status": 6})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_update_vendor_status_waiting_for_acceptance_to_forbidden(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.patch(self.order_url, {"status": 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"status": 1})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(self.order_url, {"status": 2})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(self.order_url, {"status": 3})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(self.order_url, {"status": 5})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_update_vendor_status_waiting_for_payment_to_payment_received(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.patch(self.order_url, {"status": 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"status": 4, "cost": 100})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"status": 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_update_vendor_status_waiting_for_payment_to_finished(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.patch(self.order_url, {"status": 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"status": 4, "cost": 100})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"status": 6})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_update_vendor_status_waiting_for_payment_to_canceled(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.patch(self.order_url, {"status": 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"status": 4, "cost": 100})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"status": 0})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_update_vendor_status_waiting_for_payment_to_forbidden(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.patch(self.order_url, {"status": 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"status": 4, "cost": 100})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"status": 4})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(self.order_url, {"status": 1})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(self.order_url, {"status": 2})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(self.order_url, {"status": 3})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_update_vendor_status_payment_received_to_canceled(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.patch(self.order_url, {"status": 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"status": 4, "cost": 100})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"status": 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"status": 0})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_update_vendor_status_payment_received_to_finished(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.patch(self.order_url, {"status": 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"status": 4, "cost": 100})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"status": 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"status": 6})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_update_vendor_status_payment_received_to_forbidden(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.patch(self.order_url, {"status": 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"status": 4, "cost": 100})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"status": 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(self.order_url, {"status": 1})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(self.order_url, {"status": 2})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(self.order_url, {"status": 3})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(self.order_url, {"status": 4})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(self.order_url, {"status": 5})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_update_vendor_status_payment_finished_to_forbidden(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.patch(self.order_url, {"status": 3})
        response = self.client.patch(self.order_url, {"status": 6})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in range(7):
            response = self.client.patch(self.order_url, {"status": i})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_update_vendor_status_payment_canceled_to_forbidden(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.patch(self.order_url, {"status": 3})
        response = self.client.patch(self.order_url, {"status": 0})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in range(7):
            response = self.client.patch(self.order_url, {"status": i})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_update_vendor_status_payment_rejected_to_forbidden(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.patch(self.order_url, {"status": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i in range(7):
            response = self.client.patch(self.order_url, {"status": i})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestOrderNoteViewset(APITestCase):
    data_note = {"note": "NOTE"}

    def setUp(self):
        self.vendor = create_user("test@test.com", is_vendor=True)
        self.user = create_user("user@test.com")
        self.client.force_authenticate(user=self.user)
        self.data = {"vendor": self.vendor.id, "description": "DESC"}
        response = self.client.post(order_list_url, self.data)
        self.order_id = response.json()["id"]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.order_url = order_detail_url(self.order_id)
        self.order_note_url = order_note_list_url(self.order_id)

    def test_order_note_client_create(self):
        response = self.client.post(self.order_note_url, self.data_note)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_order_note_client_update(self):
        response = self.client.post(self.order_note_url, self.data_note)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_order_note_vendor_create(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.post(self.order_note_url, self.data_note)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        note_id = response.json()["id"]
        response = self.client.patch(order_note_detail_url(self.order_id, note_id), self.data_note)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_note_vendor_update(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.post(self.order_note_url, self.data_note)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        note_id = response.json()["id"]
        response = self.client.patch(order_note_detail_url(self.order_id, note_id), self.data_note)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
