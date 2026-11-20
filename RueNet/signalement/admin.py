from django.contrib import admin

from .models import Categorie, Lieu, Signalement

admin.site.register(Categorie)
admin.site.register(Lieu)
admin.site.register(Signalement)