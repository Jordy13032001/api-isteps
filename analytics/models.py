import uuid
from django.db import models


class EventoNavegacion(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único del evento",
    )

    usuario = models.ForeignKey(
        "auth_app.Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eventos_navegacion",
        help_text="Usuario que generó el evento",
    )

    sesion = models.ForeignKey(
        "auth_app.Sesion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eventos_navegacion",
        help_text="Sesión en la que ocurrió el evento",
    )

    plataforma = models.ForeignKey(
        "integration.Plataforma",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eventos_navegacion",
        help_text="Plataforma donde ocurrió el evento",
    )

    tipo_evento = models.CharField(
        max_length=50,
        help_text="Tipo de evento: click, scroll, pageview, etc",
    )

    url = models.URLField(
        max_length=500,
        help_text="URL donde ocurrió el evento",
    )

    elemento_html = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Elemento HTML clickeado (ej: button#submit)",
    )

    coordenadas = models.JSONField(
        default=dict,
        blank=True,
        help_text="Posición X,Y del evento en formato JSON",
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora exacta del evento",
    )

    class Meta:
        db_table = "eventos_navegacion"
        verbose_name = "Evento de Navegación"
        verbose_name_plural = "Eventos de Navegación"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["usuario"]),
            models.Index(fields=["sesion"]),
            models.Index(fields=["plataforma"]),
            models.Index(fields=["tipo_evento"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "Anónimo"
        return f"{self.tipo_evento} - {usuario_str} - {self.timestamp}"

    def get_info_completa(self):
        return {
            "tipo": self.tipo_evento,
            "usuario": self.usuario.username if self.usuario else "Anónimo",
            "plataforma": self.plataforma.nombre if self.plataforma else "N/A",
            "url": self.url,
            "elemento": self.elemento_html or "N/A",
            "coordenadas": self.coordenadas,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }


class PaginaVisitada(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único de la página visitada",
    )

    usuario = models.ForeignKey(
        "auth_app.Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="paginas_visitadas",
        help_text="Usuario que visitó la página",
    )

    sesion = models.ForeignKey(
        "auth_app.Sesion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="paginas_visitadas",
        help_text="Sesión en la que se visitó la página",
    )

    plataforma = models.ForeignKey(
        "integration.Plataforma",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="paginas_visitadas",
        help_text="Plataforma donde está la página",
    )

    url = models.URLField(
        max_length=500,
        help_text="URL de la página visitada",
    )

    titulo_pagina = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Título de la página (HTML <title>)",
    )

    referrer = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL de donde vino el usuario (página anterior)",
    )

    tiempo_permanencia = models.IntegerField(
        default=0,
        help_text="Tiempo en segundos que permaneció en la página",
    )

    rebote = models.BooleanField(
        default=False,
        help_text="True si el usuario salió sin interactuar (bounce)",
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de la visita",
    )

    class Meta:
        db_table = "paginas_visitadas"
        verbose_name = "Página Visitada"
        verbose_name_plural = "Páginas Visitadas"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["usuario"]),
            models.Index(fields=["sesion"]),
            models.Index(fields=["plataforma"]),
            models.Index(fields=["timestamp"]),
            models.Index(fields=["rebote"]),
        ]

    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "Anónimo"
        return f"{usuario_str} - {self.url} - {self.tiempo_permanencia}s"

    def es_visita_larga(self):
        """Retorna True si el usuario permaneció más de 30 segundos"""
        return self.tiempo_permanencia > 30

    def get_info_completa(self):
        """Retorna información completa de la visita"""
        return {
            "usuario": self.usuario.username if self.usuario else "Anónimo",
            "plataforma": self.plataforma.nombre if self.plataforma else "N/A",
            "url": self.url,
            "titulo": self.titulo_pagina or "Sin título",
            "de_donde_vino": self.referrer or "Acceso directo",
            "tiempo_segundos": self.tiempo_permanencia,
            "es_rebote": self.rebote,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }


