from io import BytesIO

from accounts.models import User
from PIL import Image
from rest_framework.reverse import reverse

album_list_url = reverse("album-list")
profile_list_url = reverse("profile-list")
order_list_url = reverse("order-list")


def order_detail_url(pk):
    return reverse("order-detail", kwargs={"pk": pk})


def order_note_list_url(order_pk):
    return reverse("order-notes-list", kwargs={"order_pk": order_pk})


def order_note_detail_url(order_pk, pk):
    return reverse("order-notes-detail", kwargs={"order_pk": order_pk, "pk": pk})


def album_images_detail_url(album_pk, pk):
    return reverse("album-images-detail", kwargs={"album_pk": album_pk, "pk": pk})


def album_detail_url(pk):
    return reverse("album-detail", kwargs={"pk": pk})


def album_add_access_detail_url(album_pk, pk):
    return reverse("album-add-access-detail", kwargs={"album_pk": album_pk, "pk": pk})


def album_image_list_url(album_pk):
    return reverse(
        "album-images-list",
        kwargs={
            "album_pk": album_pk,
        },
    )


def create_user(email="test2@test.com", **kwargs):
    return User.objects.create_user(email=email, password="123", **kwargs)


def generate_photo_file(x=100, y=100):
    file = BytesIO()
    image = Image.new("RGBA", size=(x, y), color=(155, 0, 0))
    image.save(file, "png")
    file.name = "test.png"
    file.seek(0)
    return file
