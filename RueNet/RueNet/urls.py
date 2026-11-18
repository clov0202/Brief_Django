from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Accueil provisoire : redirige vers le catalogue
    path("", RedirectView.as_view(pattern_name="catalogue:liste"), name="accueil"),
    path("admin/", admin.site.urls),
    path("catalogue/", include("catalogue.urls")),
]