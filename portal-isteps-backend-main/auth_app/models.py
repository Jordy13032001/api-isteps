import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="ID único del usuario",
    )
    # Datos personales adicionales
    nombres = models.CharField(
        max_length=100,
        help_text="Nombres del usuario",
    )

    apellidos = models.CharField(
        max_length=100,
        help_text="Apellidos del usuario",
    )

    cedula = models.CharField(
        max_length=10,
        unique=True,
        help_text="Cédula del usuario",
    )

    telefono = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Teléfono del usuario",
    )

    fecha_nacimiento = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha de nacimiento del usuario",
    )

    ESTADO_CHOICES = [
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
        ("bloqueado", "Bloqueado"),
    ]

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="activo",
        help_text="Estado del usuario",
    )

    # Timestamps personalizados
    creado_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de creación del usuario",
    )

    actualizado_en = models.DateTimeField(
        auto_now=True,
        help_text="Fecha y hora de actualización del usuario",
    )

    eliminado_en = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora de eliminación del usuario (soft delete)",
    )


    # CONFIGURACIÓN DE AUTENTICACIÓN

    # Usar email como campo de autenticación principal
    USERNAME_FIELD = "username"  # Django-allauth necesita que sea 'username'

    # Campos requeridos al crear superusuario
    REQUIRED_FIELDS = ["email", "nombres", "apellidos", "cedula"]

    class Meta:
        db_table = "usuarios"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["-creado_en"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
            models.Index(fields=["cedula"]),
        ]

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.username})"

    def get_nombre_completo(self):
        """Retorna el nombre completo del usuario"""
        return f"{self.nombres} {self.apellidos}"

    def esta_activo(self):
        return self.is_active and self.estado == "activo" and self.eliminado_en is None

    def save(self, *args, **kwargs):
        if self.nombres:
            self.first_name = self.nombres.split()[0] if self.nombres else ""
        if self.apellidos:
            self.last_name = self.apellidos.split()[0] if self.apellidos else ""

        super().save(*args, **kwargs)


class Rol(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="ID único del rol",
    )

    nombre = models.CharField(
        max_length=50,
        unique=True,
        help_text="Nombre del rol (Super Admin, profesor, estudiante, etc.)",
    )

    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción detallada del rol",
    )

    nivel = models.IntegerField(
        help_text="Nivel jerárquico del rol (1=más alto, 6=más bajo)",
    )

    activo = models.BooleanField(
        default=True,
        help_text="Indica si el rol está activo o no",
    )

    creado_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de creación del rol",
    )

    actualizado_en = models.DateTimeField(
        auto_now=True,
        help_text="Fecha y hora de actualización del rol",
    )

    class Meta:
        db_table = "roles"
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ["nivel"]
        indexes = [
            models.Index(fields=["nombre"]),
            models.Index(fields=["nivel"]),
        ]

    def __str__(self):
        return f"{self.nombre} (Nivel {self.nivel})"

    def es_administrador(self):
        """Retorna True si es un rol administrativo (nivel <= 2)"""
        return self.nivel <= 2

    def puede_gestionar_usuarios(self):
        """Retorna True si puede gestionar usuarios (nivel <= 3)"""
        return self.nivel <= 3


class Permiso(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único del permiso",
    )

    nombre = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nombre del permiso",
    )

    codigo = models.CharField(
        max_length=50,
        unique=True,
        help_text="Código del permiso (ej: portal.read, usuarios.create)",
    )

    MODULO_CHOICES = [
        ("portal", "Portal"),
        ("usuarios", "Usuarios"),
        ("analytics", "Analytics"),
        ("plataformas", "Plataformas"),
        ("sistema", "Sistema"),
    ]

    modulo = models.CharField(
        max_length=50,
        choices=MODULO_CHOICES,
        help_text="Módulo al que pertenece el permiso",
    )

    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción detallada del permiso",
    )

    activo = models.BooleanField(
        default=True,
        help_text="Indica si el permiso está activo o no",
    )

    creado_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de creación del permiso",
    )

    class Meta:
        db_table = "permisos"
        verbose_name = "Permiso"
        verbose_name_plural = "Permisos"
        ordering = ["modulo", "codigo"]
        indexes = [
            models.Index(fields=["modulo"]),
            models.Index(fields=["codigo"]),
            models.Index(fields=["nombre"]),
        ]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def get_modulo_display_nombre(self):
        """Retorna el nombre legible del módulo"""
        modulos = dict(self.MODULO_CHOICES)
        return modulos.get(self.modulo, self.modulo)

    def es_permiso_critico(self):
        """Retorna True si es un permiso crítico del sistema"""
        permisos_criticos = [
            "usuarios.delete",
            "sistema.config",
            "plataformas.delete",
        ]
        return self.codigo in permisos_criticos


