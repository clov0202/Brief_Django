from django.db.models import Q
from django.views.generic import ListView, DetailView

from .models import Categorie, Lieu


class CatalogueView(ListView):
    model = Lieu
    template_name = "catalogue/liste.html"
    context_object_name = "lieux"

    def get_queryset(self):
        qs = Lieu.objects.select_related("categorie")
        q = self.request.GET.get("q", "").strip()
        categorie = self.request.GET.get("categorie", "")

        if q:
            # Recherche par mot-clé sur le nom, l'adresse et le quartier
            qs = qs.filter(
                Q(nom__icontains=q) | Q(adresse__icontains=q) | Q(quartier__icontains=q)
            )
        if categorie.isdigit():  # on ignore une valeur forgée non numérique
            qs = qs.filter(categorie_id=int(categorie))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Categorie.objects.all()
        ctx["q"] = self.request.GET.get("q", "")
        ctx["categorie_choisie"] = self.request.GET.get("categorie", "")
        return ctx


class LieuDetailView(DetailView):
    model = Lieu
    template_name = "catalogue/detail.html"
    context_object_name = "lieu"