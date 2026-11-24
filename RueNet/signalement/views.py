from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse

from .forms import SignalementForm
from .models import Categorie, Lieu, Signalement


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

class CreerSignalementVue(LoginRequiredMixin, CreateView):
    model = Signalement
    form_class = SignalementForm
    template_name = "signalement/demande.html"

    def dispatch(self, request, *args, **kwargs):
        self.lieu = get_object_or_404(Lieu, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        contexte = super().get_context_data(**kwargs)
        contexte["lieu"] = self.lieu
        return contexte

    def form_valid(self, form):
        form.instance.utilisateur = self.request.user
        form.instance.lieu = self.lieu
        messages.success(self.request, "Votre signalement a bien été enregistré.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("signalement:detail", kwargs={"pk": self.lieu.pk})


class MesSignalementsVue(LoginRequiredMixin, ListView):
    model = Signalement
    template_name = "signalement/mes_demandes.html"
    context_object_name = "signalements"

    def get_queryset(self):
        return Signalement.objects.filter(utilisateur=self.request.user).select_related("lieu")