class Busqueda(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único de la búsqueda",
    )

    usuario = models.ForeignKey(
        "auth_app.Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="busquedas",
        help_text="Usuario que realizó la búsqueda",
    )

    sesion = models.ForeignKey(
        "auth_app.Sesion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="busquedas",
        help_text="Sesión en la que se realizó la búsqueda",
    )

    plataforma = models.ForeignKey(
        "integration.Plataforma",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="busquedas",
        help_text="Plataforma donde se realizó la búsqueda",
    )

    termino_busqueda = models.CharField(
        max_length=255,
        help_text="Texto que buscó el usuario",
    )

    cantidad_resultados = models.IntegerField(
        default=0,
        help_text="Número de resultados encontrados",
    )

    resultado_clickeado = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL del resultado que clickeó el usuario",
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de la búsqueda",
    )

    class Meta:
        db_table = "busquedas"
        verbose_name = "Búsqueda"
        verbose_name_plural = "Búsquedas"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["usuario"]),
            models.Index(fields=["sesion"]),
            models.Index(fields=["plataforma"]),
            models.Index(fields=["termino_busqueda"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "Anónimo"
        return f"{usuario_str} buscó '{self.termino_busqueda}' - {self.cantidad_resultados} resultados"

    def sin_resultados(self):
        """Retorna True si la búsqueda no encontró nada"""
        return self.cantidad_resultados == 0

    def clickeo_resultado(self):
        """Retorna True si el usuario clickeó algún resultado"""
        return self.resultado_clickeado is not None


class AccionUsuario(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único de la acción del usuario",
    )
    usuario = models.ForeignKey(
        "auth_app.Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acciones",
        help_text="Usuario que realizó la acción",
    )

    sesion = models.ForeignKey(
        "auth_app.Sesion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acciones",
        help_text="Sesión en la que se realizó la acción",
    )

    plataforma = models.ForeignKey(
        "integration.Plataforma",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acciones",
        help_text="Plataforma donde se realizó la acción",
    )

    tipo_accion = models.CharField(
        max_length=100,
        help_text="Tipo de acción: inscripcion_curso, descarga_recurso, envio_formulario, etc",
    )

    entidad_tipo = models.CharField(
        max_length=50,
        help_text="Tipo de entidad afectada: curso, recurso, certificado, formulario",
    )

    entidad_id = models.CharField(
        max_length=255,
        help_text="ID de la entidad afectada en la plataforma externa",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Datos adicionales de la acción en formato JSON",
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de la acción",
    )

    class Meta:
        db_table = "acciones_usuario"
        verbose_name = "Acción de Usuario"
        verbose_name_plural = "Acciones de Usuario"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["usuario"]),
            models.Index(fields=["sesion"]),
            models.Index(fields=["plataforma"]),
            models.Index(fields=["tipo_accion"]),
            models.Index(fields=["entidad_tipo"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "Anónimo"
        return f"{usuario_str} - {self.tipo_accion} - {self.entidad_tipo}"

    def get_info_completa(self):
        """Retorna información completa de la acción"""
        return {
            "usuario": self.usuario.username if self.usuario else "Anónimo",
            "plataforma": self.plataforma.nombre if self.plataforma else "N/A",
            "accion": self.tipo_accion,
            "entidad": f"{self.entidad_tipo} (ID: {self.entidad_id})",
            "metadata": self.metadata,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }


class MetricaAgregada(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único de la métrica",
    )

    tipo_metrica = models.CharField(
        max_length=100,
        help_text="Tipo de métrica: total_visitas, promedio_tiempo, ranking_cursos, etc",
    )

    entidad_tipo = models.CharField(
        max_length=50,
        help_text="Tipo de entidad: curso, plataforma, usuario, general",
    )

    entidad_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="ID de la entidad específica (NULL si es métrica general)",
    )

    PERIODO_CHOICES = [
        ("diario", "Diario"),
        ("semanal", "Semanal"),
        ("mensual", "Mensual"),
        ("anual", "Anual"),
    ]

    periodo = models.CharField(
        max_length=20,
        choices=PERIODO_CHOICES,
        help_text="Período de agregación",
    )

    fecha_inicio = models.DateField(
        help_text="Fecha de inicio del período",
    )

    fecha_fin = models.DateField(
        help_text="Fecha de fin del período",
    )

    valor = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Valor calculado de la métrica",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Datos adicionales de la métrica en formato JSON",
    )

    calculado_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora en que se calculó la métrica",
    )

    class Meta:
        db_table = "metricas_agregadas"
        verbose_name = "Métrica Agregada"
        verbose_name_plural = "Métricas Agregadas"
        ordering = ["-calculado_en"]
        indexes = [
            models.Index(fields=["tipo_metrica"]),
            models.Index(fields=["entidad_tipo"]),
            models.Index(fields=["periodo"]),
            models.Index(fields=["fecha_inicio", "fecha_fin"]),
            models.Index(fields=["calculado_en"]),
        ]

    def __str__(self):
        entidad = f" - {self.entidad_id}" if self.entidad_id else ""
        return f"{self.tipo_metrica} ({self.periodo}){entidad}: {self.valor}"

    def get_info_completa(self):
        return {
            "tipo": self.tipo_metrica,
            "entidad": f"{self.entidad_tipo} ({self.entidad_id})"
            if self.entidad_id
            else self.entidad_tipo,
            "periodo": self.get_periodo_display(),
            "rango": f"{self.fecha_inicio} a {self.fecha_fin}",
            "valor": str(self.valor),
            "metadata": self.metadata,
            "calculado": self.calculado_en.strftime("%Y-%m-%d %H:%M:%S"),
        }


