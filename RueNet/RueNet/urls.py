from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView, TemplateView

urlpatterns = [
    # Accueil provisoire : redirige vers le catalogue
    # path("", RedirectView.as_view(pattern_name="signalement:liste"), name="accueil"),
    path("", TemplateView.as_view(template_name="main.html"), name="accueil"),
    path("admin/", admin.site.urls),
    path("", include("signalement.urls")),
    path("comptes/", include("comptes.urls")),
     
]