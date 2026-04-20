# api/serializers/__init__.py

from .auth_serializers import (
    UsuarioSerializer,
    UsuarioPerfilSerializer,
    UsuarioActualizarSerializer,
    LoginSerializer,
    TokenSerializer,
    ChangePasswordSerializer,
    PreferenciasSerializer,
)

from .content_serializers import (
    # Noticias Popup
    NoticiasPopupSerializer,
    NoticiasPopupCreateUpdateSerializer,
    # Cursos
    CategoriaCursoSerializer,
    CursoListSerializer,
    CursoDetailSerializer,
    CursoCreateUpdateSerializer,
    # Interesados
    InteresadoSerializer,
    InteresadoCreateSerializer,
    # Posts - CMS
    PostListSerializer,
    PostDetailSerializer,
    PostCreateUpdateSerializer,
    # Autoridades
    AutoridadListSerializer,
    AutoridadDetailSerializer,
    AutoridadCreateUpdateSerializer,
    # Documentos Transparencia
    DocumentoTransparenciaListSerializer,
    DocumentoTransparenciaDetailSerializer,
    DocumentoTransparenciaCreateSerializer,
)

from .system_serializers import (
    ConfiguracionSistemaSerializer,
    TemaColoresConfigSerializer,
    TemaColoresInputSerializer,
    MensajeDashboardListSerializer,
    MensajeDashboardDetailSerializer,
    MensajeUsuarioSerializer,
    MensajeDashboardCreateSerializer,
    MensajeDashboardUpdateSerializer,
    MensajeDashboardFiltrosSerializer,
)

from .analytics_serializers import (
    # Eventos
    EventoNavegacionSerializer,
    EventoNavegacionCreateSerializer,
    # Dashboard
    DashboardMetricasSerializer,
    DashboardFiltrosSerializer,
    # Logs Auditoría
    LogAuditoriaSerializer,
    LogAuditoriaListSerializer,
    LogAuditoriaFiltrosSerializer,
    # Reportes
    ReporteSerializer,
    ReporteListSerializer,
    ReporteGenerarSerializer,
    ConfiguracionReporteSerializer,
    # Métricas
    MetricaAgregadaSerializer,
    # Exportaciones
    ExportacionSerializer,
    ExportacionCreateSerializer,
)

__all__ = [
    # Auth
    "UsuarioSerializer",
    "UsuarioPerfilSerializer",
    "UsuarioActualizarSerializer",
    "LoginSerializer",
    "TokenSerializer",
    "ChangePasswordSerializer",
    "PreferenciasSerializer",
    # Content - Noticias
    "NoticiasPopupSerializer",
    "NoticiasPopupCreateUpdateSerializer",
    # Content - Cursos
    "CategoriaCursoSerializer",
    "CursoListSerializer",
    "CursoDetailSerializer",
    "CursoCreateUpdateSerializer",
    # Content - Interesados
    "InteresadoSerializer",
    "InteresadoCreateSerializer",
    # Content - Posts CMS
    "PostListSerializer",
    "PostDetailSerializer",
    "PostCreateUpdateSerializer",
    # Content - Autoridades
    "AutoridadListSerializer",
    "AutoridadDetailSerializer",
    "AutoridadCreateUpdateSerializer",
    # Content - Documentos Transparencia
    "DocumentoTransparenciaListSerializer",
    "DocumentoTransparenciaDetailSerializer",
    "DocumentoTransparenciaCreateSerializer",
    # System
    "ConfiguracionSistemaSerializer",
    "TemaColoresConfigSerializer",
    "TemaColoresInputSerializer",
    "MensajeDashboardListSerializer",
    "MensajeDashboardDetailSerializer",
    "MensajeUsuarioSerializer",
    "MensajeDashboardCreateSerializer",
    "MensajeDashboardUpdateSerializer",
    "MensajeDashboardFiltrosSerializer",
    # Analytics - Eventos
    "EventoNavegacionSerializer",
    "EventoNavegacionCreateSerializer",
    # Analytics - Dashboard
    "DashboardMetricasSerializer",
    "DashboardFiltrosSerializer",
    # Analytics - Logs Auditoría
    "LogAuditoriaSerializer",
    "LogAuditoriaListSerializer",
    "LogAuditoriaFiltrosSerializer",
    # Analytics - Reportes
    "ReporteSerializer",
    "ReporteListSerializer",
    "ReporteGenerarSerializer",
    "ConfiguracionReporteSerializer",
    # Analytics - Métricas
    "MetricaAgregadaSerializer",
    # Analytics - Exportaciones
    "ExportacionSerializer",
    "ExportacionCreateSerializer",
]
