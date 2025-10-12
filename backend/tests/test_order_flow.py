from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from shop.models import Cart, Category, Order, OrderItem, Product


@pytest.fixture
def api_client(db):
    """Devuelve un cliente autenticado listo para hacer peticiones."""

    def _create_authenticated_client(username="user_test", password="pw123456"):
        user = User.objects.create_user(username=username, password=password)
        client = APIClient()
        token_response = client.post(
            "/api/token/", {"username": username, "password": password}
        )
        token = token_response.data["access"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return client, user

    return _create_authenticated_client


@pytest.fixture
def category(db):
    return Category.objects.create(name="Genérica", slug="generica")


# --------------------------------------------------
# TEST 1 — Checkout con un producto
# --------------------------------------------------
@pytest.mark.django_db
def test_checkout_creates_order_with_single_product(api_client, category):
    client, user = api_client()
    product = Product.objects.create(
        name="Producto Uno",
        slug="producto-uno",
        price=Decimal("9.99"),
        stock=5,
        category=category,
    )

    client.post("/api/cart/add/", {"product_id": product.id, "quantity": 3})
    response = client.post("/api/checkout/")
    assert response.status_code == 201

    order = Order.objects.filter(user=user).first()
    assert order and float(order.total_price) == pytest.approx(29.97, 0.01)
    assert OrderItem.objects.filter(order=order).count() == 1


# --------------------------------------------------
# TEST 2 — Checkout con múltiples productos
# --------------------------------------------------
@pytest.mark.django_db
def test_checkout_creates_order_with_multiple_products(api_client, category):
    client, user = api_client("multiuser")

    products = [
        Product.objects.create(
            name="Producto A",
            slug="producto-a",
            price=Decimal("5.00"),
            stock=10,
            category=category,
        ),
        Product.objects.create(
            name="Producto B",
            slug="producto-b",
            price=Decimal("12.50"),
            stock=8,
            category=category,
        ),
        Product.objects.create(
            name="Producto C",
            slug="producto-c",
            price=Decimal("7.25"),
            stock=6,
            category=category,
        ),
    ]

    client.post("/api/cart/add/", {"product_id": products[0].id, "quantity": 2})
    client.post("/api/cart/add/", {"product_id": products[1].id, "quantity": 1})
    client.post("/api/cart/add/", {"product_id": products[2].id, "quantity": 3})

    expected_total = 10.00 + 12.50 + 21.75
    response = client.post("/api/checkout/")
    assert response.status_code == 201

    order = Order.objects.filter(user=user).first()
    assert order and float(order.total_price) == pytest.approx(expected_total, 0.01)
    assert order.items.count() == 3


# --------------------------------------------------
# TEST 3 — Checkout con carrito vacío
# --------------------------------------------------
@pytest.mark.django_db
def test_checkout_fails_if_cart_empty(api_client):
    client, user = api_client("emptycart")
    response = client.post("/api/checkout/")
    assert response.status_code == 400
    assert "vacío" in response.data["error"]
    assert not Order.objects.filter(user=user).exists()


# --------------------------------------------------
# TEST 4 — Checkout reduce stock correctamente
# --------------------------------------------------
@pytest.mark.django_db
def test_checkout_reduces_product_stock(api_client, category):
    client, user = api_client("stockuser")
    product = Product.objects.create(
        name="Producto Stock",
        slug="producto-stock",
        price=Decimal("15.00"),
        stock=10,
        category=category,
    )
    client.post("/api/cart/add/", {"product_id": product.id, "quantity": 3})
    response = client.post("/api/checkout/")
    assert response.status_code == 201

    product.refresh_from_db()
    assert product.stock == 7


# --------------------------------------------------
# TEST 5 — /api/cart/add crea y actualiza cantidades
# --------------------------------------------------
@pytest.mark.django_db
def test_cart_add_creates_and_updates_quantities(api_client, category):
    client, user = api_client("cartadder")
    product = Product.objects.create(
        name="Producto Añadido",
        slug="producto-anadido",
        price=Decimal("3.50"),
        stock=10,
        category=category,
    )

    resp1 = client.post("/api/cart/add/", {"product_id": product.id, "quantity": 3})
    assert resp1.status_code == 200
    cart = Cart.objects.get(user=user)
    item = cart.items.get(product=product)
    assert item.quantity == 3

    resp2 = client.post("/api/cart/add/", {"product_id": product.id, "quantity": 2})
    assert resp2.status_code == 200
    item.refresh_from_db()
    assert item.quantity == 5


# --------------------------------------------------
# TEST 6 — Checkout falla si stock insuficiente
# --------------------------------------------------
@pytest.mark.django_db
def test_checkout_fails_if_insufficient_stock(api_client, category):
    client, user = api_client("nostock")
    product = Product.objects.create(
        name="Producto Sin Stock",
        slug="producto-sin-stock",
        price=Decimal("20.00"),
        stock=2,
        category=category,
    )
    client.post("/api/cart/add/", {"product_id": product.id, "quantity": 5})
    response = client.post("/api/checkout/")
    assert response.status_code == 400
    assert "Stock insuficiente" in response.data["error"]
    assert not Order.objects.filter(user=user).exists()

    product.refresh_from_db()
    assert product.stock == 2


# --------------------------------------------------
# TEST 7 — Historial de pedidos del usuario
# --------------------------------------------------
@pytest.mark.django_db
def test_orders_history_returns_user_orders(api_client, category):
    """
    ✅ Verifica que /api/orders/history/ devuelve solo los pedidos del usuario autenticado.
    """
    client, user = api_client("historyuser")

    # Crear productos y pedidos manualmente
    product1 = Product.objects.create(
        name="Producto Histórico 1",
        slug="hist-1",
        price=Decimal("5.00"),
        stock=10,
        category=category,
    )
    product2 = Product.objects.create(
        name="Producto Histórico 2",
        slug="hist-2",
        price=Decimal("7.50"),
        stock=10,
        category=category,
    )

    # Crear pedidos previos
    order1 = Order.objects.create(user=user, total_price=Decimal("10.00"))
    order2 = Order.objects.create(user=user, total_price=Decimal("15.00"))
    OrderItem.objects.create(
        order=order1, product=product1, quantity=2, price=product1.price
    )
    OrderItem.objects.create(
        order=order2, product=product2, quantity=2, price=product2.price
    )

    response = client.get("/api/orders/history/")
    assert response.status_code == 200
    assert isinstance(response.data, list)
    assert len(response.data) == 2
    assert response.data[0]["id"] == order2.id  # el más reciente primero
    assert response.data[1]["id"] == order1.id

    print("\n✅ Historial de pedidos devuelto correctamente y en orden descendente.")


@pytest.mark.django_db
def test_order_detail_endpoint(api_client, category):
    """
    ✅ Verifica que el endpoint /api/orders/<id>/detail/ devuelve correctamente
    los detalles del pedido con los productos incluidos.
    """
    client, user = api_client("detailuser")

    # Crear producto y pedido
    product = Product.objects.create(
        name="Producto Detalle",
        slug="producto-detalle",
        price=Decimal("25.00"),
        stock=10,
        category=category,
    )
    order = Order.objects.create(user=user, total_price=Decimal("50.00"))
    OrderItem.objects.create(
        order=order, product=product, quantity=2, price=product.price
    )

    # Llamar al endpoint
    response = client.get(f"/api/orders/{order.id}/detail/")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == order.id
    assert float(data["total_price"]) == 50.00
    assert len(data["items"]) == 1
    assert data["items"][0]["product"]["name"] == "Producto Detalle"
    assert data["items"][0]["quantity"] == 2
