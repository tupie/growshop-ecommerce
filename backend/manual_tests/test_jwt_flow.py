"""
Script seguro para probar autenticación JWT con Django REST Framework.
Usa variables de entorno para las credenciales.
"""

import os
import sys

import requests
from dotenv import load_dotenv

# Cargar variables desde .env.local si existe
load_dotenv(".env.local")

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
USERNAME = os.getenv("TEST_USERNAME", "admin")
PASSWORD = os.getenv("TEST_PASSWORD")

if not PASSWORD:
    print("❌ ERROR: falta TEST_PASSWORD en el entorno o en .env.local")
    sys.exit(1)


def obtener_token():
    print("🔑 Solicitando token JWT...")
    response = requests.post(
        f"{BASE_URL}/api/token/",
        json={"username": USERNAME, "password": PASSWORD},
        timeout=10,  # ✅ timeout agregado
    )
    if response.status_code == 200:
        data = response.json()
        print("✅ Token obtenido correctamente.\n")
        return data["access"]
    else:
        print("❌ Error al obtener token:")
        print(response.status_code, response.text)
        sys.exit(1)


def probar_endpoint_privado(token):
    print("🔐 Probando acceso al endpoint protegido...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/private/",
        headers=headers,
        timeout=10,  # ✅ timeout agregado
    )
    if response.status_code == 200:
        print("✅ Acceso permitido:")
        print(response.json())
    else:
        print("❌ Acceso denegado:")
        print(response.status_code, response.text)


if __name__ == "__main__":
    token = obtener_token()
    probar_endpoint_privado(token)
