import uuid
from django.db import models
from django.utils import timezone


class LogAuditoria(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único del log",
    )

    usuario = models.ForeignKey(
        "auth_app.Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs_auditoria",
        help_text="Usuario que realizó la acción",
    )

    accion = models.CharField(
        max_length=100,
        help_text="Acción realizada (CREAR_USUARIO, MODIFICAR_CURSO, etc)",
    )

    entidad_tipo = models.CharField(
        max_length=50,
        help_text="Tipo de entidad afectada (usuario, curso, etc)",
    )

    entidad_id = models.CharField(
        max_length=255,
        help_text="ID de la entidad afectada",
    )

    valores_anteriores = models.JSONField(
        default=dict,
        blank=True,
        help_text="Estado de la entidad ANTES del cambio",
    )

    valores_nuevos = models.JSONField(
        default=dict, blank=True, help_text="Estado de la entidad despues del cambio"
    )
    ip_address = models.GenericIPAddressField(
        help_text="Dirección IP desde donde se realizó la acción",
    )

    user_agent = models.TextField(
        blank=True,
        null=True,
        help_text="Información del navegador usado",
    )

    NIVEL_CHOICES = [
        ("INFO", "Información"),
        ("WARNING", "Advertencia"),
        ("ERROR", "Error"),
        ("CRITICAL", "Crítico"),
    ]

    nivel = models.CharField(
        max_length=20,
        choices=NIVEL_CHOICES,
        default="INFO",
        help_text="Nivel de importancia del log",
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora exacta de la acción",
    )

    class Meta:
        db_table = "logs_auditoria"
        verbose_name = "Log de Auditoría"
        verbose_name_plural = "Logs de Auditoría"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["usuario"]),
            models.Index(fields=["accion"]),
            models.Index(fields=["entidad_tipo"]),
            models.Index(fields=["nivel"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "Sistema"
        return f"[{self.nivel}] {usuario_str} - {self.accion} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    def es_critico(self):
        """Retorna True si el log es de nivel crítico"""
        return self.nivel == "CRITICAL"

    def get_info_completa(self):
        """Retorna información completa del log"""
        return {
            "usuario": self.usuario.username if self.usuario else "Sistema",
            "accion": self.accion,
            "entidad": f"{self.entidad_tipo} (ID: {self.entidad_id})",
            "nivel": self.get_nivel_display(),
            "ip": self.ip_address,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "cambios": {
                "antes": self.valores_anteriores,
                "despues": self.valores_nuevos,
            },
        }


class Notificacion(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único de la notificación",
    )

    usuario = models.ForeignKey(
        "auth_app.Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notificaciones",
        help_text="Usuario destinatario de la notificación",
    )

    TIPO_CHOICES = [
        ("sistema", "Sistema"),
        ("academico", "Académico"),
        ("seguridad", "Seguridad"),
        ("alerta", "Alerta"),
    ]

    tipo = models.CharField(
        max_length=50,
        choices=TIPO_CHOICES,
        help_text="Tipo de notificación",
    )

    titulo = models.CharField(
        max_length=255,
        help_text="Título de la notificación",
    )

    mensaje = models.TextField(
        help_text="Contenido de la notificación",
    )

    PRIORIDAD_CHOICES = [
        ("baja", "Baja"),
        ("media", "Media"),
        ("alta", "Alta"),
        ("urgente", "Urgente"),
    ]

    prioridad = models.CharField(
        max_length=20,
        choices=PRIORIDAD_CHOICES,
        default="media",
        help_text="Nivel de prioridad",
    )

    leida = models.BooleanField(
        default=False,
        help_text="Si la notificación fue leída",
    )

    leida_en = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha y hora en que fue leída",
    )

    url_accion = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL si la notificación requiere una acción",
    )

    creado_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación de la notificación",
    )

    class Meta:
        db_table = "notificaciones"
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ["-creado_en"]
        indexes = [
            models.Index(fields=["usuario"]),
            models.Index(fields=["tipo"]),
            models.Index(fields=["prioridad"]),
            models.Index(fields=["leida"]),
            models.Index(fields=["creado_en"]),
        ]

    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "General"
        estado = "Leída" if self.leida else "No leída"
        return f"{usuario_str} - {self.titulo} ({estado})"

    def marcar_como_leida(self):
        """Marca la notificación como leída"""
        from django.utils import timezone

        if not self.leida:
            self.leida = True
            self.leida_en = timezone.now()
            self.save()
            return True
        return False

    def es_urgente(self):
        """Retorna True si la notificación es urgente"""
        return self.prioridad == "urgente"

    def get_info_completa(self):
        """Retorna información completa de la notificación"""
        return {
            "usuario": self.usuario.username if self.usuario else "General",
            "tipo": self.get_tipo_display(),
            "titulo": self.titulo,
            "mensaje": self.mensaje,
            "prioridad": self.get_prioridad_display(),
            "leida": self.leida,
            "leida_en": self.leida_en.strftime("%Y-%m-%d %H:%M:%S")
            if self.leida_en
            else "N/A",
            "creado": self.creado_en.strftime("%Y-%m-%d %H:%M:%S"),
        }


