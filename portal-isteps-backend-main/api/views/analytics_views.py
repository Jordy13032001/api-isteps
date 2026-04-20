from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta, datetime

from analytics.models import (
    EventoNavegacion,
    PaginaVisitada,
    Busqueda,
    Reporte,
    ConfiguracionReporte,
    Exportacion,
)
from system_app.models import LogAuditoria

from api.serializers.analytics_serializers import (
    EventoNavegacionCreateSerializer,
    DashboardMetricasSerializer,
    DashboardFiltrosSerializer,
    LogAuditoriaSerializer,
    LogAuditoriaListSerializer,
    LogAuditoriaFiltrosSerializer,
    ReporteSerializer,
    ReporteListSerializer,
    ReporteGenerarSerializer,
    ExportacionSerializer,
    ExportacionCreateSerializer,
)

# EVENTOS DE NAVEGACIÓN


class RegistrarEventoAPIView(APIView):
    """
    POST /api/analitica/eventos

    Registra eventos de usuario (clicks, pageviews, scroll, etc).
    Permite analytics de comportamiento del usuario.
    """

    permission_classes = [permissions.AllowAny]  # Puede ser anónimo

    def post(self, request):
        serializer = EventoNavegacionCreateSerializer(data=request.data)

        if serializer.is_valid():
            # Guardar el evento
            evento = serializer.save()

            # Retornar confirmación
            return Response(
                {
                    "message": "Evento registrado exitosamente",
                    "evento_id": str(evento.id),
                    "timestamp": evento.timestamp,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# DASHBOARD DE MÉTRICAS


class DashboardMetricasAPIView(APIView):
    """
    GET /api/analitica/dashboard

    Obtiene métricas gráficas agregadas para el dashboard de analytics.
    Acepta filtros opcionales por fecha y plataforma.
    """

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get(self, request):
        # Validar filtros
        filtros_serializer = DashboardFiltrosSerializer(data=request.query_params)

        if not filtros_serializer.is_valid():
            return Response(
                filtros_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        filtros = filtros_serializer.validated_data

        # Establecer rango de fechas (por defecto últimos 30 días)
        fecha_fin = filtros.get("fecha_fin", timezone.now().date())
        fecha_inicio = filtros.get("fecha_inicio", fecha_fin - timedelta(days=30))

        # Convertir a datetime para queries
        fecha_inicio_dt = datetime.combine(fecha_inicio, datetime.min.time())
        fecha_fin_dt = datetime.combine(fecha_fin, datetime.max.time())

        # Construir query base
        eventos_query = EventoNavegacion.objects.filter(
            timestamp__gte=fecha_inicio_dt, timestamp__lte=fecha_fin_dt
        )

        paginas_query = PaginaVisitada.objects.filter(
            timestamp__gte=fecha_inicio_dt, timestamp__lte=fecha_fin_dt
        )

        busquedas_query = Busqueda.objects.filter(
            timestamp__gte=fecha_inicio_dt, timestamp__lte=fecha_fin_dt
        )

        # Aplicar filtro de plataforma si existe
        plataforma_id = filtros.get("plataforma_id")
        if plataforma_id:
            eventos_query = eventos_query.filter(plataforma_id=plataforma_id)
            paginas_query = paginas_query.filter(plataforma_id=plataforma_id)
            busquedas_query = busquedas_query.filter(plataforma_id=plataforma_id)

        # MÉTRICAS GENERALES
        hoy = timezone.now().date()
        inicio_semana = hoy - timedelta(days=7)

        total_visitas_hoy = paginas_query.filter(timestamp__date=hoy).count()

        total_visitas_semana = paginas_query.filter(
            timestamp__date__gte=inicio_semana
        ).count()

        total_visitas_mes = paginas_query.count()

        # USUARIOS
        usuarios_activos_hoy = (
            paginas_query.filter(timestamp__date=hoy)
            .values("usuario")
            .distinct()
            .count()
        )

        usuarios_nuevos_semana = (
            paginas_query.filter(timestamp__date__gte=inicio_semana)
            .exclude(usuario__isnull=True)
            .values("usuario")
            .distinct()
            .count()
        )

        # PÁGINAS MÁS VISITADAS
        paginas_top = (
            paginas_query.values("url", "titulo_pagina")
            .annotate(visitas=Count("id"))
            .order_by("-visitas")[:10]
        )

        paginas_top_list = [
            {
                "url": p["url"],
                "titulo": p["titulo_pagina"] or "Sin título",
                "visitas": p["visitas"],
            }
            for p in paginas_top
        ]

        # BÚSQUEDAS MÁS FRECUENTES
        busquedas_top = (
            busquedas_query.values("termino_busqueda")
            .annotate(cantidad=Count("id"))
            .order_by("-cantidad")[:10]
        )

        busquedas_top_list = [
            {"termino": b["termino_busqueda"], "cantidad": b["cantidad"]}
            for b in busquedas_top
        ]

        # DISTRIBUCIÓN POR PLATAFORMA
        visitas_por_plataforma = (
            paginas_query.exclude(plataforma__isnull=True)
            .values("plataforma__nombre")
            .annotate(visitas=Count("id"))
            .order_by("-visitas")
        )

        visitas_por_plataforma_list = [
            {"plataforma": v["plataforma__nombre"], "visitas": v["visitas"]}
            for v in visitas_por_plataforma
        ]

        # EVENTOS POR TIPO
        eventos_por_tipo = (
            eventos_query.values("tipo_evento")
            .annotate(cantidad=Count("id"))
            .order_by("-cantidad")
        )

        eventos_por_tipo_list = [
            {"tipo": e["tipo_evento"], "cantidad": e["cantidad"]}
            for e in eventos_por_tipo
        ]

        # Preparar datos de respuesta
        datos_dashboard = {
            "total_visitas_hoy": total_visitas_hoy,
            "total_visitas_semana": total_visitas_semana,
            "total_visitas_mes": total_visitas_mes,
            "usuarios_activos_hoy": usuarios_activos_hoy,
            "usuarios_nuevos_semana": usuarios_nuevos_semana,
            "paginas_top": paginas_top_list,
            "busquedas_top": busquedas_top_list,
            "visitas_por_plataforma": visitas_por_plataforma_list,
            "eventos_por_tipo": eventos_por_tipo_list,
            "periodo_inicio": fecha_inicio,
            "periodo_fin": fecha_fin,
            "generado_en": timezone.now(),
        }

        serializer = DashboardMetricasSerializer(datos_dashboard)
        return Response(serializer.data, status=status.HTTP_200_OK)


# LOGS DE AUDITORÍA


class StandardResultsSetPagination(PageNumberPagination):
    """Paginación estándar para listados"""

    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200


class LogsAuditoriaAPIView(generics.ListAPIView):
    """
    GET /api/seguridad/logs

    Historial de acciones administrativas.
    Acepta filtros por usuario, acción, entidad, nivel y fechas.
    Retorna resultados paginados.
    """

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    serializer_class = LogAuditoriaListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = LogAuditoria.objects.select_related("usuario").all()

        # Obtener parámetros de filtro
        filtros_serializer = LogAuditoriaFiltrosSerializer(
            data=self.request.query_params
        )

        if filtros_serializer.is_valid():
            filtros = filtros_serializer.validated_data

            # Filtrar por usuario
            usuario_id = filtros.get("usuario_id")
            if usuario_id:
                queryset = queryset.filter(usuario_id=usuario_id)

            # Filtrar por acción
            accion = filtros.get("accion")
            if accion:
                queryset = queryset.filter(accion__icontains=accion)

            # Filtrar por entidad
            entidad_tipo = filtros.get("entidad_tipo")
            if entidad_tipo:
                queryset = queryset.filter(entidad_tipo__icontains=entidad_tipo)

            # Filtrar por nivel
            nivel = filtros.get("nivel")
            if nivel:
                queryset = queryset.filter(nivel=nivel)

            # Filtrar por rango de fechas
            fecha_inicio = filtros.get("fecha_inicio")
            fecha_fin = filtros.get("fecha_fin")

            if fecha_inicio:
                queryset = queryset.filter(timestamp__gte=fecha_inicio)
            if fecha_fin:
                queryset = queryset.filter(timestamp__lte=fecha_fin)

        return queryset

    def list(self, request, *args, **kwargs):
        """Override para agregar información adicional en la respuesta"""
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LogAuditoriaDetalleAPIView(generics.RetrieveAPIView):
    """
    GET /api/seguridad/logs/{id}/

    Obtiene detalles completos de un log específico.
    """

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    serializer_class = LogAuditoriaSerializer
    queryset = LogAuditoria.objects.select_related("usuario").all()
    lookup_field = "id"


# REPORTES


class GenerarReporteAPIView(APIView):
    """
    POST /api/reports/generador

    Solicita la generación de un nuevo reporte.
    El reporte se genera de forma asíncrona.
    """

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def post(self, request):
        serializer = ReporteGenerarSerializer(data=request.data)

        if serializer.is_valid():
            datos = serializer.validated_data

            # Obtener o crear configuración si se proporcionó
            configuracion = None
            if datos.get("configuracion_id"):
                try:
                    configuracion = ConfiguracionReporte.objects.get(
                        id=datos["configuracion_id"]
                    )
                except ConfiguracionReporte.DoesNotExist:
                    return Response(
                        {"error": "Configuración de reporte no encontrada"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            # Crear el registro del reporte
            reporte = Reporte.objects.create(
                configuracion=configuracion,
                nombre=datos["nombre"],
                periodo_inicio=datos["periodo_inicio"],
                periodo_fin=datos["periodo_fin"],
                estado="generando",
                solicitado_por=request.user,
            )

            # TODO: Aquí se debería disparar una tarea asíncrona (Celery)
            # para generar el reporte en background
            # Por ahora solo creamos el registro

            return Response(
                {
                    "message": "Reporte solicitado exitosamente",
                    "reporte_id": str(reporte.id),
                    "estado": reporte.estado,
                    "nombre": reporte.nombre,
                    "generado_en": reporte.generado_en,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportesHistoriaAPIView(generics.ListAPIView):
    """
    GET /api/reportes/historia

    Lista todos los reportes generados, con opción de filtrar por estado.
    Retorna resultados paginados.
    """

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    serializer_class = ReporteListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Reporte.objects.select_related(
            "configuracion", "solicitado_por"
        ).all()

        # Filtros opcionales
        estado = self.request.query_params.get("estado")
        if estado:
            queryset = queryset.filter(estado=estado)

        fecha_inicio = self.request.query_params.get("fecha_desde")
        if fecha_inicio:
            try:
                fecha_dt = datetime.fromisoformat(fecha_inicio)
                queryset = queryset.filter(generado_en__gte=fecha_dt)
            except (ValueError, TypeError):
                pass

        # Solo mostrar reportes del usuario si no es superusuario
        if not self.request.user.is_superuser:
            queryset = queryset.filter(solicitado_por=self.request.user)

        return queryset


class ReporteDetalleAPIView(generics.RetrieveAPIView):
    """
    GET /api/reportes/{id}/

    Obtiene detalles completos de un reporte específico.
    """

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    serializer_class = ReporteSerializer
    queryset = Reporte.objects.select_related("configuracion", "solicitado_por").all()
    lookup_field = "id"

    def get_queryset(self):
        queryset = super().get_queryset()

        # Usuarios no-superusuario solo pueden ver sus propios reportes
        if not self.request.user.is_superuser:
            queryset = queryset.filter(solicitado_por=self.request.user)

        return queryset


# EXPORTACIONES DE REPORTES


class ExportarReporteAPIView(APIView):
    """
    POST /api/reportes/{id}/exportar/

    Solicita la exportación de un reporte en el formato especificado.
    """

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def post(self, request, id):
        # Validar que el reporte existe
        try:
            reporte = Reporte.objects.select_related(
                "configuracion", "solicitado_por"
            ).get(id=id)
        except Reporte.DoesNotExist:
            return Response(
                {"error": "Reporte no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

        # Verificar permisos
        if not request.user.is_superuser:
            if reporte.solicitado_por != request.user:
                return Response(
                    {"error": "No tiene permisos para exportar este reporte"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        # Validar datos
        serializer = ExportacionCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        formato = serializer.validated_data["formato"]

        # Verificar estado del reporte
        if reporte.estado != "completado":
            return Response(
                {
                    "error": "El reporte debe estar completado para ser exportado",
                    "estado_actual": reporte.estado,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generar archivo (simulado por ahora)
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"{reporte.nombre}_{timestamp}.{formato}"
        ruta_descarga = f"/exports/reportes/{reporte.id}/{nombre_archivo}"
        tamano_bytes = 1024 * 512  # 512 KB simulados

        # Crear registro de exportación
        exportacion = Exportacion.objects.create(
            reporte=reporte,
            usuario=request.user,
            formato=formato,
            ruta_descarga=ruta_descarga,
            tamano_bytes=tamano_bytes,
        )

        return Response(
            {
                "message": f"Reporte exportado exitosamente a {formato.upper()}",
                "exportacion": {
                    "id": str(exportacion.id),
                    "formato": exportacion.get_formato_display(),
                    "ruta_descarga": exportacion.ruta_descarga,
                    "tamano": exportacion.get_tamano_legible(),
                    "exportado_en": exportacion.exportado_en,
                },
                "reporte": {
                    "id": str(reporte.id),
                    "nombre": reporte.nombre,
                    "periodo": f"{reporte.periodo_inicio} a {reporte.periodo_fin}",
                },
            },
            status=status.HTTP_201_CREATED,
        )


class ExportacionesReporteAPIView(generics.ListAPIView):
    """
    GET /api/reportes/{id}/exportaciones/

    Lista todas las exportaciones de un reporte específico.
    """

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    serializer_class = ExportacionSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        reporte_id = self.kwargs.get("id")

        try:
            reporte = Reporte.objects.get(id=reporte_id)
        except Reporte.DoesNotExist:
            return Exportacion.objects.none()

        if not self.request.user.is_superuser:
            if reporte.solicitado_por != self.request.user:
                return Exportacion.objects.none()

        queryset = (
            Exportacion.objects.filter(reporte=reporte)
            .select_related("usuario", "reporte")
            .order_by("-exportado_en")
        )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            reporte_id = self.kwargs.get("id")
            try:
                Reporte.objects.get(id=reporte_id)
                return Response(
                    {
                        "count": 0,
                        "message": "Este reporte no tiene exportaciones aún",
                        "results": [],
                    },
                    status=status.HTTP_200_OK,
                )
            except Reporte.DoesNotExist:
                return Response(
                    {"error": "Reporte no encontrado"}, status=status.HTTP_404_NOT_FOUND
                )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"count": queryset.count(), "results": serializer.data})


class MisExportacionesAPIView(generics.ListAPIView):
    """
    GET /api/usuario/exportaciones/

    Lista todas las exportaciones del usuario actual.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ExportacionSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = (
            Exportacion.objects.filter(usuario=self.request.user)
            .select_related("reporte", "usuario")
            .order_by("-exportado_en")
        )

        # Filtros opcionales
        formato = self.request.query_params.get("formato")
        if formato:
            queryset = queryset.filter(formato=formato)

        fecha_desde = self.request.query_params.get("fecha_desde")
        if fecha_desde:
            try:
                fecha_dt = datetime.fromisoformat(fecha_desde)
                queryset = queryset.filter(exportado_en__gte=fecha_dt)
            except (ValueError, TypeError):
                pass

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        stats = {
            "total_exportaciones": queryset.count(),
            "por_formato": {
                "pdf": queryset.filter(formato="pdf").count(),
                "xlsx": queryset.filter(formato="xlsx").count(),
                "csv": queryset.filter(formato="csv").count(),
            },
        }

        return Response(
            {
                "count": queryset.count(),
                "estadisticas": stats,
                "results": serializer.data,
            }
        )
