from django.test import TestCase


class HealthCheckTests(TestCase):
    """Prueba el endpoint de salud /api/health/."""

    def test_health_endpoint(self):
        """Debe responder con 200 y un JSON {'status': 'ok'}."""
        response = self.client.get("/api/health/")
        self.assertEqual(
            response.status_code, 200, "El endpoint /api/health/ no responde con 200."
        )
        self.assertEqual(
            response.json(),
            {"status": "ok"},
            "La respuesta del health check no es la esperada.",
        )
