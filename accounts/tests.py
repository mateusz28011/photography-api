import shutil

from core.settings import TEST_DIR
from core.tests_utils import generate_photo_file, profile_list_url
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from .models import User


class TestProfileViewset(APITestCase):
    

    def setUp(self):
        self.user = User.objects.create_user(email="test@test.com", password="123")
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        if hasattr(self.user, "profile"):
            if self.user.profile.avatar != "default/avatar.png":
                self.user.profile.avatar.delete()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        try:
            shutil.rmtree(TEST_DIR)
        except OSError:
            pass

    def test_profile_create_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {"description": "DESC", "name": "NAME", "payment_info": "INFORMATION"}
        response = self.client.post(profile_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_create(self):
        data = {"description": "DESC", "name": "NAME", "payment_info": "INFORMATION"}
        response = self.client.post(profile_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_profile_create_with_avatar(self):
        image = generate_photo_file()
        data = {"description": "DESC", "name": "NAME", "payment_info": "INFORMATION", "avatar": image}
        response = self.client.post(profile_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_profile_create_with_too_big_avatar(self):
        image = generate_photo_file(x=600)
        data = {"description": "DESC", "name": "NAME", "payment_info": "INFORMATION", "avatar": image}
        response = self.client.post(profile_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_create_has_profile(self):
        self.test_profile_create()
        data = {"description": "DESC", "name": "NAME", "payment_info": "INFORMATION"}
        response = self.client.post(profile_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_profile_put(self):
        data = {"description": "DESC", "name": "NAME", "payment_info": "INFORMATION"}
        response = self.client.post(profile_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        profile_id = response.json()["id"]
        data = {"description": "DESC", "name": "NAME", "payment_info": "INFORMATION"}
        response = self.client.put(reverse("profile-detail", kwargs={"pk": profile_id}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = {"description": "DESC"}
        response = self.client.put(reverse("profile-detail", kwargs={"pk": profile_id}), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_patch(self):
        data = {"description": "DESC", "name": "NAME", "payment_info": "INFORMATION"}
        response = self.client.post(profile_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        profile_id = response.json()["id"]
        data = {"description": "DESC", "name": "NAME"}
        response = self.client.patch(reverse("profile-detail", kwargs={"pk": profile_id}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = {"description": "DESC"}
        response = self.client.patch(reverse("profile-detail", kwargs={"pk": profile_id}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        avatar = generate_photo_file()
        data = {"avatar": avatar}
        response = self.client.patch(reverse("profile-detail", kwargs={"pk": profile_id}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()

    def test_profile_patch_unauthenticated(self):
        data = {"description": "DESC", "name": "NAME", "payment_info": "INFORMATION"}
        response = self.client.post(profile_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        profile_id = response.json()["id"]
        data = {"description": "DESC", "name": "NAME"}
        self.client.force_authenticate(user=None)
        response = self.client.patch(reverse("profile-detail", kwargs={"pk": profile_id}), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_put_unauthenticated(self):
        data = {"description": "DESC", "name": "NAME", "payment_info": "INFORMATION"}
        response = self.client.post(profile_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        profile_id = response.json()["id"]
        data = {"description": "DESC", "name": "NAME", "payment_info": "INFORMATION"}
        self.client.force_authenticate(user=None)
        response = self.client.put(reverse("profile-detail", kwargs={"pk": profile_id}), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_retrieve(self):
        data = {"description": "DESC", "name": "NAME", "payment_info": "INFORMATION"}
        response = self.client.post(profile_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        profile_id = response.json()["id"]
        response = self.client.get(reverse("profile-detail", kwargs={"pk": profile_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("profile-detail", kwargs={"pk": profile_id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_list(self):
        self.test_profile_create()
        response = self.client.get(profile_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=None)
        response = self.client.get(profile_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_put_other_user(self):
        data = {"description": "DESC", "name": "NAME", "payment_info": "INFORMATION"}
        response = self.client.post(profile_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        profile_id = response.json()["id"]
        self.client.force_authenticate(user=User.objects.create_user(email="test2@test.com", password="123"))
        data = {"description": "DESC", "name": "NAME"}
        response = self.client.put(reverse("profile-detail", kwargs={"pk": profile_id}), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_profile_patch_other_user(self):
        data = {"description": "DESC", "name": "NAME", "payment_info": "INFORMATION"}
        response = self.client.post(profile_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        profile_id = response.json()["id"]
        self.client.force_authenticate(user=User.objects.create_user(email="test2@test.com", password="123"))
        data = {"description": "DESC", "name": "NAME"}
        response = self.client.patch(reverse("profile-detail", kwargs={"pk": profile_id}), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