class ConfiguracionSistema(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único de la configuración",
    )

    clave = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nombre de la configuración (ej: nombre_institucion, modo_mantenimiento)",
    )

    valor = models.TextField(
        help_text="Valor de la configuración",
    )

    TIPO_CHOICES = [
        ("string", "Texto"),
        ("number", "Número"),
        ("boolean", "Booleano"),
        ("json", "JSON"),
    ]

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default="string",
        help_text="Tipo de dato del valor",
    )

    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción de qué hace esta configuración",
    )

    CATEGORIA_CHOICES = [
        ("general", "General"),
        ("email", "Email"),
        ("seguridad", "Seguridad"),
        ("integracion", "Integración"),
        ("analytics", "Analytics"),
    ]

    categoria = models.CharField(
        max_length=50,
        choices=CATEGORIA_CHOICES,
        default="general",
        help_text="Categoría de la configuración",
    )

    editable = models.BooleanField(
        default=True,
        help_text="Si la configuración puede cambiarse desde la interfaz",
    )

    actualizado_en = models.DateTimeField(
        auto_now=True,
        help_text="Fecha de última actualización",
    )

    class Meta:
        db_table = "configuracion_sistema"
        verbose_name = "Configuración del Sistema"
        verbose_name_plural = "Configuraciones del Sistema"
        ordering = ["categoria", "clave"]
        indexes = [
            models.Index(fields=["clave"]),
            models.Index(fields=["categoria"]),
            models.Index(fields=["editable"]),
        ]

    def __str__(self):
        return f"{self.clave} = {self.valor[:50]}"

    def get_info_completa(self):
        """Retorna información completa de la configuración"""
        return {
            "clave": self.clave,
            "valor": self.valor,
            "tipo": self.get_tipo_display(),
            "categoria": self.get_categoria_display(),
            "descripcion": self.descripcion or "Sin descripción",
            "editable": self.editable,
            "actualizado": self.actualizado_en.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def get_valor_convertido(self):
        """Retorna el valor convertido según su tipo"""
        if self.tipo == "number":
            try:
                return float(self.valor)
            except (ValueError, TypeError):
                return 0
        elif self.tipo == "boolean":
            return self.valor.lower() in ["true", "1", "yes", "si"]
        elif self.tipo == "json":
            import json

            try:
                return json.loads(self.valor)
            except json.JSONDecodeError:
                return {}
        else:
            return self.valor


class TareaProgramada(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único de la tarea",
    )

    nombre = models.CharField(
        max_length=100,
        help_text="Nombre descriptivo de la tarea",
    )

    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción de qué hace la tarea",
    )

    TIPO_CHOICES = [
        ("maintenance", "Mantenimiento"),
        ("backup", "Backup"),
        ("analytics", "Analytics"),
        ("sync", "Sincronización"),
        ("cleanup", "Limpieza"),
    ]

    tipo = models.CharField(
        max_length=50,
        choices=TIPO_CHOICES,
        help_text="Tipo de tarea",
    )

    comando = models.TextField(
        help_text="Comando o script a ejecutar",
    )

    frecuencia = models.CharField(
        max_length=50,
        help_text="Expresión cron (ej: */5 * * * * = cada 5 minutos)",
    )

    activa = models.BooleanField(
        default=True,
        help_text="Si la tarea está activa",
    )

    ultima_ejecucion = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha y hora de última ejecución",
    )

    proxima_ejecucion = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha y hora de próxima ejecución",
    )

    ESTADO_CHOICES = [
        ("exitoso", "Exitoso"),
        ("fallido", "Fallido"),
        ("ejecutando", "Ejecutando"),
    ]

    estado_ultima = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        blank=True,
        null=True,
        help_text="Estado de la última ejecución",
    )

    creado_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación de la tarea",
    )

    class Meta:
        db_table = "tareas_programadas"
        verbose_name = "Tarea Programada"
        verbose_name_plural = "Tareas Programadas"
        ordering = ["nombre"]
        indexes = [
            models.Index(fields=["tipo"]),
            models.Index(fields=["activa"]),
            models.Index(fields=["proxima_ejecucion"]),
            models.Index(fields=["estado_ultima"]),
        ]

    def __str__(self):
        estado = "Activa" if self.activa else "Inactiva"
        return f"{self.nombre} ({estado}) - {self.frecuencia}"

    def esta_activa(self):
        """Retorna True si la tarea está activa"""
        return self.activa

    def fue_exitosa(self):
        """Retorna True si la última ejecución fue exitosa"""
        return self.estado_ultima == "exitoso"

    def get_info_completa(self):
        """Retorna información completa de la tarea"""
        return {
            "nombre": self.nombre,
            "tipo": self.get_tipo_display(),
            "descripcion": self.descripcion or "Sin descripción",
            "frecuencia": self.frecuencia,
            "activa": self.activa,
            "ultima_ejecucion": self.ultima_ejecucion.strftime("%Y-%m-%d %H:%M:%S")
            if self.ultima_ejecucion
            else "Nunca",
            "proxima_ejecucion": self.proxima_ejecucion.strftime("%Y-%m-%d %H:%M:%S")
            if self.proxima_ejecucion
            else "No programada",
            "estado": self.get_estado_ultima_display()
            if self.estado_ultima
            else "Sin ejecutar",
        }


