from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView , UpdateView
from django.shortcuts import get_object_or_404
from django.urls import reverse

from comptes.models import Utilisateur
from comptes.views import RoleRequisMixin

from .forms import SignalementForm, NouveauSignalementForm
from .models import Categorie, Lieu, Signalement

from .forms import FormulaireGestionSignalement


class CatalogueVue(ListView):
    """
        Vue d'une liste de tous les lieux du catalogue, avec possibilité de les filtrer.
    """
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
    """
        Vue détaillée d'un lieu du catalogue.
    """
    model = Lieu
    template_name = "catalogue/detail.html"
    context_object_name = "lieu"

class CreerSignalementVue(RoleRequisMixin, CreateView):
    """
        Vue du formulaire de création d'un signalement directement via l'id/pk d'un lieu.
        Accès limité aux utilisateurs uniquement.
    """
    role_requis = Utilisateur.Role.UTILISATEUR
    model = Signalement
    form_class = SignalementForm
    template_name = "catalogue/demande.html"

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


class NouveauSignalementVue(RoleRequisMixin, CreateView):
    """
        Vue du formulaire de création d'un nouveau signalement.
        Accès limité aux utilisateurs uniquement.
    """
    role_requis = Utilisateur.Role.UTILISATEUR
    model = Signalement
    form_class = NouveauSignalementForm
    template_name = "signalement/nouveau.html"
    success_url = reverse_lazy("signalement:mes_demandes")

    def form_valid(self, form):
        form.instance.utilisateur = self.request.user
        messages.success(self.request, "Votre signalement a bien été enregistré.")
        return super().form_valid(form)


class MesSignalementsVue(RoleRequisMixin, ListView):
    """
        Vue d'une liste des signalements créés par l'utilisateur connecté.
        Accès limité aux utilisateurs uniquement.
    """
    role_requis = Utilisateur.Role.UTILISATEUR
    model = Signalement
    template_name = "catalogue/mes_demandes.html"
    context_object_name = "signalements"

    def get_queryset(self):
        return Signalement.objects.filter(utilisateur=self.request.user).select_related("lieu")


##  VUES GESTIONNAIRES

class ListeSignalementsVue(RoleRequisMixin, ListView):
    """
        Vue d'une liste des signalements, avec possibilité de les filtrer.
        Accès limité aux gestionnaires uniquement.
    """
    role_requis = Utilisateur.Role.GESTIONNAIRE
    model = Signalement
    template_name = "gestion/liste.html"
    context_object_name = "signalements"

    def get_queryset(self):
        signalements = super().get_queryset().select_related("lieu", "lieu__categorie")
        mot_cle = self.request.GET.get("mot_cle", "").strip()
        etat = self.request.GET.get("etat", "")
        categorie_id = self.request.GET.get("categorie", "")

        if mot_cle:
            # Recherche par mot-clé sur le nom, l'adresse et le quartier
            signalements = signalements.filter(
                Q(lieu__nom__icontains=mot_cle)
                | Q(lieu__adresse__icontains=mot_cle)
                | Q(lieu__quartier__icontains=mot_cle)
            )
        if etat:
            signalements = signalements.filter(
                etat=etat
            )
        if categorie_id:
            signalements = signalements.filter(
                lieu__categorie__id=categorie_id
            )
        return signalements


    def get_context_data(self, **kwargs):
        contexte = super().get_context_data(**kwargs)   # remplit  contexte["signalements"]  avec le retour du get_queryset au dessus.
        contexte["categories"] = Categorie.objects.all()   
        contexte["etats"] = Signalement.ETATS
        contexte["mot_cle"] = self.request.GET.get("mot_cle", "")
        contexte["etat_choisi"] = self.request.GET.get("etat", "")
        contexte["categorie_choisie"] = self.request.GET.get("categorie", "")
        contexte["total_signalements"] = Signalement.objects.count()     
        return contexte


class DetailSignalementVue(RoleRequisMixin, UpdateView):
    """
        Vue détaillée d'un signalement, avec possibilité de modifier son état d'avancement.
        Accès limité aux gestionnaires uniquement.
    """    
    role_requis = Utilisateur.Role.GESTIONNAIRE
    model = Signalement
    form_class = FormulaireGestionSignalement
    template_name = "gestion/detail.html"
    context_object_name = "signalement"
    success_url = reverse_lazy("signalement:gestion_liste")

    def form_valid(self, form):
        form.instance.date_modification = timezone.now()
        messages.success(self.request, f"Le signalement n°{self.object.pk} a bien été mis à jour → {self.object.get_etat_display()}")
        return super().form_valid(form)