class UsuarioRol(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único de la asignación",
    )

    usuario = models.ForeignKey(
        Usuario,  # Ahora referencia directamente a Usuario
        on_delete=models.CASCADE,
        related_name="usuarios_roles",
        help_text="Usuario al que se le asigna el rol",
    )

    rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE,
        related_name="usuarios_roles",
        help_text="Rol que se asigna al usuario",
    )

    asignado_por = models.ForeignKey(
        Usuario,  # Ahora referencia directamente a Usuario
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asignaciones_realizadas",
        help_text="Usuario administrador que asignó el rol",
    )

    asignado_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de la asignación del rol",
    )

    class Meta:
        db_table = "usuarios_roles"
        verbose_name = "Usuario-Rol"
        verbose_name_plural = "Usuarios-Roles"
        ordering = ["-asignado_en"]
        unique_together = [["usuario", "rol"]]
        indexes = [
            models.Index(fields=["usuario"]),
            models.Index(fields=["rol"]),
            models.Index(fields=["asignado_en"]),
        ]

    def __str__(self):
        return f"{self.usuario.username} → {self.rol.nombre}"

    def get_info_completa(self):
        """Retorna información completa de la asignación"""
        asignador = self.asignado_por.username if self.asignado_por else "Sistema"
        return f"{self.usuario.get_nombre_completo()} tiene rol {self.rol.nombre} (asignado por {asignador})"


class RolPermiso(models.Model):
    """
    Tabla intermedia N:M entre Rol y Permiso.
    Define qué permisos tiene cada rol.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único del rol-permiso",
    )

    rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE,
        related_name="rol_permisos",
        help_text="Rol al que se le asigna el permiso",
    )

    permiso = models.ForeignKey(
        Permiso,
        on_delete=models.CASCADE,
        related_name="rol_permisos",
        help_text="Permiso que se asigna al rol",
    )

    asignado_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de la asignación del permiso",
    )

    class Meta:
        db_table = "rol_permisos"
        verbose_name = "Rol-Permiso"
        verbose_name_plural = "Roles-Permisos"
        ordering = ["rol", "permiso"]
        unique_together = [["rol", "permiso"]]
        indexes = [
            models.Index(fields=["rol"]),
            models.Index(fields=["permiso"]),
        ]

    def __str__(self):
        return f"{self.rol.nombre} → {self.permiso.codigo}"

    def get_info_completa(self):
        """Retorna información completa de la asignación"""
        return f"Rol '{self.rol.nombre}' tiene permiso '{self.permiso.nombre}' ({self.permiso.codigo})"

    def es_permiso_critico(self):
        """Retorna True si el permiso asignado es crítico"""
        return self.permiso.es_permiso_critico()


class Sesion(models.Model):
    """
    Modelo para registrar sesiones de usuario.
    Complementa el sistema de sesiones de Django con información adicional.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único de la sesión",
    )

    usuario = models.ForeignKey(
        Usuario,  # Ahora referencia directamente a Usuario
        on_delete=models.CASCADE,
        related_name="sesiones",
        help_text="Usuario dueño de esta sesión",
    )

    token_sesion = models.CharField(
        max_length=500,
        unique=True,
        help_text="Token JWT de la sesión",
    )

    ip_address = models.GenericIPAddressField(
        help_text="Dirección IP desde donde se conectó",
    )

    user_agent = models.TextField(
        help_text="Información del navegador y sistema operativo",
    )

    DISPOSITIVO_CHOICES = [
        ("desktop", "Escritorio"),
        ("mobile", "Móvil"),
        ("tablet", "Tablet"),
    ]

    dispositivo = models.CharField(
        max_length=50,
        choices=DISPOSITIVO_CHOICES,
        help_text="Tipo de dispositivo usado",
    )

    inicio_sesion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de inicio de sesión",
    )

    ultimo_acceso = models.DateTimeField(
        auto_now=True,
        help_text="Última actividad registrada",
    )

    cierre_sesion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora de cierre (NULL si está activa)",
    )

    duracion_segundos = models.IntegerField(
        null=True,
        blank=True,
        help_text="Duración total de la sesión en segundos",
    )

    class Meta:
        db_table = "sesiones"
        verbose_name = "Sesión"
        verbose_name_plural = "Sesiones"
        ordering = ["-inicio_sesion"]
        indexes = [
            models.Index(fields=["usuario"]),
            models.Index(fields=["inicio_sesion"]),
            models.Index(fields=["ip_address"]),
        ]

    def __str__(self):
        estado = "Activa" if self.esta_activa() else "Cerrada"
        return f"{self.usuario.username} - {self.dispositivo} ({estado})"

    def esta_activa(self):
        """Retorna True si la sesión está activa"""
        return self.cierre_sesion is None

    def cerrar_sesion(self):
        """Cierra la sesión actual calculando la duración"""
        from django.utils import timezone

        if self.esta_activa():
            self.cierre_sesion = timezone.now()
            duracion = self.cierre_sesion - self.inicio_sesion
            self.duracion_segundos = int(duracion.total_seconds())
            self.save()
            return True
        return False

    def get_duracion_legible(self):
        """Retorna la duración en formato legible"""
        if not self.duracion_segundos:
            return "Sesión activa"

        horas = self.duracion_segundos // 3600
        minutos = (self.duracion_segundos % 3600) // 60
        segundos = self.duracion_segundos % 60

        if horas > 0:
            return f"{horas}h {minutos}m {segundos}s"
        elif minutos > 0:
            return f"{minutos}m {segundos}s"
        else:
            return f"{segundos}s"


