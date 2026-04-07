# api/serializers/system_serializers.py

from rest_framework import serializers
from system_app.models import ConfiguracionSistema
import json
from system_app.models import MensajeDashboard, MensajeDashboardRol, ArchivoSistema
from auth_app.models import Rol


class ConfiguracionSistemaSerializer(serializers.ModelSerializer):
    """
    Serializer base para ConfiguracionSistema.
    Incluye el campo valor_convertido que automáticamente parsea JSON/números/booleanos.
    """

    valor_convertido = serializers.SerializerMethodField()

    class Meta:
        model = ConfiguracionSistema
        fields = [
            "id",
            "clave",
            "valor",
            "tipo",
            "descripcion",
            "categoria",
            "editable",
            "valor_convertido",
            "actualizado_en",
        ]
        read_only_fields = ["id", "actualizado_en"]

    def get_valor_convertido(self, obj):
        """
        Retorna el valor convertido según su tipo.
        Usa el método del modelo que ya convierte automáticamente.
        """
        return obj.get_valor_convertido()


# SERIALIZERS PARA TEMA/COLORES


class TemaColoresConfigSerializer(serializers.ModelSerializer):
    """
    Serializer para GET /api/config/tema

    Retorna el modelo ConfiguracionSistema completo con los colores parseados.
    Respuesta ejemplo:
    {
        "id": "uuid",
        "clave": "tema_colores",
        "colores": {
            "color_primario": "#1976d2",
            "color_secundario": "#dc004e",
            ...
        },
        "actualizado_en": "2026-01-26T10:30:00Z"
    }
    """

    colores = serializers.SerializerMethodField()

    class Meta:
        model = ConfiguracionSistema
        fields = ["id", "clave", "colores", "actualizado_en"]
        read_only_fields = ["id", "clave", "actualizado_en"]

    def get_colores(self, obj):
        """
        Extrae y retorna solo los colores del JSON almacenado.
        Si hay error, retorna valores por defecto.
        """
        try:
            return json.loads(obj.valor)
        except (json.JSONDecodeError, AttributeError):
            return {
                "color_primario": "#1976d2",
                "color_secundario": "#dc004e",
                "color_fondo": "#ffffff",
                "color_texto": "#000000",
                "color_navbar": "#1976d2",
                "color_footer": "#424242",
            }


class TemaColoresInputSerializer(serializers.Serializer):
    """
    Serializer para PUT /api/config/tema/actualizar/

    Valida el input del usuario al actualizar colores.
    Solo acepta colores en formato HEX (#RGB o #RRGGBB).
    """

    color_primario = serializers.CharField(
        max_length=20,
        default="#1976d2",
        help_text="Color primario en formato HEX (ej: #1976d2)",
    )

    color_secundario = serializers.CharField(
        max_length=20,
        default="#dc004e",
        help_text="Color secundario en formato HEX (ej: #dc004e)",
    )

    color_fondo = serializers.CharField(
        max_length=20,
        default="#ffffff",
        help_text="Color de fondo en formato HEX (ej: #ffffff)",
    )

    color_texto = serializers.CharField(
        max_length=20,
        default="#000000",
        help_text="Color de texto principal en formato HEX (ej: #000000)",
    )

    color_navbar = serializers.CharField(
        max_length=20,
        default="#1976d2",
        help_text="Color de la barra de navegación en formato HEX",
    )

    color_footer = serializers.CharField(
        max_length=20, default="#424242", help_text="Color del footer en formato HEX"
    )

    def validate_color_primario(self, value):
        """Validar formato HEX del color primario"""
        if not value.startswith("#") or len(value) not in [4, 7]:
            raise serializers.ValidationError(
                "Debe ser un color HEX válido (#RGB o #RRGGBB)"
            )
        return value

    def validate_color_secundario(self, value):
        """Validar formato HEX del color secundario"""
        if not value.startswith("#") or len(value) not in [4, 7]:
            raise serializers.ValidationError(
                "Debe ser un color HEX válido (#RGB o #RRGGBB)"
            )
        return value

    def validate_color_fondo(self, value):
        """Validar formato HEX del color de fondo"""
        if not value.startswith("#") or len(value) not in [4, 7]:
            raise serializers.ValidationError(
                "Debe ser un color HEX válido (#RGB o #RRGGBB)"
            )
        return value

    def validate_color_texto(self, value):
        """Validar formato HEX del color de texto"""
        if not value.startswith("#") or len(value) not in [4, 7]:
            raise serializers.ValidationError(
                "Debe ser un color HEX válido (#RGB o #RRGGBB)"
            )
        return value

    def validate_color_navbar(self, value):
        """Validar formato HEX del color de navbar"""
        if not value.startswith("#") or len(value) not in [4, 7]:
            raise serializers.ValidationError(
                "Debe ser un color HEX válido (#RGB o #RRGGBB)"
            )
        return value

    def validate_color_footer(self, value):
        """Validar formato HEX del color de footer"""
        if not value.startswith("#") or len(value) not in [4, 7]:
            raise serializers.ValidationError(
                "Debe ser un color HEX válido (#RGB o #RRGGBB)"
            )
        return value


