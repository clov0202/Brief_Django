from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q
from django.views.generic import ListView, DetailView, UpdateView

from .models import Categorie, Lieu, Signalement
from .forms import FormulaireGestionSignalement


class CatalogueVue(ListView):
    model = Lieu
    template_name = "catalogue/liste.html"
    context_object_name = "lieux"

    def get_queryset(self):
        lieux = Lieu.objects.select_related("categorie")
        mot_cle = self.request.GET.get("mot_cle", "").strip()
        categorie = self.request.GET.get("categorie", "")

        if mot_cle:
            # Recherche par mot-clé sur le nom, l'adresse et le quartier
            lieux = lieux.filter(
                Q(nom__icontains=mot_cle)
                | Q(adresse__icontains=mot_cle)
                | Q(quartier__icontains=mot_cle)
            )
        if categorie.isdigit():  # on ignore une valeur forgée non numérique
            lieux = lieux.filter(categorie_id=int(categorie))
        return lieux

    def get_context_data(self, **kwargs):
        contexte = super().get_context_data(**kwargs)
        contexte["categories"] = Categorie.objects.all()
        contexte["mot_cle"] = self.request.GET.get("mot_cle", "")
        contexte["categorie_choisie"] = self.request.GET.get("categorie", "")
        return contexte


class DetailLieuVue(DetailView):
    model = Lieu
    template_name = "catalogue/detail.html"
    context_object_name = "lieu"



##--------------------------------------------------



class ListeSignalementsVue(ListView):
    model = Signalement
    template_name = "gestion/liste.html"
    context_object_name = "signalements"

    def get_queryset(self):
        pass

    def get_context_data(self, **kwargs):
        pass


class DetailSignalementVue(UpdateView):
    model = Signalement
    form_class = FormulaireGestionSignalement
    template_name = "gestion/detail.html"
    context_object_name = "signalement"
    success_url = reverse_lazy("signalement:gestion:liste")

    def form_valid(self, form):
        # Met à jour la date de modification manuellement (puisque auto_now n'est pas utilisé)
        form.instance.date_modification = timezone.now()
        return super().form_valid(form)