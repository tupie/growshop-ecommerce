import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_jwt_token_and_cart_access():
    """
    Verifica que un usuario puede obtener un token JWT
    y acceder a un endpoint protegido (/api/cart/).
    """
    User.objects.create_user(username="jwt_test", password="pw123456")
    client = APIClient()

    # 🔐 Obtener token JWT
    response = client.post(
        "/api/token/", {"username": "jwt_test", "password": "pw123456"}, format="json"
    )
    assert (
        response.status_code == 200
    ), f"Error al obtener token: {response.status_code}"
    access = response.data.get("access")
    assert access, "No se obtuvo token de acceso"

    # 🛒 Acceder a un endpoint protegido con JWT
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    response = client.get("/api/cart/")
    assert response.status_code in [
        200,
        404,
    ], f"Respuesta inesperada: {response.status_code}"