class MensajeDashboard(models.Model):
    """
    Mensajes personalizados para el dashboard según rol del usuario.

    Un mensaje puede dirigirse a múltiples roles simultáneamente.
    Ejemplo: Un mensaje de bienvenida puede ir a Estudiantes y Profesores.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único del mensaje",
    )

    titulo = models.CharField(max_length=255, help_text="Título corto del mensaje")

    mensaje = models.TextField(help_text="Contenido completo del mensaje")

    imagen_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        help_text="URL de la imagen opcional para el mensaje",
    )

    color_fondo = models.CharField(
        max_length=20,
        default="#e3f2fd",
        null=True,
        blank=True,
        help_text="Color de fondo en formato hexadecimal (ej: #e3f2fd)",
    )

    enlace_url = models.URLField(
        max_length=500, null=True, blank=True, help_text="URL del enlace opcional"
    )

    enlace_texto = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Texto del botón/enlace (ej: 'Ver más', 'Ir al calendario')",
    )

    activo = models.BooleanField(
        default=True, help_text="Si el mensaje está activo y visible"
    )

    prioridad = models.IntegerField(
        default=100, help_text="Orden de visualización (1 = más prioritario)"
    )

    fecha_inicio = models.DateField(
        null=True,
        blank=True,
        help_text="Desde cuándo se muestra el mensaje (NULL = desde siempre)",
    )

    fecha_fin = models.DateField(
        null=True,
        blank=True,
        help_text="Hasta cuándo se muestra el mensaje (NULL = sin límite)",
    )

    creado_por = models.ForeignKey(
        "auth_app.Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mensajes_creados",
        help_text="Usuario que creó el mensaje",
    )

    creado_en = models.DateTimeField(
        auto_now_add=True, help_text="Fecha y hora de creación"
    )

    actualizado_en = models.DateTimeField(
        auto_now=True, help_text="Fecha y hora de última actualización"
    )

    class Meta:
        db_table = "mensajes_dashboard"
        verbose_name = "Mensaje de Dashboard"
        verbose_name_plural = "Mensajes de Dashboard"
        ordering = ["prioridad", "-creado_en"]
        indexes = [
            models.Index(fields=["activo"]),
            models.Index(fields=["fecha_inicio"]),
            models.Index(fields=["fecha_fin"]),
            models.Index(fields=["prioridad"]),
            models.Index(fields=["creado_por"]),
        ]

    def __str__(self):
        return f"{self.titulo} (Prioridad: {self.prioridad})"

    def esta_vigente(self):
        """Verifica si el mensaje está dentro de su periodo de vigencia"""
        hoy = timezone.now().date()

        # Verificar fecha de inicio
        if self.fecha_inicio and self.fecha_inicio > hoy:
            return False

        # Verificar fecha de fin
        if self.fecha_fin and self.fecha_fin < hoy:
            return False

        return True

    def get_roles_asignados(self):
        """Retorna lista de nombres de roles asignados a este mensaje"""
        return [rel.rol.nombre for rel in self.roles.all()]


class MensajeDashboardRol(models.Model):
    """
    Tabla intermedia N:M entre MensajeDashboard y Rol.

    Define a qué roles va dirigido cada mensaje.
    Un mensaje puede tener múltiples roles y un rol puede recibir múltiples mensajes.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único de la relación",
    )

    mensaje = models.ForeignKey(
        MensajeDashboard,
        on_delete=models.CASCADE,
        related_name="roles",
        help_text="Mensaje asignado",
    )

    rol = models.ForeignKey(
        "auth_app.Rol",
        on_delete=models.CASCADE,
        related_name="mensajes_dashboard",
        help_text="Rol destinatario del mensaje",
    )

    asignado_en = models.DateTimeField(
        auto_now_add=True, help_text="Fecha y hora de asignación"
    )

    class Meta:
        db_table = "mensajes_dashboard_roles"
        verbose_name = "Asignación Mensaje-Rol"
        verbose_name_plural = "Asignaciones Mensaje-Rol"
        unique_together = [
            ["mensaje", "rol"]
        ]  # Un mensaje no puede asignarse dos veces al mismo rol
        indexes = [
            models.Index(fields=["mensaje"]),
            models.Index(fields=["rol"]),
        ]

    def __str__(self):
        return f"{self.mensaje.titulo} → {self.rol.nombre}"


