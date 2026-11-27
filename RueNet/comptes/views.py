from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import FormulaireInscription
from .models import Utilisateur


class RoleRequisMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
        Contrôle l'accès aux vues/pages en fonction de si un compte est connecté et du role de ce dernier.
    """
    raise_exception = True
    role_requis = None

    def get_permission_denied_message(self):
        if self.role_requis:
            nom_role = getattr(self.role_requis, "label", str(self.role_requis)).lower()
            return f"Vous devez être connecté avec un compte {nom_role} pour accéder à cette page."
        return super().get_permission_denied_message()

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.role == self.role_requis

    def handle_no_permission(self):
        if self.request.user.is_authenticated and self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return super().handle_no_permission()



class VueInscription(CreateView):
    """
        Vue du formulaire d'inscription d'un nouvel utilisateur.
    """
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
    """
        Redirige à la connexion.
    """
    template_name = "comptes/connexion.html"
    redirect_authenticated_user = True
    next_page = reverse_lazy("signalement:liste")


class VueDeconnexion(LogoutView):
    """
        Redirige à la deconnexion.
    """
    next_page = reverse_lazy("comptes:connexion")