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
from accounts.views import ProfileViewSet, UserViewSet
from album.views import AlbumViewset, AllowedUsersViewSet, ImageViewset
from dj_rest_auth.registration.views import ConfirmEmailView, VerifyEmailView
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from order.views import NoteViewSet, OrderViewSet
from rest_framework import permissions
from rest_framework_nested import routers

schema_view = get_schema_view(
    openapi.Info(
        title="Photography API",
        default_version="v1",
        description="""
        #### How to start?
        1. Create your account through **_POST /auth/users_**.
        2. Activate your account by clicking link sent to your e-mail.
        3. Create your access token through **_POST /auth/jwt/create_**.
        4. Authorize yourself by clicking green button below. In value field paste your token as **_JWT \{token\}_**.
        5. Now you are ready to go!
        """,
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="mathew28011@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

router = routers.SimpleRouter()

router.register(r"orders", OrderViewSet)
router.register(r"albums", AlbumViewset)
router.register(r"profiles", ProfileViewSet)
router.register(r"dj-rest-auth/users", UserViewSet)

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
        path("", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
        path("dj-rest-auth/", include("dj_rest_auth.urls")),
        path(
            "dj-rest-auth/registration/account-confirm-email/<str:key>/",
            ConfirmEmailView.as_view(),
        ),
        path("dj-rest-auth/registration/", include("dj_rest_auth.registration.urls")),
        path(
            "dj-rest-auth/account-confirm-email/",
            VerifyEmailView.as_view(),
            name="account_email_verification_sent",
        ),
        # path(
        #     "dj-rest-auth/account-confirm-email/<str:key>/",
        #     VerifyEmailView.as_view(),
        #     name="account_email_verification_sent",
        # ),
        # path("accounts/", include("allauth.urls")),
        # path("auth/", include("djoser.urls")),
        # path("auth/", include("djoser.urls.jwt")),
        # path("auth/", include("djoser.urls.authtoken")),
        # path("auth/activate/<str:uid>/<str:token>/", UserActivationView.as_view()),
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
# from djoser import urls

# print(images_router.urls)
