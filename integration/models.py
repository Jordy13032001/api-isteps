from django.db import models
import uuid


class Plataforma(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="ID único de la plataforma",
    )

    nombre = models.CharField(
        max_length=120, help_text="Nombre de la plataforma (Eva, SGA, etc.)"
    )

    codigo = models.CharField(
        max_length=50, unique=True, help_text="Código unico de la plataforma"
    )

    TIPO_CHOICES = (("eva", "Eva"), ("sga", "Sga"), ("cursos", "Cursos"))

    tipo = models.CharField(
        max_length=50,
        choices=TIPO_CHOICES,
        help_text="Tipo de plataforma (Eva, Sga, Cursos)",
    )

    url_base = models.URLField(
        max_length=200,
        help_text="URL base de la plataforma",
    )

    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción de la plataforma",
    )

    icono_url = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        help_text="URL del icono de la plataforma",
    )

    ESTADO_CHOICES = [
        ("activo", "Activo"),
        ("mantenimiento", "En Mantenimiento"),
        ("inactivo", "Inactivo"),
    ]

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="activo",
        help_text="Estado actual de la plataforma",
    )

    creado_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación del registro",
    )

    actualizado_en = models.DateTimeField(
        auto_now=True,
        help_text="Fecha de última actualización",
    )

    class Meta:
        db_table = "plataformas"
        verbose_name = "Plataforma"
        verbose_name_plural = "Plataformas"
        ordering = ["nombre"]
        indexes = [
            models.Index(fields=["codigo"]),
            models.Index(fields=["tipo"]),
            models.Index(fields=["estado"]),
        ]

    def __str__(self):
        return f"{self.nombre} {self.codigo}"

    def get_url_completa(self, ruta=" "):
        if ruta:
            return f"{self.url_base.rstrip('/')}/{ruta.lstrip('/')}"
        return self.url_base

    def esta_activa(self):
        return self.estado == "activo"


class IntegracionSSO(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador unico de la integracion SSO",
    )

    plataforma = models.OneToOneField(
        "Plataforma",
        on_delete=models.CASCADE,
        help_text="Plataforma a la que pertenece esta configuracion SSO",
    )

    PROTOCOLO_CHOICES = [
        ("SAML2", "SAML 2.0"),
        ("OAUth2", "OAuth 2.0"),
        ("OpenID", "OpenID Connect"),
    ]

    protocolo = models.CharField(
        max_length=20,
        choices=PROTOCOLO_CHOICES,
        help_text="Protocolo de autenticacion utilizado",
    )

    client_id = models.CharField(
        max_length=255,
        help_text="ID del cliente en Keycloak",
    )

    client_secret = models.CharField(
        max_length=500,
        help_text="Secreto del cliente (debe estar encriptado en producción)",
    )

    metadata_url = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        help_text="URL de metadatos SAML/OAuth",
    )

    callback_url = models.URLField(
        max_length=255,
        help_text="URL de callback después del login",
    )

    logout_url = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        help_text="URL de logout de la plataforma",
    )

    certificado = models.TextField(
        blank=True,
        null=True,
        help_text="Certificado SSL público para validación",
    )

    activo = models.BooleanField(
        default=True,
        help_text="Si la integración SSO está activa",
    )

    creado_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación del registro",
    )

    actualizado_en = models.DateTimeField(
        auto_now=True,
        help_text="Fecha de última actualización",
    )

    class Meta:
        db_table = "integraciones_sso"
        verbose_name = "Integración SSO"
        verbose_name_plural = "Integraciones SSO"
        indexes = [
            models.Index(fields=["plataforma"]),
            models.Index(fields=["protocolo"]),
        ]

    def __str__(self):
        return f"SSO {self.protocolo} para {self.plataforma.nombre}"

    def esta_configurada(self):
        return bool(self.client_id and self.callback_url and self.activo)

    def get_metadata_completa(self):
        return {
            "protocolo": self.get_protocolo_display(),
            "client_id": self.client_id,
            "callback_url": self.callback_url,
            "metadata_url": self.metadata_url,
            "logout_url": self.logout_url,
            "activo": self.activo,
        }


class Sincronizacion(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único de la sincronización",
    )

    plataforma = models.ForeignKey(
        "Plataforma",
        on_delete=models.CASCADE,
        related_name="sincronizaciones",
        help_text="Plataforma con la que se sincronizó",
    )

    TIPO_CHOICES = [
        ("usuarios", "Usuarios"),
        ("cursos", "Cursos"),
        ("notas", "Notas"),
        ("asistencia", "Asistencia"),
    ]

    tipo = models.CharField(
        max_length=50,
        choices=TIPO_CHOICES,
        help_text="Tipo de datos sincronizados",
    )

    DIRECCION_CHOICES = [
        ("pull", "Pull (traer datos)"),
        ("push", "Push (enviar datos)"),
        ("bidireccional", "Bidireccional"),
    ]

    direccion = models.CharField(
        max_length=20,
        choices=DIRECCION_CHOICES,
        help_text="Dirección de la sincronización",
    )

    ESTADO_CHOICES = [
        ("exitoso", "Exitoso"),
        ("fallido", "Fallido"),
        ("parcial", "Parcial"),
    ]

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        help_text="Estado de la sincronización",
    )

    registros_procesados = models.IntegerField(
        default=0,
        help_text="Cantidad total de registros procesados",
    )

    registros_exitosos = models.IntegerField(
        default=0,
        help_text="Cantidad de registros sincronizados exitosamente",
    )

    registros_fallidos = models.IntegerField(
        default=0,
        help_text="Cantidad de registros con error",
    )

    mensaje_error = models.TextField(
        blank=True,
        null=True,
        help_text="Detalles del error si la sincronización falló",
    )

    duracion_segundos = models.IntegerField(
        blank=True,
        null=True,
        help_text="Tiempo que tomó la sincronización en segundos",
    )

    creado_por = models.ForeignKey(
        "auth_app.Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sincronizaciones_creadas",
        help_text="Usuario que ejecutó la sincronización",
    )

    creado_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de la sincronización",
    )

    class Meta:
        db_table = "sincronizaciones"
        verbose_name = "Sincronización"
        verbose_name_plural = "Sincronizaciones"
        ordering = ["-creado_en"]
        indexes = [
            models.Index(fields=["plataforma"]),
            models.Index(fields=["tipo"]),
            models.Index(fields=["estado"]),
            models.Index(fields=["creado_en"]),
        ]

    def __str__(self):
        return f"Sync {self.tipo} - {self.plataforma.codigo} ({self.estado})"

    def fue_exitosa(self):
        return self.estado == "exitoso"

    def get_tasa_exito(self):
        if self.registros_procesados == 0:
            return 0
        return round((self.registros_exitosos / self.registros_procesados) * 100, 2)

    def get_resumen(self):
        return {
            "plataforma": self.plataforma.nombre,
            "tipo": self.get_tipo_display(),
            "direccion": self.get_direccion_display(),
            "estado": self.get_estado_display(),
            "procesados": self.registros_procesados,
            "exitosos": self.registros_exitosos,
            "fallidos": self.registros_fallidos,
            "tasa_exito": f"{self.get_tasa_exito()}%",
            "duracion": f"{self.duracion_segundos}s"
            if self.duracion_segundos
            else "N/A",
        }
