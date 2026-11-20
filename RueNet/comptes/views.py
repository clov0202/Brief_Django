from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import FormulaireInscription
from .models import Utilisateur

# Create your views here.

class VueInscription(CreateView):
    model = Utilisateur
    form_class = FormulaireInscription
    template_name = "comptes/inscription.html"
    success_url = reverse_lazy("signalement:liste")

    def form_valid(self, form):
        reponse = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f"Bienvenue {self.object.username}, votre compte est créé.")
        return reponse


class VueConnexion(LoginView):
    template_name = "comptes/connexion.html"
    redirect_authenticated_user = True
    next_page = reverse_lazy("signalement:liste")


class VueDeconnexion(LogoutView):
    next_page = reverse_lazy("comptes:connexion")