# MODELO PARA ARCHIVOS DEL SISTEMA


class ArchivoSistema(models.Model):
    """
    Gestión de archivos del sistema (formularios, etc.)
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único del archivo",
    )

    nombre = models.CharField(
        max_length=255, help_text="Nombre descriptivo del archivo"
    )

    archivo = models.FileField(
        upload_to="sistema/archivos/%Y/%m/", help_text="Archivo subido al sistema"
    )

    ESTADO_CHOICES = [
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
    ]

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="activo",
        help_text="Estado del archivo",
    )

    creado_en = models.DateTimeField(auto_now_add=True, help_text="Fecha de creación")

    actualizado_en = models.DateTimeField(
        auto_now=True, help_text="Fecha de actualización"
    )

    class Meta:
        db_table = "archivos_sistema"
        verbose_name = "Archivo del Sistema"
        verbose_name_plural = "Archivos del Sistema"
        ordering = ["-creado_en"]
        indexes = [
            models.Index(fields=["estado"]),
            models.Index(fields=["creado_en"]),
        ]

    def __str__(self):
        return self.nombre

    def get_url_archivo(self):
        """Retorna la URL del archivo"""
        if self.archivo:
            return self.archivo.url
        return None

    def get_tamano_legible(self):
        """Retorna el tamaño del archivo en formato legible"""
        if self.archivo:
            size = self.archivo.size
            for unit in ["B", "KB", "MB", "GB"]:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        return "0 B"
