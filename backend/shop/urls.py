from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .views import checkout

router = DefaultRouter()
router.register(r"categories", views.CategoryViewSet)
router.register(r"products", views.ProductViewSet)
router.register(r"reviews", views.ReviewViewSet)
router.register(r"orders", views.OrderViewSet)
router.register(r"order-items", views.OrderItemViewSet)
router.register(r"cart", views.CartViewSet, basename="cart")


urlpatterns = router.urls + [
    path("checkout/", checkout, name="checkout"),
]
