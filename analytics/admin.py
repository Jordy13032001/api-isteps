from django.contrib import admin
from .models import (
    EventoNavegacion,
    PaginaVisitada,
    Busqueda,
    AccionUsuario,
    MetricaAgregada,
    Exportacion,
    Reporte,
    ConfiguracionReporte,
)

admin.site.register(EventoNavegacion)
admin.site.register(PaginaVisitada)
admin.site.register(Busqueda)
admin.site.register(AccionUsuario)
admin.site.register(MetricaAgregada)
admin.site.register(Exportacion)
admin.site.register(Reporte)
admin.site.register(ConfiguracionReporte)
