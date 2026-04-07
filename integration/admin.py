from django.contrib import admin
from .models import Plataforma, IntegracionSSO, Sincronizacion

admin.site.register(Plataforma)
admin.site.register(IntegracionSSO)
admin.site.register(Sincronizacion)
