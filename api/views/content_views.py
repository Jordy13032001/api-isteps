# api/views/content_views.py

from multiprocessing import context

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import api_view
from api.services.moodle_service import obtener_cursos_publicos

from django.utils import timezone

from content.models import (
    NoticiasPopup,
    Curso,
    CategoriaCurso,
    Interesado,
    Post,
    Etiqueta,
    Autoridad,
    DocumentoTransparencia,
)
from api.serializers.content_serializers import (
    # Noticias Popup
    NoticiasPopupSerializer,
    NoticiasPopupCreateUpdateSerializer,
    # Cursos
    CursoListSerializer,
    CursoDetailSerializer,
    CursoCreateUpdateSerializer,
    CategoriaCursoSerializer,
    # Interesados
    InteresadoSerializer,
    InteresadoCreateSerializer,
    # Etiquetas
    EtiquetaSerializer,
    EtiquetaListSerializer,
    EtiquetaCreateUpdateSerializer,
    # Post
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


# VIEWSET PARA NOTICIAS POPUP


class NoticiasPopupViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para gestionar Noticias Popup.
    """

    queryset = NoticiasPopup.objects.all().order_by("-creado_en")
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return NoticiasPopupCreateUpdateSerializer
        return NoticiasPopupSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "activas"]:
            return [AllowAny()]
        return [IsAdminUser()]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {"count": queryset.count(), "results": serializer.data},
            status=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            output_serializer = NoticiasPopupSerializer(serializer.instance)
            return Response(
                {
                    "message": "Noticia popup creada exitosamente",
                    "data": output_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            output_serializer = NoticiasPopupSerializer(serializer.instance)
            return Response(
                {
                    "message": "Noticia popup actualizada exitosamente",
                    "data": output_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            output_serializer = NoticiasPopupSerializer(serializer.instance)
            return Response(
                {
                    "message": "Noticia popup actualizada parcialmente",
                    "data": output_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        nombre = instance.nombre
        instance.delete()
        return Response(
            {"message": f"Noticia '{nombre}' eliminada exitosamente"},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def activas(self, request):
        hoy = timezone.now().date()
        noticias = NoticiasPopup.objects.filter(
            estado=True, fecha_inicio__lte=hoy, fecha_fin__gte=hoy
        ).order_by("-creado_en")
        serializer = NoticiasPopupSerializer(noticias, many=True)
        return Response(
            {"count": noticias.count(), "results": serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def activar(self, request, pk=None):
        noticia = self.get_object()
        if noticia.estado:
            return Response(
                {"message": "La noticia ya está activa"}, status=status.HTTP_200_OK
            )
        noticia.estado = True
        noticia.save()
        serializer = NoticiasPopupSerializer(noticia)
        return Response(
            {
                "message": f"Noticia '{noticia.nombre}' activada exitosamente",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def desactivar(self, request, pk=None):
        noticia = self.get_object()
        if not noticia.estado:
            return Response(
                {"message": "La noticia ya está desactivada"}, status=status.HTTP_200_OK
            )
        noticia.estado = False
        noticia.save()
        serializer = NoticiasPopupSerializer(noticia)
        return Response(
            {
                "message": f"Noticia '{noticia.nombre}' desactivada exitosamente",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# VIEWSET PARA CURSOS (PROGRAMAS ACADÉMICOS)


class CursoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Cursos/Programas Académicos.

    Endpoints:
    - GET    /api/academico/programas/              → Lista cursos activos
    - GET    /api/academico/programas/{id}/         → Detalle de un curso
    - POST   /api/academico/programas/              → Crear curso (Admin)
    - PUT    /api/academico/programas/{id}/         → Actualizar curso (Admin)
    - PATCH  /api/academico/programas/{id}/         → Actualizar parcial (Admin)
    - DELETE /api/academico/programas/{id}/         → Eliminar curso (Admin)
    - GET    /api/academico/programas/por_coordinacion/  → Agrupados por coordinación
    """

    queryset = Curso.objects.select_related(
        "plataforma", "categoria_curso", "coordinador"
    ).all()

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["titulo", "descripcion", "codigo_externo"]
    ordering_fields = ["titulo", "creado_en", "fecha_inicio", "duracion_horas"]
    ordering = ["-creado_en"]

    def get_serializer_class(self):
        if self.action == "list":
            return CursoListSerializer
        elif self.action == "retrieve":
            return CursoDetailSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return CursoCreateUpdateSerializer
        return CursoListSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "por_coordinacion"]:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Si no es admin, solo mostrar activos
        if not self.request.user.is_staff:
            queryset = queryset.filter(estado="activo")

        # Filtros por query params
        coordinacion = self.request.query_params.get("coordinacion")
        categoria = self.request.query_params.get("categoria")
        nivel = self.request.query_params.get("nivel")
        estado = self.request.query_params.get("estado")
        plataforma = self.request.query_params.get("plataforma")

        if coordinacion:
            queryset = queryset.filter(coordinacion=coordinacion)
        if categoria:
            queryset = queryset.filter(categoria_curso_id=categoria)
        if nivel:
            queryset = queryset.filter(nivel=nivel)
        if estado and self.request.user.is_staff:
            queryset = queryset.filter(estado=estado)
        if plataforma:
            queryset = queryset.filter(plataforma_id=plataforma)

        return queryset

    def list(self, request, *args, **kwargs):
        """GET /api/academico/programas/"""
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"count": queryset.count(), "results": serializer.data})

    def retrieve(self, request, *args, **kwargs):
        """GET /api/academico/programas/{id}/"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """POST /api/academico/programas/"""
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            output_serializer = CursoDetailSerializer(serializer.instance)
            return Response(
                {
                    "message": "Curso creado exitosamente",
                    "data": output_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """PUT /api/academico/programas/{id}/"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            output_serializer = CursoDetailSerializer(serializer.instance)
            return Response(
                {
                    "message": "Curso actualizado exitosamente",
                    "data": output_serializer.data,
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """DELETE /api/academico/programas/{id}/"""
        instance = self.get_object()
        titulo = instance.titulo
        instance.delete()
        return Response(
            {"message": f'Curso "{titulo}" eliminado exitosamente'},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def por_coordinacion(self, request):
        """
        GET /api/academico/programas/por_coordinacion/

        Retorna cursos agrupados por coordinación.
        """
        vicerrectorado = Curso.objects.filter(
            coordinacion=1, estado="activo"
        ).select_related("categoria_curso")

        educacion_continua = Curso.objects.filter(
            coordinacion=2, estado="activo"
        ).select_related("categoria_curso")

        return Response(
            {
                "vicerrectorado": {
                    "id": 1,
                    "nombre": "Vicerrectorado",
                    "descripcion": "Programas de Tercer y Cuarto Nivel",
                    "count": vicerrectorado.count(),
                    "cursos": CursoListSerializer(vicerrectorado, many=True).data,
                },
                "educacion_continua": {
                    "id": 2,
                    "nombre": "Educación Continua",
                    "descripcion": "Cursos y capacitaciones",
                    "count": educacion_continua.count(),
                    "cursos": CursoListSerializer(educacion_continua, many=True).data,
                },
            }
        )


# VIEWSET PARA CATEGORÍAS DE CURSOS
class CategoriaCursoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para categorías de cursos.

    Endpoints:
    - GET /api/academico/categorias/                      → Lista todas
    - GET /api/academico/categorias/{id}/                 → Detalle
    - GET /api/academico/categorias/por_coordinacion/     → Filtradas
    """

    queryset = CategoriaCurso.objects.filter(activo=True).order_by(
        "coordinacion", "nombre"
    )
    serializer_class = CategoriaCursoSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"])
    def por_coordinacion(self, request):
        """
        GET /api/academico/categorias/por_coordinacion/?coordinacion=1
        """
        coordinacion = request.query_params.get("coordinacion")

        if not coordinacion:
            return Response(
                {"error": "Debe especificar el parámetro coordinacion (1 o 2)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            coordinacion = int(coordinacion)
        except ValueError:
            return Response(
                {"error": "El parámetro coordinacion debe ser 1 o 2"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        categorias = self.get_queryset().filter(coordinacion=coordinacion)
        serializer = self.get_serializer(categorias, many=True)

        return Response(
            {
                "coordinacion": coordinacion,
                "coordinacion_nombre": "Vicerrectorado"
                if coordinacion == 1
                else "Educación Continua",
                "count": categorias.count(),
                "categorias": serializer.data,
            }
        )


# VIEWSET PARA INTERESADOS


class InteresadoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Interesados (Leads).

    Endpoints:
    - GET    /api/academico/interesados/           → Lista (Admin)
    - GET    /api/academico/interesados/{id}/      → Detalle (Admin)
    - POST   /api/academico/interesado/            → Registrar interés (Público)
    - PUT    /api/academico/interesados/{id}/      → Actualizar (Admin)
    - DELETE /api/academico/interesados/{id}/      → Eliminar (Admin)
    - POST   /api/academico/interesados/{id}/marcar_atendido/  → Marcar como atendido
    """

    queryset = (
        Interesado.objects.select_related("curso_interes")
        .all()
        .order_by("-fecha_registro")
    )

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombres", "apellidos", "email", "telefono"]
    ordering_fields = ["fecha_registro", "atendido"]
    ordering = ["-fecha_registro"]

    def get_serializer_class(self):
        if self.action == "create":
            return InteresadoCreateSerializer
        return InteresadoSerializer

    def get_permissions(self):
        # Solo el POST de registro es público
        if self.action == "create":
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtros por query params
        atendido = self.request.query_params.get("atendido")
        curso = self.request.query_params.get("curso")

        if atendido is not None:
            atendido_bool = atendido.lower() in ["true", "1", "si", "yes"]
            queryset = queryset.filter(atendido=atendido_bool)
        if curso:
            queryset = queryset.filter(curso_interes_id=curso)

        return queryset

    def list(self, request, *args, **kwargs):
        """GET /api/academico/interesados/ (Admin)"""
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "count": queryset.count(),
                "pendientes": queryset.filter(atendido=False).count(),
                "atendidos": queryset.filter(atendido=True).count(),
                "results": serializer.data,
            }
        )

    def create(self, request, *args, **kwargs):
        """
        POST /api/academico/interesado/

        Registra un nuevo interesado (formulario público).
        """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            interesado = serializer.save()

            return Response(
                {
                    "message": "¡Gracias por tu interés! Nos pondremos en contacto contigo pronto.",
                    "data": {
                        "id": str(interesado.id),
                        "nombre": interesado.get_nombre_completo(),
                        "curso": interesado.curso_interes.titulo,
                        "fecha_registro": interesado.fecha_registro.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """PUT /api/academico/interesados/{id}/ (Admin)"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = InteresadoSerializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Interesado actualizado exitosamente",
                    "data": serializer.data,
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """DELETE /api/academico/interesados/{id}/ (Admin)"""
        instance = self.get_object()
        nombre = instance.get_nombre_completo()
        instance.delete()
        return Response(
            {"message": f'Registro de "{nombre}" eliminado exitosamente'},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def marcar_atendido(self, request, pk=None):
        """
        POST /api/academico/interesados/{id}/marcar_atendido/

        Marca un interesado como atendido.
        """
        interesado = self.get_object()

        if interesado.atendido:
            return Response(
                {"message": "Este interesado ya fue marcado como atendido"},
                status=status.HTTP_200_OK,
            )

        interesado.atendido = True
        interesado.fecha_atencion = timezone.now()

        # Guardar notas si se envían
        notas = request.data.get("notas")
        if notas:
            interesado.notas_seguimiento = notas

        interesado.save()

        serializer = InteresadoSerializer(interesado)
        return Response(
            {
                "message": f'Interesado "{interesado.get_nombre_completo()}" marcado como atendido',
                "data": serializer.data,
            }
        )


# VIEWSET PARA ETIQUETAS


class EtiquetaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Etiquetas de Posts.

    Endpoints:
    - GET    /api/cms/etiquetas/              → Lista todas (público)
    - GET    /api/cms/etiquetas/{id}/         → Detalle (público)
    - POST   /api/cms/etiquetas/              → Crear (Admin)
    - PUT    /api/cms/etiquetas/{id}/         → Actualizar (Admin)
    - PATCH  /api/cms/etiquetas/{id}/         → Actualizar parcial (Admin)
    - DELETE /api/cms/etiquetas/{id}/         → Eliminar (Admin)
    - GET    /api/cms/etiquetas/activas/      → Solo etiquetas activas
    """

    queryset = Etiqueta.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "descripcion"]
    ordering_fields = ["nombre", "creado_en"]
    ordering = ["nombre"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return EtiquetaCreateUpdateSerializer
        return EtiquetaSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "activas"]:
            return [AllowAny()]
        return [IsAdminUser()]

    def list(self, request, *args, **kwargs):
        """GET /api/cms/etiquetas/"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"count": queryset.count(), "results": serializer.data})

    def retrieve(self, request, *args, **kwargs):
        """GET /api/cms/etiquetas/{id}/"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """POST /api/cms/etiquetas/"""
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            etiqueta = serializer.save()
            output_serializer = EtiquetaSerializer(etiqueta)

            return Response(
                {
                    "message": "Etiqueta creada exitosamente",
                    "data": output_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """PUT /api/cms/etiquetas/{id}/"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            etiqueta = serializer.save()
            output_serializer = EtiquetaSerializer(etiqueta)

            return Response(
                {
                    "message": "Etiqueta actualizada exitosamente",
                    "data": output_serializer.data,
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        """PATCH /api/cms/etiquetas/{id}/"""
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """DELETE /api/cms/etiquetas/{id}/"""
        instance = self.get_object()
        nombre = instance.nombre
        instance.delete()

        return Response(
            {"message": f'Etiqueta "{nombre}" eliminada exitosamente'},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def activas(self, request):
        """
        GET /api/cms/etiquetas/activas/

        Retorna solo etiquetas activas.
        """
        etiquetas = self.get_queryset().filter(activo=True)
        serializer = EtiquetaListSerializer(etiquetas, many=True)

        return Response({"count": etiquetas.count(), "results": serializer.data})


# VIEWSET PARA POSTS


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Posts (Noticias, Blogs, Publicaciones).

    Endpoints:
    - GET    /api/cms/posts/                  → Lista posts publicados
    - GET    /api/cms/posts/{id}/             → Detalle de un post
    - POST   /api/cms/posts/                  → Crear post (Admin)
    - PUT    /api/cms/posts/{id}/             → Actualizar post (Admin)
    - PATCH  /api/cms/posts/{id}/             → Actualizar parcial (Admin)
    - DELETE /api/cms/posts/{id}/             → Eliminar post (Admin)
    - GET    /api/cms/posts/destacados/       → Posts destacados
    - GET    /api/cms/posts/por_tipo/         → Posts filtrados por tipo
    - POST   /api/cms/posts/{id}/publicar/    → Publicar borrador (Admin)
    - POST   /api/cms/posts/{id}/archivar/    → Archivar post (Admin)
    """

    queryset = Post.objects.select_related("autor").prefetch_related("etiquetas").all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["titulo", "resumen", "contenido"]
    ordering_fields = ["titulo", "fecha_publicacion", "creado_en"]
    ordering = ["-fecha_publicacion", "-creado_en"]

    # Permitir búsqueda por slug además de id
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        elif self.action == "retrieve":
            return PostDetailSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return PostCreateUpdateSerializer
        return PostListSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "destacados", "por_tipo", "por_slug"]:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Si no es admin, solo mostrar publicados
        if not self.request.user.is_staff:
            queryset = queryset.filter(estado="publicado")

        # Filtros por query params
        tipo = self.request.query_params.get("tipo")
        estado = self.request.query_params.get("estado")
        destacado = self.request.query_params.get("destacado")

        if tipo:
            queryset = queryset.filter(tipo=tipo)
        if estado and self.request.user.is_staff:
            queryset = queryset.filter(estado=estado)
        if destacado is not None:
            destacado_bool = destacado.lower() in ["true", "1", "si", "yes"]
            queryset = queryset.filter(destacado=destacado_bool)

        return queryset

    def list(self, request, *args, **kwargs):
        """GET /api/cms/posts/"""
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )
        return Response({"count": queryset.count(), "results": serializer.data})

    def retrieve(self, request, *args, **kwargs):
        """GET /api/cms/posts/{id}/"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={"request": request})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """POST /api/cms/posts/"""
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Si no se especifica autor, usar el usuario actual
            if not serializer.validated_data.get("autor"):
                serializer.save(autor=request.user)
            else:
                serializer.save()

            output_serializer = PostDetailSerializer(
                serializer.instance, context={"request": request}
            )

            return Response(
                {"message": "Post creado exitosamente", "data": output_serializer.data},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """PUT /api/cms/posts/{id}/"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()

            output_serializer = PostDetailSerializer(
                serializer.instance, context={"request": request}
            )

            return Response(
                {
                    "message": "Post actualizado exitosamente",
                    "data": output_serializer.data,
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """DELETE /api/cms/posts/{id}/"""
        instance = self.get_object()
        titulo = instance.titulo
        instance.delete()
        return Response(
            {"message": f'Post "{titulo}" eliminado exitosamente'},
            status=status.HTTP_200_OK,
        )

    # ACCIONES PERSONALIZADAS

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def destacados(self, request):
        """
        GET /api/cms/posts/destacados/

        Retorna posts destacados (para banner principal).
        """
        posts = (
            self.get_queryset()
            .filter(destacado=True, estado="publicado")
            .order_by("-fecha_publicacion")[:5]
        )

        serializer = PostListSerializer(posts, many=True, context={"request": request})

        return Response({"count": len(serializer.data), "results": serializer.data})

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def por_tipo(self, request):
        """
        GET /api/cms/posts/por_tipo/?tipo=noticia

        Retorna posts filtrados por tipo.
        Tipos válidos: noticia, blog, publicacion
        """
        tipo = request.query_params.get("tipo")

        if not tipo:
            return Response(
                {
                    "error": "Debe especificar el parámetro tipo (noticia, blog, publicacion)"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        tipos_validos = ["noticia", "blog", "publicacion"]
        if tipo not in tipos_validos:
            return Response(
                {
                    "error": f"Tipo inválido. Valores permitidos: {', '.join(tipos_validos)}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        posts = self.get_queryset().filter(tipo=tipo)

        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostListSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = PostListSerializer(posts, many=True, context={"request": request})

        return Response(
            {"tipo": tipo, "count": posts.count(), "results": serializer.data}
        )

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[AllowAny],
        url_path="slug/(?P<slug>[^/.]+)",
    )
    def por_slug(self, request, slug=None):
        """
        GET /api/cms/posts/slug/{slug}/

        Obtiene un post por su slug (URL amigable).
        """
        try:
            post = self.get_queryset().get(slug=slug)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = PostDetailSerializer(post, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def publicar(self, request, pk=None):
        """
        POST /api/cms/posts/{id}/publicar/

        Publica un post en borrador.
        """
        post = self.get_object()

        if post.estado == "publicado":
            return Response(
                {"message": "Este post ya está publicado"}, status=status.HTTP_200_OK
            )

        post.estado = "publicado"
        if not post.fecha_publicacion:
            post.fecha_publicacion = timezone.now()
        post.save()

        serializer = PostDetailSerializer(post, context={"request": request})

        return Response(
            {
                "message": f'Post "{post.titulo}" publicado exitosamente',
                "data": serializer.data,
            }
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def archivar(self, request, pk=None):
        """
        POST /api/cms/posts/{id}/archivar/

        Archiva un post.
        """
        post = self.get_object()

        if post.estado == "archivado":
            return Response(
                {"message": "Este post ya está archivado"}, status=status.HTTP_200_OK
            )

        post.estado = "archivado"
        post.save()

        serializer = PostDetailSerializer(post, context={"request": request})

        return Response(
            {
                "message": f'Post "{post.titulo}" archivado exitosamente',
                "data": serializer.data,
            }
        )


# VIEWSETS PARA INSTITUCIONAL Y TRANSPARENCIA


class AutoridadViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Autoridades del ISTEPS.

    Endpoints:
    - GET    /api/instituto/autoridades/           → Lista autoridades activas
    - GET    /api/instituto/autoridades/{id}/      → Detalle de autoridad
    - POST   /api/instituto/autoridades/           → Crear autoridad (Admin)
    - PUT    /api/instituto/autoridades/{id}/      → Actualizar (Admin)
    - PATCH  /api/instituto/autoridades/{id}/      → Actualizar parcial (Admin)
    - DELETE /api/instituto/autoridades/{id}/      → Eliminar (Admin)
    - GET    /api/instituto/autoridades/por_cargo/ → Agrupar por cargo
    """

    queryset = Autoridad.objects.all().order_by("orden", "apellidos")
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action == "list":
            return AutoridadListSerializer
        elif self.action == "retrieve":
            return AutoridadDetailSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return AutoridadCreateUpdateSerializer
        return AutoridadListSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "por_cargo"]:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Si no es admin, solo mostrar activos
        if not self.request.user.is_staff:
            queryset = queryset.filter(activo=True)

        # Filtros por query params
        cargo = self.request.query_params.get("cargo")
        activo = self.request.query_params.get("activo")

        if cargo:
            queryset = queryset.filter(cargo=cargo)
        if activo is not None and self.request.user.is_staff:
            activo_bool = activo.lower() in ["true", "1", "si", "yes"]
            queryset = queryset.filter(activo=activo_bool)

        return queryset

    def list(self, request, *args, **kwargs):
        """GET /api/instituto/autoridades/"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )

        return Response({"count": queryset.count(), "results": serializer.data})

    def create(self, request, *args, **kwargs):
        """POST /api/instituto/autoridades/"""
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            output_serializer = AutoridadDetailSerializer(
                serializer.instance, context={"request": request}
            )

            return Response(
                {
                    "message": "Autoridad creada exitosamente",
                    "data": output_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """PUT /api/instituto/autoridades/{id}/"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()

            output_serializer = AutoridadDetailSerializer(
                serializer.instance, context={"request": request}
            )

            return Response(
                {
                    "message": "Autoridad actualizada exitosamente",
                    "data": output_serializer.data,
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """DELETE /api/instituto/autoridades/{id}/"""
        instance = self.get_object()
        nombre = instance.get_nombre_completo()
        instance.delete()

        return Response(
            {"message": f'Autoridad "{nombre}" eliminada exitosamente'},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def por_cargo(self, request):
        """
        GET /api/instituto/autoridades/por_cargo/

        Retorna autoridades agrupadas por cargo.
        """
        from collections import OrderedDict

        queryset = self.get_queryset()

        # Orden de cargos según jerarquía
        orden_cargos = [
            "rector",
            "vicerrector",
            "secretario_general",
            "coordinador_academico",
            "director_carrera",
            "coordinador_investigacion",
        ]

        agrupado = OrderedDict()
        for cargo in orden_cargos:
            autoridades = queryset.filter(cargo=cargo)
            if autoridades.exists():
                serializer = AutoridadListSerializer(
                    autoridades, many=True, context={"request": request}
                )
                # Obtener el display name del cargo
                cargo_display = dict(Autoridad.CARGO_CHOICES).get(cargo, cargo)
                agrupado[cargo] = {
                    "cargo_display": cargo_display,
                    "count": autoridades.count(),
                    "autoridades": serializer.data,
                }

        return Response({"total": queryset.count(), "por_cargo": agrupado})


class DocumentoTransparenciaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Documentos de Transparencia.

    Endpoints:
    - GET    /api/transparencia/documentos/              → Lista documentos
    - GET    /api/transparencia/documentos/{id}/         → Detalle documento
    - POST   /api/transparencia/documentos/              → Subir documento (Admin)
    - DELETE /api/transparencia/documentos/{id}/         → Eliminar (Admin)
    - GET    /api/transparencia/documentos/por_categoria/ → Agrupar por categoría
    - GET    /api/transparencia/documentos/categorias/   → Lista de categorías
    """

    queryset = DocumentoTransparencia.objects.select_related("subido_por").all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["titulo", "descripcion"]
    ordering_fields = ["titulo", "fecha_documento", "subido_en"]
    ordering = ["-fecha_documento", "-subido_en"]

    def get_serializer_class(self):
        if self.action == "list":
            return DocumentoTransparenciaListSerializer
        elif self.action == "retrieve":
            return DocumentoTransparenciaDetailSerializer
        elif self.action == "create":
            return DocumentoTransparenciaCreateSerializer
        return DocumentoTransparenciaListSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "por_categoria", "categorias"]:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtros por query params
        categoria = self.request.query_params.get("categoria")
        anio = self.request.query_params.get("anio")

        if categoria:
            queryset = queryset.filter(categoria=categoria)
        if anio:
            queryset = queryset.filter(fecha_documento__year=anio)

        return queryset

    def list(self, request, *args, **kwargs):
        """GET /api/transparencia/documentos/"""
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )

        return Response({"count": queryset.count(), "results": serializer.data})

    def create(self, request, *args, **kwargs):
        """POST /api/transparencia/documentos/"""
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Asignar el usuario que sube el documento
            serializer.save(subido_por=request.user)

            output_serializer = DocumentoTransparenciaDetailSerializer(
                serializer.instance, context={"request": request}
            )

            return Response(
                {
                    "message": "Documento subido exitosamente",
                    "data": output_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """DELETE /api/transparencia/documentos/{id}/"""
        instance = self.get_object()
        titulo = instance.titulo

        # Eliminar el archivo físico también
        if instance.archivo:
            instance.archivo.delete(save=False)

        instance.delete()

        return Response(
            {"message": f'Documento "{titulo}" eliminado exitosamente'},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def por_categoria(self, request):
        """
        GET /api/transparencia/documentos/por_categoria/

        Retorna documentos agrupados por categoría.
        """
        from collections import OrderedDict

        queryset = self.get_queryset()

        # Orden de categorías
        orden_categorias = [
            "normativa",
            "reglamentos",
            "resoluciones",
            "actas",
            "presupuesto",
            "informes",
            "convenios",
        ]

        agrupado = OrderedDict()
        for categoria in orden_categorias:
            documentos = queryset.filter(categoria=categoria)
            if documentos.exists():
                serializer = DocumentoTransparenciaListSerializer(
                    documentos, many=True, context={"request": request}
                )
                categoria_display = dict(DocumentoTransparencia.CATEGORIA_CHOICES).get(
                    categoria, categoria
                )
                agrupado[categoria] = {
                    "categoria_display": categoria_display,
                    "count": documentos.count(),
                    "documentos": serializer.data,
                }

        return Response({"total": queryset.count(), "por_categoria": agrupado})

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def categorias(self, request):
        """
        GET /api/transparencia/documentos/categorias/

        Lista las categorías disponibles con conteo de documentos.
        """
        from django.db.models import Count

        categorias = (
            DocumentoTransparencia.objects.values("categoria")
            .annotate(total=Count("id"))
            .order_by("categoria")
        )

        resultado = []
        for cat in categorias:
            categoria_display = dict(DocumentoTransparencia.CATEGORIA_CHOICES).get(
                cat["categoria"], cat["categoria"]
            )
            resultado.append(
                {
                    "categoria": cat["categoria"],
                    "categoria_display": categoria_display,
                    "total_documentos": cat["total"],
                }
            )

        return Response({"count": len(resultado), "categorias": resultado})

@api_view(["GET"])
def cursos_moodle(request):
    data = obtener_cursos_publicos()

    # 🚨 Si hay error en el service
    if isinstance(data, dict) and data.get("error"):
        return Response(data, status=400)

    return Response(
        {
            "count": len(data),
            "results": data
        },
        status=200
    )
