import shutil

from accounts.models import User
from core.settings import TEST_DIR
from core.tests_utils import (
    album_add_access_detail_url,
    album_detail_url,
    album_image_list_url,
    album_images_detail_url,
    album_list_url,
    create_user,
    generate_photo_file,
)
from rest_framework import status
from rest_framework.test import APITestCase


class TestAlbumViewSetCreateDestroy(APITestCase):
    data = {"name": "NAME"}

    def setUp(self):
        self.user = User.objects.create_user(email="test@test.com", password="123")
        self.client.force_authenticate(user=self.user)
        self.user.is_vendor = True

    def test_album_create(self):
        response = self.client.post(album_list_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_album_create_other_user_parent_album(self):
        user = create_user()
        user.is_vendor = True
        self.client.force_authenticate(user=user)
        response = self.client.post(album_list_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        other_album_id = response.json()["id"]

        self.client.force_authenticate(user=self.user)
        data = self.data.copy()
        data["parent_album"] = other_album_id
        response = self.client.post(album_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_album_create_is_not_vendor(self):
        self.user.is_vendor = False
        response = self.client.post(album_list_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_album_create_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(album_list_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_album_create_destroy(self):
        response = self.client.post(album_list_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        album_id = response.json()["id"]
        response = self.client.delete(album_detail_url(album_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_album_destroy_other_user_album(self):
        response = self.client.post(album_list_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        album_id = response.json()["id"]
        user = create_user()
        self.client.force_authenticate(user=user)
        response = self.client.delete(album_detail_url(album_id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        user.is_vendor = True
        self.client.force_authenticate(user=user)
        response = self.client.delete(album_detail_url(album_id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_album_create_child_album(self):
        response = self.client.post(album_list_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        album_id = response.json()["id"]
        data = self.data.copy()
        data["parent_album"] = album_id
        response = self.client.post(album_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_album_destroy_with_child_album(self):
        response = self.client.post(album_list_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        album_id = response.json()["id"]
        data = self.data.copy()
        data["parent_album"] = album_id
        response = self.client.post(album_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        child_album_id = response.json()["id"]
        response = self.client.delete(album_detail_url(album_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.delete(album_detail_url(child_album_id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestAlbumViewSetUpdate(APITestCase):
    data = {"name": "NAME"}

    def setUp(self):
        self.user = User.objects.create_user(email="test@test.com", password="123")
        self.client.force_authenticate(user=self.user)
        self.user.is_vendor = True
        response = self.client.post(album_list_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.album_id = response.json()["id"]

    def test_album_partial_update_name(self):
        data = {"name": "NEW_NAME"}
        response = self.client.patch(album_detail_url(self.album_id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        name = response.json()["name"]
        self.assertEqual(name, data["name"])

    def test_album_partial_update_parent_album(self):
        response = self.client.post(album_list_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        album_id = response.json()["id"]
        data = {"parent_album": self.album_id}
        response = self.client.patch(album_detail_url(album_id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        name = response.json()["parent_album"]
        self.assertEqual(name, data["parent_album"])

    def test_album_partial_update_is_public(self):
        data = {"is_public": True}
        response = self.client.patch(album_detail_url(self.album_id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        name = response.json()["is_public"]
        self.assertEqual(name, data["is_public"])

    def test_album_partial_update_all(self):
        response = self.client.post(album_list_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        album_id = response.json()["id"]
        data = {"name": "NEW_NAME", "is_public": True, "parent_album": self.album_id}
        response = self.client.patch(album_detail_url(album_id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        response_data.pop("id")
        self.assertEqual(response_data, data)


class TestAlbumAllowedUsersViewSet(APITestCase):
    data = {"name": "NAME"}

    def setUp(self):
        self.user = User.objects.create_user(email="test@test.com", password="123")
        self.client.force_authenticate(user=self.user)
        self.user.is_vendor = True
        response = self.client.post(album_list_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.album_id = response.json()["id"]
        response = self.client.post(album_image_list_url(self.album_id), {"image": generate_photo_file()})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        try:
            shutil.rmtree(TEST_DIR)
        except OSError:
            pass

    def test_album_allowed_users_add_remove_access(self):
        user = create_user()
        url = album_add_access_detail_url(self.album_id, user.id)
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        url = album_add_access_detail_url(self.album_id, self.user.id)
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_album_allowed_users_accessing(self):
        user = create_user()
        self.client.force_authenticate(user=user)
        response = self.client.get(album_detail_url(self.album_id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.user)
        response = self.client.put(album_add_access_detail_url(self.album_id, user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=user)
        response = self.client.get(album_detail_url(self.album_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_album_allowed_users_accessing_image(self):
        user = create_user()
        response = self.client.put(album_add_access_detail_url(self.album_id, user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=user)
        response = self.client.get(album_detail_url(self.album_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        image_url = response.json()["images"][0]["url"]
        response = self.client.get(image_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(album_add_access_detail_url(self.album_id, user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=user)
        response = self.client.get(image_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestAlbumImageViewSet(APITestCase):
    data = {"name": "NAME"}

    def setUp(self):
        self.user = User.objects.create_user(email="test@test.com", password="123")
        self.client.force_authenticate(user=self.user)
        self.user.is_vendor = True
        response = self.client.post(album_list_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.album_id = response.json()["id"]
        response = self.client.post(album_image_list_url(self.album_id), {"image": generate_photo_file()})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.image_id = response.json()["id"]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        try:
            shutil.rmtree(TEST_DIR)
        except OSError as err:
            pass

    def test_album_image_public_access(self):
        data = {"is_public": True}
        response = self.client.patch(album_detail_url(self.album_id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        name = response.json()["is_public"]
        self.assertEqual(name, data["is_public"])
        self.client.force_authenticate(user=None)
        response = self.client.get(album_detail_url(self.album_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        image_url = response.json()["images"][0]["url"]
        response = self.client.get(image_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=self.user)
        data = {"is_public": False}
        response = self.client.patch(album_detail_url(self.album_id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=None)
        response = self.client.get(image_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(user=create_user())
        response = self.client.get(image_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(image_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_album_image_create(self):
        user = create_user()
        response = self.client.put(album_add_access_detail_url(self.album_id, user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=user)
        response = self.client.post(album_image_list_url(self.album_id), {"image": generate_photo_file()})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_album_image_update(self):
        data = {"title": "new title"}
        response = self.client.patch(album_images_detail_url(self.album_id, self.image_id), data)
        self.assertEqual(response.json()["title"], data["title"])
        user = create_user()
        self.client.force_authenticate(user=user)
        response = self.client.patch(album_images_detail_url(self.album_id, self.image_id), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_album_image_delete(self):
        user = create_user()
        response = self.client.put(album_add_access_detail_url(self.album_id, user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=user)
        response = self.client.delete(album_images_detail_url(self.album_id, self.image_id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(album_images_detail_url(self.album_id, self.image_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
