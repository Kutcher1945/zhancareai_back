from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserProfileViewSet, ConsultationViewSet

router = DefaultRouter()
router.register(r'auth', UserViewSet, basename='user')
router.register(r'user-profile', UserProfileViewSet, basename='user-profile')
router.register(r'consultations', ConsultationViewSet, basename='consultations')

urlpatterns = [
    path('', include(router.urls)),
]
