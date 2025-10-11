from django.http import JsonResponse


def health(request):
    """Devuelve 200 OK para indicar que la API está viva."""
    return JsonResponse({"status": "ok"})
