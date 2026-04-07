from django.contrib import admin
from .models import LogAuditoria, Notificacion, ConfiguracionSistema, TareaProgramada


admin.site.register(LogAuditoria)
admin.site.register(Notificacion)
admin.site.register(ConfiguracionSistema)
admin.site.register(TareaProgramada)
