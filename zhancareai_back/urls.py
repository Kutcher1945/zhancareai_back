from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static


# Define the Swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title="ZhanCare.AI Backend API",
        default_version="v1",
        description=(
            "ZhanCare.AI provides a comprehensive API for telemedicine solutions, enabling remote medical consultations, "
            "secure patient-doctor communication, AI-driven medical insights, and efficient healthcare management. "
            "This API allows seamless integration with ZhanCare.AI's platform, facilitating access to video conferencing, "
            "electronic medical records, notifications, and advanced AI-powered tools."
        ),
        terms_of_service="https://www.zhancare.ai/terms/",
        contact=openapi.Contact(email="support@zhancare.ai"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("common.urls")),  # Include the common app's URLs

    # Swagger and ReDoc routes
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]


# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)