from django.urls import path
from . import views

app_name = "signalement"

urlpatterns = [
    path("catalogue/", views.CatalogueVue.as_view(), name="liste"),
    path("catalogue/<int:pk>/", views.DetailLieuVue.as_view(), name="detail"),
    path("catalogue/<int:pk>/demande/", views.CreerSignalementVue.as_view(), name="demande"),
    path("mes-demandes/", views.MesSignalementsVue.as_view(), name="mes_demandes"),
   

    path("gestion/", views.ListeSignalementsVue.as_view(), name="gestion_liste"),
    path("gestion/<int:pk>/", views.DetailSignalementVue.as_view(), name="gestion_detail"),

]