import os

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://127.0.0.1:8000/api"
USERNAME = os.getenv("TEST_USERNAME", "tupie-test")
PASSWORD = os.getenv("TEST_PASSWORD", "pw9242")


def get_token():
    print("🔐 Obteniendo token JWT...")
    res = requests.post(
        f"{BASE_URL}/token/",
        json={"username": USERNAME, "password": PASSWORD},
        timeout=10,  # ✅ timeout agregado
    )
    res.raise_for_status()
    data = res.json()
    print("✅ Token obtenido correctamente.")
    return data["access"]


def add_to_cart(token, product_id=1, quantity=1):
    print(f"🛒 Agregando producto {product_id} (x{quantity}) al carrito...")
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.post(
        f"{BASE_URL}/cart/add/",
        json={"product_id": product_id, "quantity": quantity},
        headers=headers,
        timeout=10,  # ✅ timeout agregado
    )
    res.raise_for_status()
    print("✅ Producto agregado correctamente.")


def get_cart(token):
    print("📦 Consultando carrito...")
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{BASE_URL}/cart/", headers=headers, timeout=10)  # ✅
    res.raise_for_status()
    data = res.json()
    print("🧾 Contenido del carrito:")
    print(data)
    return data


def checkout(token):
    print("💳 Realizando checkout...")
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.post(f"{BASE_URL}/checkout/", headers=headers, timeout=10)  # ✅
    res.raise_for_status()
    data = res.json()
    print("✅ Pedido creado correctamente:")
    print(data)
    return data


def main():
    token = get_token()
    add_to_cart(token, product_id=1, quantity=2)
    get_cart(token)
    checkout(token)


if __name__ == "__main__":
    main()