# SERIALIZERS DE SOLO LECTURA (PARA GET)


class MensajeDashboardListSerializer(serializers.ModelSerializer):
    """
    Serializer para listar mensajes (usado en GET de lista).
    Incluye información resumida y roles asignados.
    """

    roles_asignados = serializers.SerializerMethodField()
    creado_por_username = serializers.SerializerMethodField()
    esta_vigente = serializers.SerializerMethodField()

    class Meta:
        model = MensajeDashboard
        fields = [
            "id",
            "titulo",
            "mensaje",
            "activo",
            "prioridad",
            "fecha_inicio",
            "fecha_fin",
            "esta_vigente",
            "roles_asignados",
            "creado_por",
            "creado_por_username",
            "creado_en",
            "actualizado_en",
        ]
        read_only_fields = fields

    def get_roles_asignados(self, obj):
        """Retorna lista de roles asignados al mensaje"""
        return [
            {"id": str(rel.rol.id), "nombre": rel.rol.nombre}
            for rel in obj.roles.select_related("rol").all()
        ]

    def get_creado_por_username(self, obj):
        return obj.creado_por.username if obj.creado_por else "Sistema"

    def get_esta_vigente(self, obj):
        return obj.esta_vigente()


class MensajeDashboardDetailSerializer(serializers.ModelSerializer):
    """
    Serializer para detalle de mensaje (usado en GET de detalle).
    Incluye toda la información del mensaje.
    """

    roles_asignados = serializers.SerializerMethodField()
    creado_por_info = serializers.SerializerMethodField()
    esta_vigente = serializers.SerializerMethodField()

    class Meta:
        model = MensajeDashboard
        fields = [
            "id",
            "titulo",
            "mensaje",
            "imagen_url",
            "color_fondo",
            "enlace_url",
            "enlace_texto",
            "activo",
            "prioridad",
            "fecha_inicio",
            "fecha_fin",
            "esta_vigente",
            "roles_asignados",
            "creado_por",
            "creado_por_info",
            "creado_en",
            "actualizado_en",
        ]
        read_only_fields = fields

    def get_roles_asignados(self, obj):
        return [
            {
                "id": str(rel.rol.id),
                "nombre": rel.rol.nombre,
                "descripcion": rel.rol.descripcion,
                "asignado_en": rel.asignado_en,
            }
            for rel in obj.roles.select_related("rol").all()
        ]

    def get_creado_por_info(self, obj):
        if not obj.creado_por:
            return None
        return {
            "id": str(obj.creado_por.id),
            "username": obj.creado_por.username,
            "nombre_completo": obj.creado_por.get_nombre_completo(),
        }

    def get_esta_vigente(self, obj):
        return obj.esta_vigente()


class MensajeUsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para mensajes del usuario autenticado.
    Solo muestra información necesaria para el dashboard.
    """

    class Meta:
        model = MensajeDashboard
        fields = [
            "id",
            "titulo",
            "mensaje",
            "imagen_url",
            "color_fondo",
            "enlace_url",
            "enlace_texto",
            "prioridad",
        ]
        read_only_fields = fields


# SERIALIZERS DE ESCRITURA (PARA POST, PUT, PATCH)


class MensajeDashboardCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear mensajes (POST).
    Permite seleccionar múltiples roles.
    """

    roles_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        help_text="Lista de IDs de roles a los que va dirigido el mensaje",
        min_length=1,  # Al menos un rol requerido
    )

    class Meta:
        model = MensajeDashboard
        fields = [
            "titulo",
            "mensaje",
            "imagen_url",
            "color_fondo",
            "enlace_url",
            "enlace_texto",
            "activo",
            "prioridad",
            "fecha_inicio",
            "fecha_fin",
            "roles_ids",
        ]

    def validate_roles_ids(self, value):
        """Valida que todos los roles existan"""
        roles = Rol.objects.filter(id__in=value, activo=True)
        if len(roles) != len(value):
            raise serializers.ValidationError(
                "Uno o más roles no existen o están inactivos"
            )
        return value

    def validate(self, data):
        """Validaciones adicionales"""
        # Validar que fecha_fin sea posterior a fecha_inicio
        if data.get("fecha_inicio") and data.get("fecha_fin"):
            if data["fecha_fin"] < data["fecha_inicio"]:
                raise serializers.ValidationError(
                    {
                        "fecha_fin": "La fecha de fin debe ser posterior a la fecha de inicio"
                    }
                )

        return data

    def create(self, validated_data):
        """Crear mensaje y asignar roles"""
        roles_ids = validated_data.pop("roles_ids")

        # Obtener el usuario del contexto
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["creado_por"] = request.user

        # Crear el mensaje
        mensaje = MensajeDashboard.objects.create(**validated_data)

        # Asignar roles
        for rol_id in roles_ids:
            MensajeDashboardRol.objects.create(mensaje=mensaje, rol_id=rol_id)

        return mensaje


class MensajeDashboardUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar mensajes (PUT, PATCH).
    Permite modificar roles asignados.
    """

    roles_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        help_text="Lista de IDs de roles (opcional, solo si quieres cambiar roles)",
    )

    class Meta:
        model = MensajeDashboard
        fields = [
            "titulo",
            "mensaje",
            "imagen_url",
            "color_fondo",
            "enlace_url",
            "enlace_texto",
            "activo",
            "prioridad",
            "fecha_inicio",
            "fecha_fin",
            "roles_ids",
        ]

    def validate_roles_ids(self, value):
        """Valida que todos los roles existan"""
        if value:
            roles = Rol.objects.filter(id__in=value, activo=True)
            if len(roles) != len(value):
                raise serializers.ValidationError(
                    "Uno o más roles no existen o están inactivos"
                )
        return value

    def validate(self, data):
        """Validaciones adicionales"""
        instance = self.instance

        # Obtener fechas actuales si no se envían
        fecha_inicio = data.get(
            "fecha_inicio", instance.fecha_inicio if instance else None
        )
        fecha_fin = data.get("fecha_fin", instance.fecha_fin if instance else None)

        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise serializers.ValidationError(
                {"fecha_fin": "La fecha de fin debe ser posterior a la fecha de inicio"}
            )

        return data

    def update(self, instance, validated_data):
        """Actualizar mensaje y roles si se especifican"""
        roles_ids = validated_data.pop("roles_ids", None)

        # Actualizar campos del mensaje
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Si se enviaron roles, actualizar las asignaciones
        if roles_ids is not None:
            # Eliminar asignaciones actuales
            instance.roles.all().delete()

            # Crear nuevas asignaciones
            for rol_id in roles_ids:
                MensajeDashboardRol.objects.create(mensaje=instance, rol_id=rol_id)

        return instance


# SERIALIZER PARA FILTROS


class MensajeDashboardFiltrosSerializer(serializers.Serializer):
    """
    Serializer para validar filtros de búsqueda de mensajes.
    """

    activo = serializers.BooleanField(required=False)
    vigente = serializers.BooleanField(required=False)
    rol_id = serializers.UUIDField(required=False)
    fecha_desde = serializers.DateField(required=False)
    fecha_hasta = serializers.DateField(required=False)


# SERIALIZERS PARA ARCHIVOS DEL SISTEMA
# ==============================================================================


class ArchivoSistemaListSerializer(serializers.ModelSerializer):
    """
    Serializer para listado de archivos (GET lista).
    """

    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    archivo_url = serializers.SerializerMethodField()
    tamano = serializers.SerializerMethodField()

    class Meta:
        model = ArchivoSistema
        fields = [
            "id",
            "nombre",
            "archivo_url",
            "tamano",
            "estado",
            "estado_display",
            "creado_en",
            "actualizado_en",
        ]
        read_only_fields = fields

    def get_archivo_url(self, obj):
        if obj.archivo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.archivo.url)
            return obj.archivo.url
        return None

    def get_tamano(self, obj):
        return obj.get_tamano_legible()


class ArchivoSistemaDetailSerializer(serializers.ModelSerializer):
    """
    Serializer para detalle de archivo (GET detalle).
    """

    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    archivo_url = serializers.SerializerMethodField()
    tamano = serializers.SerializerMethodField()

    class Meta:
        model = ArchivoSistema
        fields = [
            "id",
            "nombre",
            "archivo",
            "archivo_url",
            "tamano",
            "estado",
            "estado_display",
            "creado_en",
            "actualizado_en",
        ]
        read_only_fields = ["id", "creado_en", "actualizado_en"]

    def get_archivo_url(self, obj):
        if obj.archivo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.archivo.url)
            return obj.archivo.url
        return None

    def get_tamano(self, obj):
        return obj.get_tamano_legible()


class ArchivoSistemaCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear y actualizar archivos (POST/PATCH).
    """

    class Meta:
        model = ArchivoSistema
        fields = [
            "id",
            "nombre",
            "archivo",
            "estado",
        ]
        read_only_fields = ["id"]

    def validate_nombre(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre es requerido")
        return value.strip()

    def validate_archivo(self, value):
        if not value:
            raise serializers.ValidationError("Debe adjuntar un archivo")

        # Validar tamaño máximo (10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError("El archivo no puede superar los 10MB")

        return value
