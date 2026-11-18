from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Categorie, Lieu, Signalement

admin.site.register(User, UserAdmin)
admin.site.register(Categorie)
admin.site.register(Lieu)
admin.site.register(Signalement)