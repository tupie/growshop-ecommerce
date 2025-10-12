from decimal import Decimal

from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Cart, CartItem, Category, Order, OrderItem, Product, Review
from .serializers import (
    CartSerializer,
    CategorySerializer,
    OrderItemSerializer,
    OrderSerializer,
    ProductSerializer,
    ReviewSerializer,
)


# --------------------------------------------------
# Category
# --------------------------------------------------
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name"]
    permission_classes = [permissions.AllowAny]


# --------------------------------------------------
# Product
# --------------------------------------------------
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category__slug"]
    search_fields = ["name", "meta_title", "meta_description"]
    ordering_fields = ["price", "name", "created_at"]
    permission_classes = [permissions.AllowAny]


# --------------------------------------------------
# Review
# --------------------------------------------------
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related("product", "user").all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# --------------------------------------------------
# Order
# --------------------------------------------------
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related("items").all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request):
        """
        ✅ Devuelve el historial de pedidos del usuario autenticado.
        Admite filtro opcional por estado: ?status=pending/completed/etc.
        """
        status_filter = request.query_params.get("status")
        orders = (
            Order.objects.filter(user=request.user)
            .prefetch_related("items__product")
            .order_by("-created_at")
        )
        if status_filter:
            orders = orders.filter(status=status_filter)

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="detail")
    def order_detail(self, request, pk=None):  # 👈 renombrado aquí
        """
        ✅ Devuelve los detalles completos de un pedido (items + productos)
        Solo accesible por el dueño del pedido.
        """
        try:
            order = Order.objects.prefetch_related("items__product").get(
                pk=pk, user=request.user
            )
        except Order.DoesNotExist:
            return Response(
                {"error": "Pedido no encontrado o no pertenece al usuario."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


# --------------------------------------------------
# OrderItem
# --------------------------------------------------
class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.select_related("order", "product").all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]


# --------------------------------------------------
# Cart
# --------------------------------------------------
class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"])
    def add(self, request):
        """Añadir producto al carrito o incrementar cantidad."""
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))
        cart, _ = Cart.objects.get_or_create(user=request.user)

        item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id)
        if created:
            item.quantity = quantity
        else:
            item.quantity += quantity
        item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def clear(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response({"detail": "Cart cleared."}, status=status.HTTP_200_OK)


# --------------------------------------------------
# Checkout
# --------------------------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def checkout(request):
    user = request.user
    cart = Cart.objects.filter(user=user).first()
    if not cart or cart.items.count() == 0:
        return Response({"error": "El carrito está vacío"}, status=400)

    total = Decimal("0.00")
    for item in cart.items.select_related("product"):
        # ✅ Comprobar stock antes de procesar
        if item.quantity > item.product.stock:
            return Response(
                {"error": f"Stock insuficiente para el producto {item.product.name}"},
                status=400,
            )
        total += item.product.price * item.quantity

    # 🧾 Crear pedido
    order = Order.objects.create(user=user, total_price=total)

    # 🧩 Crear items y descontar stock
    for item in cart.items.select_related("product"):
        product = item.product
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item.quantity,
            price=product.price,
        )
        product.stock -= item.quantity
        product.save()

    # 🧹 Vaciar carrito
    cart.items.all().delete()

    return Response(
        {
            "message": "Pedido creado correctamente",
            "order_id": order.id,
            "total": float(total),
        },
        status=status.HTTP_201_CREATED,
    )
