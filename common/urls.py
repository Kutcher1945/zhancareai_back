from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, UserViewSet

router = DefaultRouter()
router.register(r'auth', UserViewSet, basename='user')
router.register(r'user-profile', UserProfileViewSet, basename='user-profile')

urlpatterns = [
    path('', include(router.urls)),
]
