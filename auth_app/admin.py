from django.contrib import admin
from .models import (
    Usuario,
    Rol,
    Permiso,
    UsuarioRol,
    RolPermiso,
    Sesion,
    PreferenciasUsuario,
)

admin.site.register(Usuario)
admin.site.register(Rol)
admin.site.register(Permiso)
admin.site.register(UsuarioRol)
admin.site.register(RolPermiso)
admin.site.register(Sesion)
admin.site.register(PreferenciasUsuario)

