from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Panel admin
    path("admin/", admin.site.urls),
    # Esquema OpenAPI JSON
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI (sin sidecar)
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Redoc
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    # API principal
    path("api/", include("shop.urls")),
]
