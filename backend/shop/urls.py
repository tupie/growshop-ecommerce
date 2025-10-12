from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CartViewSet,
    CategoryViewSet,
    OrderItemViewSet,
    OrderViewSet,
    ProductViewSet,
    ReviewViewSet,
    checkout,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("products", ProductViewSet)
router.register("reviews", ReviewViewSet)
router.register("orders", OrderViewSet, basename="order")  # 👈 correcto
router.register("order-items", OrderItemViewSet)
router.register("cart", CartViewSet, basename="cart")

urlpatterns = [
    path("", include(router.urls)),
    path("checkout/", checkout, name="checkout"),
]