class PreferenciasUsuario(models.Model):
    """
    Preferencias personalizadas de cada usuario (tema, idioma, etc).
    Relación 1:1 con Usuario.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único de las preferencias",
    )

    usuario = models.OneToOneField(
        Usuario,  # Ahora referencia directamente a Usuario
        on_delete=models.CASCADE,
        related_name="preferencias",
        help_text="Usuario dueño de estas preferencias",
    )

    IDIOMA_CHOICES = [
        ("es", "Español"),
        ("en", "English"),
    ]

    idioma = models.CharField(
        max_length=5,
        choices=IDIOMA_CHOICES,
        default="es",
        help_text="Idioma de la interfaz",
    )

    TEMA_CHOICES = [
        ("claro", "Claro"),
        ("oscuro", "Oscuro"),
        ("auto", "Automático"),
    ]

    tema = models.CharField(
        max_length=20,
        choices=TEMA_CHOICES,
        default="claro",
        help_text="Tema visual de la interfaz",
    )

    zona_horaria = models.CharField(
        max_length=50,
        default="America/Guayaquil",
        help_text="Zona horaria del usuario",
    )

    notificaciones_email = models.BooleanField(
        default=True,
        help_text="Recibir notificaciones por correo electrónico",
    )

    dashboard_layout = models.JSONField(
        default=dict,
        help_text="Configuración del layout del dashboard en formato JSON",
    )

    actualizado_en = models.DateTimeField(
        auto_now=True,
        help_text="Fecha y hora de última actualización",
    )

    class Meta:
        db_table = "preferencias_usuario"
        verbose_name = "Preferencia de Usuario"
        verbose_name_plural = "Preferencias de Usuarios"
        indexes = [
            models.Index(fields=["usuario"]),
        ]

    def __str__(self):
        return f"Preferencias de {self.usuario.username}"

    def get_config_completa(self):
        """Retorna todas las preferencias en un diccionario"""
        return {
            "idioma": self.get_idioma_display(),
            "tema": self.get_tema_display(),
            "zona_horaria": self.zona_horaria,
            "notificaciones_email": self.notificaciones_email,
            "dashboard_layout": self.dashboard_layout,
        }

    def cambiar_tema(self, nuevo_tema):
        """Cambia el tema de la interfaz"""
        if nuevo_tema in dict(self.TEMA_CHOICES):
            self.tema = nuevo_tema
            self.save()
            return True
        return False

    def cambiar_idioma(self, nuevo_idioma):
        """Cambia el idioma de la interfaz"""
        if nuevo_idioma in dict(self.IDIOMA_CHOICES):
            self.idioma = nuevo_idioma
            self.save()
            return True
        return False
