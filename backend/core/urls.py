from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.views_health import health

# --------------------------------------------------
# URL patterns
# --------------------------------------------------
urlpatterns = [
    # Panel de administración
    path("admin/", admin.site.urls),
    # Endpoint de salud (💚 lo movemos arriba)
    path("api/health/", health),
    # Esquema OpenAPI JSON
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI (sin sidecar)
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Redoc UI
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Endpoints de autenticación JWT
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Endpoints principales
    path("api/", include("shop.urls")),
    path("api/", include("jwtcheck.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
