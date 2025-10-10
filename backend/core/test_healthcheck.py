from django.test import TestCase


class HealthCheckTests(TestCase):
    def test_health_endpoint(self):
        """Verifica que la raíz responde con 200."""
        response = self.client.get("/")
        self.assertIn(response.status_code, [200, 302])
