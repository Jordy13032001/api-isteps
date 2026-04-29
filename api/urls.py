from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from api.views.content_views import estudiantes_curso

from api.views.content_views import cursos_moodle

from api.views import (
    # Auth views
    LogoutAPIView,
    PerfilUsuarioAPIView,
    ActualizarPerfilAPIView,
    CambiarPasswordAPIView,
    PreferenciasUsuarioAPIView,
    VerificarTokenAPIView,
    ObtenerTokenDesdeSesionAPIView,
    usuario_info,
    health_check,
    verificar_autenticacion,
    # Content views
    NoticiasPopupViewSet,
    CursoViewSet,
    CategoriaCursoViewSet,
    InteresadoViewSet,
    EtiquetaViewSet,
    PostViewSet,
    AutoridadViewSet,
    DocumentoTransparenciaViewSet,
    ImagenCarruselViewSet,
    BotonSoporteViewSet,
    # System views
    TemaColoresAPIView,
    MensajeDashboardViewSet,
    ArchivoSistemaViewSet,
    # Analytics views
    RegistrarEventoAPIView,
    DashboardMetricasAPIView,
    LogsAuditoriaAPIView,
    LogAuditoriaDetalleAPIView,
    GenerarReporteAPIView,
    ReportesHistoriaAPIView,
    ReporteDetalleAPIView,
    ExportarReporteAPIView,
    ExportacionesReporteAPIView,
    MisExportacionesAPIView,
)

app_name = "api"

# Router para ViewSets
router = DefaultRouter()
router.register(r"config/emergencia", NoticiasPopupViewSet, basename="noticias-popup")
router.register(r"academico/programas", CursoViewSet, basename="cursos")
router.register(r"academico/categorias", CategoriaCursoViewSet, basename="categorias")
router.register(r"academico/interesados", InteresadoViewSet, basename="interesados")

router.register(r"cms/etiquetas", EtiquetaViewSet, basename="etiquetas")
router.register(r"cms/posts", PostViewSet, basename="posts")
router.register(r"instituto/autoridades", AutoridadViewSet, basename="autoridades")
router.register(
    r"transparencia/documentos", DocumentoTransparenciaViewSet, basename="documentos"
)
router.register(
    r"cms/carruseles", ImagenCarruselViewSet, basename="carruseles"
)
router.register(r"cms/botones-soporte", BotonSoporteViewSet, basename="botones-soporte")
router.register(
    r"dashboard/mensajes", MensajeDashboardViewSet, basename="mensajes-dashboard"
)
router.register(r"sistema/archivos", ArchivoSistemaViewSet, basename="archivos-sistema")


urlpatterns = [
    # Health check
    path("health/", health_check, name="health-check"),
    # AUTENTICACIÓN (solo con Microsoft 365)
    path(
        "auth/social-token/",
        ObtenerTokenDesdeSesionAPIView.as_view(),
        name="social-token",
    ),
    path(
        "auth/verificar-autenticacion/",
        verificar_autenticacion,
        name="verificar-autenticacion",
    ),
    path("auth/logout/", LogoutAPIView.as_view(), name="logout"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path(
        "auth/verificar-token/", VerificarTokenAPIView.as_view(), name="verificar-token"
    ),
    # USUARIO - Perfil
    path("usuario/perfil/", PerfilUsuarioAPIView.as_view(), name="perfil"),
    path(
        "usuario/perfil/actualizar/",
        ActualizarPerfilAPIView.as_view(),
        name="perfil-actualizar",
    ),
    path("usuario/info/", usuario_info, name="usuario-info"),
    path(
        "usuario/cambiar-password/",
        CambiarPasswordAPIView.as_view(),
        name="cambiar-password",
    ),
    # USUARIO - Preferencias
    path(
        "usuario/preferencias/",
        PreferenciasUsuarioAPIView.as_view(),
        name="preferencias",
    ),
    # USUARIO - Mis Exportaciones
    path(
        "usuario/exportaciones/",
        MisExportacionesAPIView.as_view(),
        name="usuario-exportaciones",
    ),
    # CONFIGURACIÓN GLOBAL
    # Tema/Colores - GET, PUT, PATCH
    path(
        "config/tema/",
        TemaColoresAPIView.as_view(),
        name="tema-colores",
    ),
    # ANALYTICS - Eventos y Dashboard
    path(
        "analitica/eventos/",
        RegistrarEventoAPIView.as_view(),
        name="analytics-eventos",
    ),
    path(
        "analitica/dashboard/",
        DashboardMetricasAPIView.as_view(),
        name="analytics-dashboard",
    ),
    # SEGURIDAD - Logs de Auditoría
    path(
        "seguridad/logs/",
        LogsAuditoriaAPIView.as_view(),
        name="auditoria-logs",
    ),
    path(
        "seguridad/logs/<uuid:id>/",
        LogAuditoriaDetalleAPIView.as_view(),
        name="auditoria-log-detalle",
    ),
    # REPORTES - Generación y Listado
    path(
        "reports/generador/",
        GenerarReporteAPIView.as_view(),
        name="reportes-generar",
    ),
    path(
        "reportes/historia/",
        ReportesHistoriaAPIView.as_view(),
        name="reportes-historia",
    ),
    path(
        "reportes/<uuid:id>/",
        ReporteDetalleAPIView.as_view(),
        name="reportes-detalle",
    ),
    # REPORTES - Exportaciones
    path(
        "reportes/<uuid:id>/exportar/",
        ExportarReporteAPIView.as_view(),
        name="reportes-exportar",
    ),
    path(
        "reportes/<uuid:id>/exportaciones/",
        ExportacionesReporteAPIView.as_view(),
        name="reportes-exportaciones",
    ),
    # ACADÉMICO - Ruta especial para POST interesado (singular)
    path(
        "academico/interesado/",
        InteresadoViewSet.as_view({"post": "create"}),
        name="registrar-interesado",
    ),
    # ROUTER (VIEWSETS)
    path("", include(router.urls)),
    path("academico/moodle-cursos/", cursos_moodle),
    path('moodle/curso/<int:course_id>/estudiantes/', estudiantes_curso),

]