class ConfiguracionReporte(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único de la configuración",
    )

    nombre = models.CharField(
        max_length=255,
        help_text="Nombre descriptivo del reporte",
    )

    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción detallada del reporte",
    )

    TIPO_REPORTE_CHOICES = [
        ("cursos", "Cursos"),
        ("usuarios", "Usuarios"),
        ("analytics", "Analytics"),
        ("plataformas", "Plataformas"),
        ("general", "General"),
    ]

    tipo_reporte = models.CharField(
        max_length=50,
        choices=TIPO_REPORTE_CHOICES,
        help_text="Tipo/categoría del reporte",
    )

    filtros = models.JSONField(
        default=dict,
        blank=True,
        help_text="Filtros configurados en formato JSON",
    )

    columnas = models.JSONField(
        default=list,
        blank=True,
        help_text="Columnas a mostrar en el reporte",
    )

    visualizaciones = models.JSONField(
        default=list,
        blank=True,
        help_text="Gráficos y visualizaciones configurados",
    )

    FRECUENCIA_CHOICES = [
        ("manual", "Manual"),
        ("diario", "Diario"),
        ("semanal", "Semanal"),
        ("mensual", "Mensual"),
    ]

    frecuencia = models.CharField(
        max_length=20,
        choices=FRECUENCIA_CHOICES,
        default="manual",
        help_text="Frecuencia de generación automática",
    )

    destinatarios_email = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista de emails que reciben el reporte automático",
    )

    creado_por = models.ForeignKey(
        "auth_app.Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="configuraciones_reporte",
        help_text="Usuario que creó esta configuración",
    )

    activo = models.BooleanField(
        default=True,
        help_text="Si la configuración está activa",
    )

    creado_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación",
    )

    class Meta:
        db_table = "configuraciones_reporte"
        verbose_name = "Configuración de Reporte"
        verbose_name_plural = "Configuraciones de Reportes"
        ordering = ["-creado_en"]
        indexes = [
            models.Index(fields=["tipo_reporte"]),
            models.Index(fields=["frecuencia"]),
            models.Index(fields=["activo"]),
            models.Index(fields=["creado_por"]),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_reporte_display()}) - {self.get_frecuencia_display()}"

    def get_info_completa(self):
        creador = self.creado_por.username if self.creado_por else "Sistema"
        return {
            "nombre": self.nombre,
            "tipo": self.get_tipo_reporte_display(),
            "frecuencia": self.get_frecuencia_display(),
            "filtros": self.filtros,
            "columnas": self.columnas,
            "destinatarios": len(self.destinatarios_email),
            "creado_por": creador,
            "activo": self.activo,
        }


