"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from album.views import AlbumViewset, AllowedUsersViewSet, ImageViewset
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from order.views import NoteViewSet, OrderViewSet
from rest_framework_nested import routers

router = routers.SimpleRouter()

router.register(r"orders", OrderViewSet)
router.register(r"albums", AlbumViewset)
router.register(r"images", ImageViewset)

notes_router = routers.NestedSimpleRouter(router, r"orders", lookup="order")
notes_router.register(r"notes", NoteViewSet, basename="order-notes")

allowed_users_router = routers.NestedSimpleRouter(router, r"albums", lookup="album")
allowed_users_router.register(r"access", AllowedUsersViewSet, basename="album-add-access")

images_router = routers.NestedSimpleRouter(router, r"albums", lookup="album")
images_router.register(r"images", ImageViewset, basename="album-images")

urlpatterns = (
    [
        path("admin/", admin.site.urls),
        # path("user/", include("user.urls")),
        path("auth/", include("djoser.urls")),
        path("auth/", include("djoser.urls.jwt")),
        # path("auth/", include("djoser.urls.authtoken")),
    ]
    + router.urls
    + notes_router.urls
    + allowed_users_router.urls
    + images_router.urls
    + static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
)

print(images_router.urls)
