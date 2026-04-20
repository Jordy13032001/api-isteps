# api/serializers/analytics_serializers.py

from rest_framework import serializers
from analytics.models import (
    EventoNavegacion,
    MetricaAgregada,
    ConfiguracionReporte,
    Reporte,
    Exportacion,
)
from system_app.models import LogAuditoria


# SERIALIZERS PARA EVENTOS DE NAVEGACIÓN
class EventoNavegacionSerializer(serializers.ModelSerializer):
    """
    Serializer para lectura de eventos de navegación.
    Usado en GET /api/analitica/eventos/
    """

    usuario_username = serializers.SerializerMethodField()
    plataforma_nombre = serializers.SerializerMethodField()

    class Meta:
        model = EventoNavegacion
        fields = [
            "id",
            "usuario",
            "usuario_username",
            "sesion",
            "plataforma",
            "plataforma_nombre",
            "tipo_evento",
            "url",
            "elemento_html",
            "coordenadas",
            "timestamp",
        ]
        read_only_fields = ["id", "timestamp"]

    def get_usuario_username(self, obj):
        """Retorna el username del usuario o 'Anónimo'"""
        return obj.usuario.username if obj.usuario else "Anónimo"

    def get_plataforma_nombre(self, obj):
        """Retorna el nombre de la plataforma o 'N/A'"""
        return obj.plataforma.nombre if obj.plataforma else "N/A"


class EventoNavegacionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear eventos de navegación.
    Usado en POST /api/analitica/eventos/

    El frontend envía eventos cuando el usuario:
    - Hace click en elementos
    - Navega entre páginas (pageview)
    - Hace scroll
    - Interactúa con elementos específicos
    """

    class Meta:
        model = EventoNavegacion
        fields = [
            "usuario",
            "sesion",
            "plataforma",
            "tipo_evento",
            "url",
            "elemento_html",
            "coordenadas",
        ]

    def validate_tipo_evento(self, value):
        """Validar que el tipo de evento sea válido"""
        tipos_validos = [
            "click",
            "scroll",
            "pageview",
            "submit",
            "hover",
            "focus",
            "blur",
        ]
        if value.lower() not in tipos_validos:
            raise serializers.ValidationError(
                f"Tipo de evento inválido. Valores permitidos: {', '.join(tipos_validos)}"
            )
        return value.lower()

    def validate_url(self, value):
        """Validar que la URL no esté vacía"""
        if not value or not value.strip():
            raise serializers.ValidationError("La URL del evento es requerida")
        return value.strip()


# SERIALIZERS PARA DASHBOARD DE MÉTRICAS
class DashboardMetricasSerializer(serializers.Serializer):
    """
    Serializer para las métricas del dashboard.
    Usado en GET /api/analitica/dashboard/

    No está ligado a un modelo específico, agrupa datos calculados.
    """

    # Métricas generales
    total_visitas_hoy = serializers.IntegerField()
    total_visitas_semana = serializers.IntegerField()
    total_visitas_mes = serializers.IntegerField()

    # Usuarios
    usuarios_activos_hoy = serializers.IntegerField()
    usuarios_nuevos_semana = serializers.IntegerField()

    # Páginas más visitadas
    paginas_top = serializers.ListField(
        child=serializers.DictField(),
        help_text="Lista de páginas más visitadas con conteo",
    )

    # Búsquedas más frecuentes
    busquedas_top = serializers.ListField(
        child=serializers.DictField(), help_text="Lista de términos más buscados"
    )

    # Distribución por plataforma
    visitas_por_plataforma = serializers.ListField(
        child=serializers.DictField(),
        help_text="Distribución de visitas por plataforma",
    )

    # Eventos por tipo
    eventos_por_tipo = serializers.ListField(
        child=serializers.DictField(), help_text="Distribución de eventos por tipo"
    )

    # Período de los datos
    periodo_inicio = serializers.DateField()
    periodo_fin = serializers.DateField()
    generado_en = serializers.DateTimeField()


class DashboardFiltrosSerializer(serializers.Serializer):
    """
    Serializer para validar los filtros del dashboard.
    Query params para GET /api/analitica/dashboard/
    """

    fecha_inicio = serializers.DateField(required=False)
    fecha_fin = serializers.DateField(required=False)
    plataforma_id = serializers.UUIDField(required=False)
    tipo_metrica = serializers.ChoiceField(
        choices=["visitas", "usuarios", "busquedas", "eventos"],
        required=False,
        default="visitas",
    )

    def validate(self, attrs):
        """Validar que fecha_inicio sea menor que fecha_fin"""
        fecha_inicio = attrs.get("fecha_inicio")
        fecha_fin = attrs.get("fecha_fin")

        if fecha_inicio and fecha_fin:
            if fecha_inicio > fecha_fin:
                raise serializers.ValidationError(
                    {"fecha_fin": "La fecha fin debe ser posterior a la fecha inicio"}
                )
        return attrs


# SERIALIZERS PARA LOGS DE AUDITORÍA


class LogAuditoriaSerializer(serializers.ModelSerializer):
    """
    Serializer para lectura de logs de auditoría.
    Usado en GET /api/seguridad/logs/
    """

    usuario_username = serializers.SerializerMethodField()
    nivel_display = serializers.SerializerMethodField()

    class Meta:
        model = LogAuditoria
        fields = [
            "id",
            "usuario",
            "usuario_username",
            "accion",
            "entidad_tipo",
            "entidad_id",
            "valores_anteriores",
            "valores_nuevos",
            "ip_address",
            "user_agent",
            "nivel",
            "nivel_display",
            "timestamp",
        ]
        read_only_fields = fields  # Todos son de solo lectura

    def get_usuario_username(self, obj):
        """Retorna el username del usuario o 'Sistema'"""
        return obj.usuario.username if obj.usuario else "Sistema"

    def get_nivel_display(self, obj):
        """Retorna el nombre legible del nivel"""
        return obj.get_nivel_display()


class LogAuditoriaListSerializer(serializers.ModelSerializer):
    """
    Serializer resumido para listado de logs.
    Menos campos para mejor rendimiento en listados grandes.
    """

    usuario_username = serializers.SerializerMethodField()

    class Meta:
        model = LogAuditoria
        fields = [
            "id",
            "usuario_username",
            "accion",
            "entidad_tipo",
            "nivel",
            "ip_address",
            "timestamp",
        ]

    def get_usuario_username(self, obj):
        return obj.usuario.username if obj.usuario else "Sistema"


class LogAuditoriaFiltrosSerializer(serializers.Serializer):
    """
    Serializer para validar filtros de búsqueda de logs.
    Query params para GET /api/seguridad/logs/
    """

    usuario_id = serializers.UUIDField(required=False)
    accion = serializers.CharField(max_length=100, required=False)
    entidad_tipo = serializers.CharField(max_length=50, required=False)
    nivel = serializers.ChoiceField(
        choices=["INFO", "WARNING", "ERROR", "CRITICAL"], required=False
    )
    fecha_inicio = serializers.DateTimeField(required=False)
    fecha_fin = serializers.DateTimeField(required=False)


# SERIALIZERS PARA REPORTES
class ReporteSerializer(serializers.ModelSerializer):
    """
    Serializer para lectura de reportes.
    Usado en GET /api/reportes/historia/
    """

    solicitado_por_username = serializers.SerializerMethodField()
    estado_display = serializers.SerializerMethodField()
    tamano_legible = serializers.SerializerMethodField()
    configuracion_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Reporte
        fields = [
            "id",
            "configuracion",
            "configuracion_nombre",
            "nombre",
            "periodo_inicio",
            "periodo_fin",
            "estado",
            "estado_display",
            "ruta_archivo",
            "tamano_bytes",
            "tamano_legible",
            "mensaje_error",
            "solicitado_por",
            "solicitado_por_username",
            "generado_en",
        ]
        read_only_fields = fields

    def get_solicitado_por_username(self, obj):
        """Retorna el username de quien solicitó el reporte"""
        return obj.solicitado_por.username if obj.solicitado_por else "Sistema"

    def get_estado_display(self, obj):
        """Retorna el nombre legible del estado"""
        return obj.get_estado_display()

    def get_tamano_legible(self, obj):
        """Retorna el tamaño en formato legible"""
        return obj.get_tamano_legible()

    def get_configuracion_nombre(self, obj):
        """Retorna el nombre de la configuración usada"""
        return obj.configuracion.nombre if obj.configuracion else "Reporte manual"


class ReporteListSerializer(serializers.ModelSerializer):
    """
    Serializer resumido para listado de reportes.
    """

    solicitado_por_username = serializers.SerializerMethodField()
    tamano_legible = serializers.SerializerMethodField()

    class Meta:
        model = Reporte
        fields = [
            "id",
            "nombre",
            "estado",
            "periodo_inicio",
            "periodo_fin",
            "tamano_legible",
            "solicitado_por_username",
            "generado_en",
        ]

    def get_solicitado_por_username(self, obj):
        return obj.solicitado_por.username if obj.solicitado_por else "Sistema"

    def get_tamano_legible(self, obj):
        return obj.get_tamano_legible()


class ReporteGenerarSerializer(serializers.Serializer):
    """
    Serializer para solicitar generación de reporte.
    Usado en POST /api/reports/generador/
    """

    nombre = serializers.CharField(
        max_length=255, help_text="Nombre descriptivo del reporte"
    )

    tipo_reporte = serializers.ChoiceField(
        choices=["cursos", "usuarios", "analytics", "plataformas", "general"],
        help_text="Tipo de reporte a generar",
    )

    periodo_inicio = serializers.DateField(
        help_text="Fecha de inicio del período de datos"
    )

    periodo_fin = serializers.DateField(help_text="Fecha de fin del período de datos")

    configuracion_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="ID de configuración predefinida (opcional)",
    )

    filtros = serializers.JSONField(
        required=False, default=dict, help_text="Filtros adicionales en formato JSON"
    )

    formato_salida = serializers.ChoiceField(
        choices=["pdf", "xlsx", "csv"],
        default="pdf",
        help_text="Formato del archivo de salida",
    )

    def validate(self, attrs):
        """Validar fechas y parámetros"""
        periodo_inicio = attrs.get("periodo_inicio")
        periodo_fin = attrs.get("periodo_fin")

        if periodo_inicio and periodo_fin:
            if periodo_inicio > periodo_fin:
                raise serializers.ValidationError(
                    {"periodo_fin": "La fecha fin debe ser posterior a la fecha inicio"}
                )

            if (periodo_fin - periodo_inicio).days > 365:
                raise serializers.ValidationError(
                    {"periodo_fin": "El período no puede ser mayor a 1 año"}
                )

        return attrs

    def validate_nombre(self, value):
        """Validar que el nombre no esté vacío"""
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre del reporte es requerido")
        return value.strip()


# SERIALIZERS PARA CONFIGURACIÓN DE REPORTES
class ConfiguracionReporteSerializer(serializers.ModelSerializer):
    """
    Serializer completo para configuraciones de reporte.
    """

    creado_por_username = serializers.SerializerMethodField()
    tipo_reporte_display = serializers.SerializerMethodField()
    frecuencia_display = serializers.SerializerMethodField()

    class Meta:
        model = ConfiguracionReporte
        fields = [
            "id",
            "nombre",
            "descripcion",
            "tipo_reporte",
            "tipo_reporte_display",
            "filtros",
            "columnas",
            "visualizaciones",
            "frecuencia",
            "frecuencia_display",
            "destinatarios_email",
            "creado_por",
            "creado_por_username",
            "activo",
            "creado_en",
        ]
        read_only_fields = ["id", "creado_en"]

    def get_creado_por_username(self, obj):
        return obj.creado_por.username if obj.creado_por else "Sistema"

    def get_tipo_reporte_display(self, obj):
        return obj.get_tipo_reporte_display()

    def get_frecuencia_display(self, obj):
        return obj.get_frecuencia_display()


# SERIALIZERS PARA MÉTRICAS AGREGADAS
class MetricaAgregadaSerializer(serializers.ModelSerializer):
    """
    Serializer para métricas agregadas pre-calculadas.
    """

    periodo_display = serializers.SerializerMethodField()

    class Meta:
        model = MetricaAgregada
        fields = [
            "id",
            "tipo_metrica",
            "entidad_tipo",
            "entidad_id",
            "periodo",
            "periodo_display",
            "fecha_inicio",
            "fecha_fin",
            "valor",
            "metadata",
            "calculado_en",
        ]
        read_only_fields = fields

    def get_periodo_display(self, obj):
        return obj.get_periodo_display()


# SERIALIZERS PARA EXPORTACIONES
class ExportacionSerializer(serializers.ModelSerializer):
    """
    Serializer completo para exportaciones de reportes.
    Usado en GET para listar exportaciones.
    """

    usuario_username = serializers.SerializerMethodField()
    reporte_nombre = serializers.SerializerMethodField()
    formato_display = serializers.SerializerMethodField()
    tamano_legible = serializers.SerializerMethodField()

    class Meta:
        model = Exportacion
        fields = [
            "id",
            "reporte",
            "reporte_nombre",
            "usuario",
            "usuario_username",
            "formato",
            "formato_display",
            "ruta_descarga",
            "tamano_bytes",
            "tamano_legible",
            "exportado_en",
        ]
        read_only_fields = fields

    def get_usuario_username(self, obj):
        return obj.usuario.username if obj.usuario else "Sistema"

    def get_reporte_nombre(self, obj):
        return obj.reporte.nombre if obj.reporte else "N/A"

    def get_formato_display(self, obj):
        return obj.get_formato_display()

    def get_tamano_legible(self, obj):
        return obj.get_tamano_legible()


class ExportacionCreateSerializer(serializers.Serializer):
    """
    Serializer para solicitar exportación de un reporte.
    Usado en POST /api/reportes/{id}/exportar/
    """

    formato = serializers.ChoiceField(
        choices=["pdf", "xlsx", "csv"],
        help_text="Formato de exportación: pdf, xlsx, csv",
    )

    incluir_graficos = serializers.BooleanField(
        default=True,
        required=False,
        help_text="Incluir gráficos en la exportación (solo PDF/XLSX)",
    )

    def validate_formato(self, value):
        """Validar que el formato sea válido"""
        if value not in ["pdf", "xlsx", "csv"]:
            raise serializers.ValidationError(
                "Formato inválido. Valores permitidos: pdf, xlsx, csv"
            )
        return value
