from django.urls import path

from .views import private_view

urlpatterns = [
    path("private/", private_view, name="private"),
]
