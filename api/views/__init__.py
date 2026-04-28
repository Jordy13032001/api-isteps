# api/views/__init__.py

from .auth_views import (
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
)

from .content_views import (
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
)

from .system_views import (
    TemaColoresAPIView,
    MensajeDashboardViewSet,
    ArchivoSistemaViewSet,
)

from .analytics_views import (
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

__all__ = [
    # Auth views
    "LogoutAPIView",
    "PerfilUsuarioAPIView",
    "ActualizarPerfilAPIView",
    "CambiarPasswordAPIView",
    "PreferenciasUsuarioAPIView",
    "VerificarTokenAPIView",
    "ObtenerTokenDesdeSesionAPIView",
    "usuario_info",
    "health_check",
    "verificar_autenticacion",
    # Content views
    "NoticiasPopupViewSet",
    "CursoViewSet",
    "CategoriaCursoViewSet",
    "InteresadoViewSet",
    "EtiquetaViewSet",
    "PostViewSet",
    "AutoridadViewSet",
    "DocumentoTransparenciaViewSet",
    "ImagenCarruselViewSet",
    "BotonSoporteViewSet",
    # System views
    "TemaColoresAPIView",
    "MensajeDashboardViewSet",
    "ArchivoSistemaViewSet",
    # Analytics views
    "RegistrarEventoAPIView",
    "DashboardMetricasAPIView",
    "LogsAuditoriaAPIView",
    "LogAuditoriaDetalleAPIView",
    "GenerarReporteAPIView",
    "ReportesHistoriaAPIView",
    "ReporteDetalleAPIView",
    "ExportarReporteAPIView",
    "ExportacionesReporteAPIView",
    "MisExportacionesAPIView",
]