class Reporte(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único del reporte",
    )

    configuracion = models.ForeignKey(
        "ConfiguracionReporte",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reportes",
        help_text="Configuración usada para generar este reporte",
    )

    nombre = models.CharField(
        max_length=255,
        help_text="Nombre del reporte generado",
    )

    periodo_inicio = models.DateField(
        help_text="Fecha de inicio de los datos del reporte",
    )

    periodo_fin = models.DateField(
        help_text="Fecha de fin de los datos del reporte",
    )

    ESTADO_CHOICES = [
        ("generando", "Generando"),
        ("completado", "Completado"),
        ("error", "Error"),
    ]

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="generando",
        help_text="Estado actual del reporte",
    )

    ruta_archivo = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Ruta donde se guardó el archivo del reporte",
    )

    tamano_bytes = models.BigIntegerField(
        blank=True,
        null=True,
        help_text="Tamaño del archivo en bytes",
    )

    mensaje_error = models.TextField(
        blank=True,
        null=True,
        help_text="Mensaje de error si la generación falló",
    )

    solicitado_por = models.ForeignKey(
        "auth_app.Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reportes_solicitados",
        help_text="Usuario que solicitó el reporte",
    )

    generado_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de generación",
    )

    class Meta:
        db_table = "reportes"
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"
        ordering = ["-generado_en"]
        indexes = [
            models.Index(fields=["configuracion"]),
            models.Index(fields=["estado"]),
            models.Index(fields=["solicitado_por"]),
            models.Index(fields=["periodo_inicio", "periodo_fin"]),
            models.Index(fields=["generado_en"]),
        ]

    def __str__(self):
        return f"{self.nombre} - {self.get_estado_display()} - {self.generado_en.strftime('%Y-%m-%d')}"

    def fue_exitoso(self):
        """Retorna True si el reporte se generó correctamente"""
        return self.estado == "completado"

    def get_tamano_legible(self):
        """Retorna el tamaño en formato legible (KB, MB)"""
        if not self.tamano_bytes:
            return "N/A"

        if self.tamano_bytes < 1024:
            return f"{self.tamano_bytes} bytes"
        elif self.tamano_bytes < 1024 * 1024:
            kb = self.tamano_bytes / 1024
            return f"{kb:.2f} KB"
        else:
            mb = self.tamano_bytes / (1024 * 1024)
            return f"{mb:.2f} MB"

    def get_info_completa(self):
        solicitante = self.solicitado_por.username if self.solicitado_por else "Sistema"
        return {
            "nombre": self.nombre,
            "estado": self.get_estado_display(),
            "periodo": f"{self.periodo_inicio} a {self.periodo_fin}",
            "tamaño": self.get_tamano_legible(),
            "solicitado_por": solicitante,
            "generado": self.generado_en.strftime("%Y-%m-%d %H:%M:%S"),
            "ruta": self.ruta_archivo or "N/A",
        }


class Exportacion(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único de la exportación",
    )

    reporte = models.ForeignKey(
        "Reporte",
        on_delete=models.CASCADE,
        related_name="exportaciones",
        help_text="Reporte que fue exportado",
    )

    usuario = models.ForeignKey(
        "auth_app.Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exportaciones",
        help_text="Usuario que exportó el reporte",
    )

    FORMATO_CHOICES = [
        ("pdf", "PDF"),
        ("xlsx", "Excel (XLSX)"),
        ("csv", "CSV"),
    ]

    formato = models.CharField(
        max_length=10,
        choices=FORMATO_CHOICES,
        help_text="Formato de exportación",
    )

    ruta_descarga = models.CharField(
        max_length=500,
        help_text="Ubicación del archivo exportado",
    )

    tamano_bytes = models.BigIntegerField(
        help_text="Tamaño del archivo exportado en bytes",
    )

    exportado_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de la exportación",
    )

    class Meta:
        db_table = "exportaciones"
        verbose_name = "Exportación"
        verbose_name_plural = "Exportaciones"
        ordering = ["-exportado_en"]
        indexes = [
            models.Index(fields=["reporte"]),
            models.Index(fields=["usuario"]),
            models.Index(fields=["formato"]),
            models.Index(fields=["exportado_en"]),
        ]

    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "Anónimo"
        return f"{usuario_str} exportó a {self.get_formato_display()} - {self.exportado_en.strftime('%Y-%m-%d')}"

    def get_tamano_legible(self):
        """Retorna el tamaño en formato legible (KB, MB)"""
        if self.tamano_bytes < 1024:
            return f"{self.tamano_bytes} bytes"
        elif self.tamano_bytes < 1024 * 1024:
            kb = self.tamano_bytes / 1024
            return f"{kb:.2f} KB"
        else:
            mb = self.tamano_bytes / (1024 * 1024)
            return f"{mb:.2f} MB"

    def get_info_completa(self):
        """Retorna información completa de la exportación"""
        return {
            "usuario": self.usuario.username if self.usuario else "Anónimo",
            "reporte": self.reporte.nombre,
            "formato": self.get_formato_display(),
            "tamaño": self.get_tamano_legible(),
            "ruta": self.ruta_descarga,
            "exportado": self.exportado_en.strftime("%Y-%m-%d %H:%M:%S"),
        }
