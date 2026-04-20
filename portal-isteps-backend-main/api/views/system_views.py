# api/views/system_views.py
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAdminUser, AllowAny
from system_app.models import ConfiguracionSistema
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

from system_app.models import MensajeDashboard, ArchivoSistema
from auth_app.models import UsuarioRol
from api.serializers.system_serializers import (
    TemaColoresConfigSerializer,
    TemaColoresInputSerializer,
    MensajeDashboardListSerializer,
    MensajeDashboardDetailSerializer,
    MensajeUsuarioSerializer,
    MensajeDashboardCreateSerializer,
    MensajeDashboardUpdateSerializer,
    ArchivoSistemaListSerializer,
    ArchivoSistemaDetailSerializer,
    ArchivoSistemaCreateUpdateSerializer,
)
import json


# API: /api/config/tema (GET, PUT, PATCH)


class TemaColoresAPIView(APIView):
    """
    GET /api/config/tema/
    PUT /api/config/tema/
    PATCH /api/config/tema/

    Gestiona la configuración de colores del tema visual del portal.
    """

    def get_permissions(self):
        """GET es público, PUT/PATCH requieren admin"""
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request):
        """
        GET /api/config/tema/

        Obtiene la configuración de colores del tema visual.

        Permisos: Público (sin autenticación)

        Respuesta (200):
        {
            "id": "uuid",
            "clave": "tema_colores",
            "colores": {
                "color_primario": "#1976d2",
                "color_secundario": "#dc004e",
                "color_fondo": "#ffffff",
                "color_texto": "#000000",
                "color_navbar": "#1976d2",
                "color_footer": "#424242"
            },
            "actualizado_en": "2026-01-26T10:30:00Z"
        }
        """
        try:
            config = ConfiguracionSistema.objects.get(clave="tema_colores")
            serializer = TemaColoresConfigSerializer(config)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ConfiguracionSistema.DoesNotExist:
            valores_default = {
                "id": None,
                "clave": "tema_colores",
                "colores": {
                    "color_primario": "#1976d2",
                    "color_secundario": "#dc004e",
                    "color_fondo": "#ffffff",
                    "color_texto": "#000000",
                    "color_navbar": "#1976d2",
                    "color_footer": "#424242",
                },
                "actualizado_en": None,
            }
            return Response(valores_default, status=status.HTTP_200_OK)

    def put(self, request):
        """
        PUT /api/config/tema/

        Actualización completa de colores del tema.

        Permisos: Solo administradores

        Body (JSON):
        {
            "color_primario": "#00bcd4",
            "color_secundario": "#ff5722",
            "color_fondo": "#fafafa",
            "color_texto": "#212121",
            "color_navbar": "#00bcd4",
            "color_footer": "#263238"
        }
        """
        return self._actualizar_tema(request, partial=False)

    def patch(self, request):
        """
        PATCH /api/config/tema/

        Actualización parcial de colores del tema.

        Permisos: Solo administradores

        Body (JSON) - Solo los campos que quieras actualizar:
        {
            "color_primario": "#00bcd4"
        }
        """
        return self._actualizar_tema(request, partial=True)

    def _actualizar_tema(self, request, partial=False):
        """Método auxiliar para PUT y PATCH"""
        input_serializer = TemaColoresInputSerializer(
            data=request.data, partial=partial
        )

        if not input_serializer.is_valid():
            return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Obtener configuración existente o valores actuales
            try:
                config = ConfiguracionSistema.objects.get(clave="tema_colores")
                if partial:
                    # Para PATCH, combinar valores existentes con nuevos
                    valores_actuales = json.loads(config.valor)
                    valores_actuales.update(input_serializer.validated_data)
                    nuevos_valores = valores_actuales
                else:
                    # Para PUT, reemplazar todo
                    nuevos_valores = input_serializer.validated_data

                config.valor = json.dumps(nuevos_valores)
                config.save()
                created = False

            except ConfiguracionSistema.DoesNotExist:
                # Crear nueva configuración
                config = ConfiguracionSistema.objects.create(
                    clave="tema_colores",
                    tipo="json",
                    categoria="general",
                    descripcion="Colores del tema visual del portal",
                    editable=True,
                    valor=json.dumps(input_serializer.validated_data),
                )
                created = True

            output_serializer = TemaColoresConfigSerializer(config)

            mensaje = (
                "Configuración de colores creada exitosamente"
                if created
                else "Configuración de colores actualizada exitosamente"
            )

            return Response(
                {
                    "message": mensaje,
                    "data": output_serializer.data,
                },
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"Error al guardar la configuración: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# VIEWSET PARA MENSAJES DEL DASHBOARD


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200


class MensajeDashboardViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para gestionar Mensajes del Dashboard.

    Endpoints:
    - GET    /api/dashboard/mensajes/              → Lista todos (Admin)
    - GET    /api/dashboard/mensajes/{id}/         → Detalle (Admin)
    - POST   /api/dashboard/mensajes/              → Crear (Admin)
    - PUT    /api/dashboard/mensajes/{id}/         → Actualizar (Admin)
    - PATCH  /api/dashboard/mensajes/{id}/         → Actualizar parcial (Admin)
    - DELETE /api/dashboard/mensajes/{id}/         → Eliminar (Admin)
    - GET    /api/dashboard/mensajes/mis-mensajes/ → Mensajes del usuario
    """

    queryset = (
        MensajeDashboard.objects.select_related("creado_por")
        .prefetch_related("roles__rol")
        .all()
    )
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == "list":
            return MensajeDashboardListSerializer
        elif self.action == "retrieve":
            return MensajeDashboardDetailSerializer
        elif self.action == "create":
            return MensajeDashboardCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return MensajeDashboardUpdateSerializer
        elif self.action == "mis_mensajes":
            return MensajeUsuarioSerializer
        return MensajeDashboardListSerializer

    def get_permissions(self):
        if self.action == "mis_mensajes":
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        queryset = super().get_queryset()

        activo = self.request.query_params.get("activo")
        if activo is not None:
            activo_bool = activo.lower() in ["true", "1", "si", "yes"]
            queryset = queryset.filter(activo=activo_bool)

        vigente = self.request.query_params.get("vigente")
        if vigente is not None and vigente.lower() in ["true", "1", "si", "yes"]:
            hoy = timezone.now().date()
            queryset = queryset.filter(
                Q(fecha_inicio__isnull=True) | Q(fecha_inicio__lte=hoy),
                Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=hoy),
            )

        rol_id = self.request.query_params.get("rol_id")
        if rol_id:
            queryset = queryset.filter(roles__rol_id=rol_id).distinct()

        return queryset.order_by("prioridad", "-creado_en")

    def list(self, request, *args, **kwargs):
        """GET /api/dashboard/mensajes/"""
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"count": queryset.count(), "results": serializer.data})

    def retrieve(self, request, *args, **kwargs):
        """GET /api/dashboard/mensajes/{id}/"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """POST /api/dashboard/mensajes/"""
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            mensaje = serializer.save()
            output_serializer = MensajeDashboardDetailSerializer(mensaje)

            return Response(
                {
                    "message": "Mensaje creado exitosamente",
                    "data": output_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """PUT /api/dashboard/mensajes/{id}/"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            mensaje = serializer.save()
            output_serializer = MensajeDashboardDetailSerializer(mensaje)

            return Response(
                {
                    "message": "Mensaje actualizado exitosamente",
                    "data": output_serializer.data,
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        """PATCH /api/dashboard/mensajes/{id}/"""
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """DELETE /api/dashboard/mensajes/{id}/"""
        instance = self.get_object()
        titulo = instance.titulo
        instance.delete()

        return Response(
            {"message": f'Mensaje "{titulo}" eliminado exitosamente'},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def mis_mensajes(self, request):
        """
        GET /api/dashboard/mensajes/mis-mensajes/

        Obtiene los mensajes activos y vigentes para el usuario según sus roles.
        """
        roles_usuario = UsuarioRol.objects.filter(usuario=request.user).values_list(
            "rol_id", flat=True
        )

        if not roles_usuario:
            return Response(
                {
                    "count": 0,
                    "message": "El usuario no tiene roles asignados",
                    "results": [],
                },
                status=status.HTTP_200_OK,
            )

        hoy = timezone.now().date()

        mensajes = (
            MensajeDashboard.objects.filter(
                activo=True, roles__rol_id__in=roles_usuario
            )
            .filter(
                Q(fecha_inicio__isnull=True) | Q(fecha_inicio__lte=hoy),
                Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=hoy),
            )
            .distinct()
            .order_by("prioridad", "-creado_en")
        )

        serializer = MensajeUsuarioSerializer(mensajes, many=True)

        return Response({"count": mensajes.count(), "results": serializer.data})

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def activar(self, request, pk=None):
        """POST /api/dashboard/mensajes/{id}/activar/"""
        mensaje = self.get_object()

        if mensaje.activo:
            return Response(
                {"message": "El mensaje ya está activo"}, status=status.HTTP_200_OK
            )

        mensaje.activo = True
        mensaje.save()

        serializer = MensajeDashboardDetailSerializer(mensaje)

        return Response(
            {
                "message": f'Mensaje "{mensaje.titulo}" activado exitosamente',
                "data": serializer.data,
            }
        )

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def desactivar(self, request, pk=None):
        """POST /api/dashboard/mensajes/{id}/desactivar/"""
        mensaje = self.get_object()

        if not mensaje.activo:
            return Response(
                {"message": "El mensaje ya está desactivado"}, status=status.HTTP_200_OK
            )

        mensaje.activo = False
        mensaje.save()

        serializer = MensajeDashboardDetailSerializer(mensaje)

        return Response(
            {
                "message": f'Mensaje "{mensaje.titulo}" desactivado exitosamente',
                "data": serializer.data,
            }
        )


# VIEWSET PARA ARCHIVOS DEL SISTEMA
# ==============================================================================


class ArchivoSistemaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Archivos del Sistema.

    Endpoints:
    - GET    /api/sistema/archivos/              → Lista todos (Admin)
    - GET    /api/sistema/archivos/{id}/         → Detalle (Admin)
    - POST   /api/sistema/archivos/              → Subir archivo (Admin)
    - PATCH  /api/sistema/archivos/{id}/         → Actualizar (Admin)
    - DELETE /api/sistema/archivos/{id}/         → Eliminar (Admin)
    """

    queryset = ArchivoSistema.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.action == "list":
            return ArchivoSistemaListSerializer
        elif self.action == "retrieve":
            return ArchivoSistemaDetailSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return ArchivoSistemaCreateUpdateSerializer
        return ArchivoSistemaListSerializer

    def list(self, request, *args, **kwargs):
        """GET /api/sistema/archivos/"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )
        return Response({"count": queryset.count(), "results": serializer.data})

    def retrieve(self, request, *args, **kwargs):
        """GET /api/sistema/archivos/{id}/"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={"request": request})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """POST /api/sistema/archivos/"""
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            archivo = serializer.save()
            output_serializer = ArchivoSistemaDetailSerializer(
                archivo, context={"request": request}
            )

            return Response(
                {
                    "message": "Archivo subido exitosamente",
                    "data": output_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        """PATCH /api/sistema/archivos/{id}/"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            archivo = serializer.save()
            output_serializer = ArchivoSistemaDetailSerializer(
                archivo, context={"request": request}
            )

            return Response(
                {
                    "message": "Archivo actualizado exitosamente",
                    "data": output_serializer.data,
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """DELETE /api/sistema/archivos/{id}/"""
        instance = self.get_object()
        nombre = instance.nombre

        # Eliminar archivo físico
        if instance.archivo:
            instance.archivo.delete(save=False)

        instance.delete()

        return Response(
            {"message": f'Archivo "{nombre}" eliminado exitosamente'},
            status=status.HTTP_200_OK,
        )
