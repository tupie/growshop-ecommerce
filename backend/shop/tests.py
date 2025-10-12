from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ProductViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet)
router.register(r"products", ProductViewSet)
router.register(r"reviews", ReviewViewSet)

urlpatterns = router.urls
