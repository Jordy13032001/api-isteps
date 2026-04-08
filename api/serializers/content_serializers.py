# api/serializers/content_serializers.py

from rest_framework import serializers
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


# SERIALIZERS PARA NOTICIAS POPUP


class NoticiasPopupSerializer(serializers.ModelSerializer):
    """
    Serializer para vista pública de noticias popup
    """

    imagen_url = serializers.SerializerMethodField()
    debe_mostrarse = serializers.SerializerMethodField()
    esta_vigente = serializers.SerializerMethodField()

    class Meta:
        model = NoticiasPopup
        fields = [
            "id",
            "nombre",
            "descripcion",
            "imagen_url",
            "fecha_inicio",
            "fecha_fin",
            "estado",
            "enlace_url",
            "enlace_texto",
            "debe_mostrarse",
            "esta_vigente",
            "creado_en",
            "actualizado_en",
        ]
        read_only_fields = [
            "id",
            "imagen_url",
            "debe_mostrarse",
            "esta_vigente",
            "creado_en",
            "actualizado_en",
        ]

    def get_imagen_url(self, obj):
        if obj.imagen:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.imagen.url)
            return obj.imagen.url
        return None

    def get_debe_mostrarse(self, obj):
        return obj.debe_mostrarse()

    def get_esta_vigente(self, obj):
        return obj.esta_vigente()


class NoticiasPopupCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear y actualizar noticias popup (Panel Admin)
    """

    class Meta:
        model = NoticiasPopup
        fields = [
            "id",
            "nombre",
            "descripcion",
            "imagen",
            "fecha_inicio",
            "fecha_fin",
            "estado",
            "enlace_url",
            "enlace_texto",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        fecha_inicio = attrs.get("fecha_inicio")
        fecha_fin = attrs.get("fecha_fin")

        if self.instance:
            fecha_inicio = fecha_inicio or self.instance.fecha_inicio
            fecha_fin = fecha_fin or self.instance.fecha_fin

        if fecha_inicio and fecha_fin:
            if fecha_fin < fecha_inicio:
                raise serializers.ValidationError(
                    {
                        "fecha_fin": "La fecha de fin debe ser posterior o igual a la fecha de inicio"
                    }
                )

        return attrs

    def validate_nombre(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError(
                "El nombre de la noticia no puede estar vacío"
            )
        return value.strip()


# SERIALIZERS PARA CATEGORÍA CURSO


class CategoriaCursoSerializer(serializers.ModelSerializer):
    """
    Serializer para categorías de cursos.
    """

    coordinacion_display = serializers.CharField(
        source="get_coordinacion_display", read_only=True
    )

    class Meta:
        model = CategoriaCurso
        fields = [
            "id",
            "nombre",
            "coordinacion",
            "coordinacion_display",
            "descripcion",
            "activo",
        ]
        read_only_fields = ["id"]


# SERIALIZERS PARA CURSO


class CursoListSerializer(serializers.ModelSerializer):
    """
    Serializer para listado de cursos (GET lista).
    Solo muestra: id, titulo, descripcion
    """

    class Meta:
        model = Curso
        fields = [
            "id",
            "titulo",
            "descripcion",
        ]
        read_only_fields = fields


class CursoDetailSerializer(serializers.ModelSerializer):
    """
    Serializer para detalle de un curso (GET por ID).
    Información completa incluyendo todos los campos y relaciones.
    """

    plataforma_nombre = serializers.CharField(
        source="plataforma.nombre", read_only=True
    )
    coordinacion_display = serializers.CharField(
        source="get_coordinacion_display", read_only=True
    )
    categoria_curso_detail = CategoriaCursoSerializer(
        source="categoria_curso", read_only=True
    )
    nivel_display = serializers.CharField(source="get_nivel_display", read_only=True)
    jornada_display = serializers.CharField(
        source="get_jornada_display", read_only=True
    )
    modalidad_display = serializers.CharField(
        source="get_modalidad_display", read_only=True
    )
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    coordinador_info = serializers.SerializerMethodField()
    malla_curricular_url = serializers.SerializerMethodField()

    class Meta:
        model = Curso
        fields = [
            "id",
            "codigo_externo",
            "titulo",
            "descripcion",
            "imagen_url",
            "plataforma",
            "plataforma_nombre",
            "coordinacion",
            "coordinacion_display",
            "categoria_curso",
            "categoria_curso_detail",
            "nivel",
            "nivel_display",
            "duracion_horas",
            "fecha_inicio",
            "fecha_fin",
            "fecha_inicio_publicidad",
            "fecha_fin_publicidad",
            "titulo_obtenido",
            "jornada",
            "jornada_display",
            "modalidad",
            "modalidad_display",
            "costo_matricula",
            "costo_total",
            "cuotas",
            "resolucion",
            "presentacion",
            "perfil_profesional",
            "malla_curricular",
            "malla_curricular_url",
            "coordinador",
            "coordinador_info",
            "estado",
            "estado_display",
            "creado_en",
            "actualizado_en",
        ]

    def get_coordinador_info(self, obj):
        if obj.coordinador:
            return {
                "id": str(obj.coordinador.id),
                "nombre": obj.coordinador.nombre,
                "apellido": obj.coordinador.apellido,
                "cargo": obj.coordinador.cargo,
                "email": obj.coordinador.email,
            }
        return None

    def get_malla_curricular_url(self, obj):
        if obj.malla_curricular:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.malla_curricular.url)
            return obj.malla_curricular.url
        return None


class CursoCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear y actualizar cursos (POST/PUT/PATCH).
    Incluye todos los campos nuevos.
    """

    class Meta:
        model = Curso
        fields = [
            "id",
            "plataforma",
            "codigo_externo",
            "titulo",
            "descripcion",
            "coordinacion",
            "categoria_curso",
            "nivel",
            "duracion_horas",
            "imagen_url",
            "fecha_inicio",
            "fecha_fin",
            "fecha_inicio_publicidad",
            "fecha_fin_publicidad",
            "titulo_obtenido",
            "jornada",
            "modalidad",
            "costo_matricula",
            "costo_total",
            "cuotas",
            "resolucion",
            "presentacion",
            "perfil_profesional",
            "malla_curricular",
            "coordinador",
            "estado",
        ]
        read_only_fields = ["id"]

    def validate_titulo(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("El título no puede estar vacío")
        return value.strip()

    def validate_duracion_horas(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("La duración debe ser un número positivo")
        return value

    def validate_costo_matricula(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("El costo de matrícula debe ser positivo")
        return value

    def validate_costo_total(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("El costo total debe ser positivo")
        return value

    def validate_cuotas(self, value):
        if value is not None and value < 1:
            raise serializers.ValidationError("El número de cuotas debe ser al menos 1")
        return value

    def validate(self, attrs):
        # Validar fechas del curso
        fecha_inicio = attrs.get("fecha_inicio")
        fecha_fin = attrs.get("fecha_fin")

        if self.instance:
            fecha_inicio = fecha_inicio or self.instance.fecha_inicio
            fecha_fin = fecha_fin or self.instance.fecha_fin

        if fecha_inicio and fecha_fin:
            if fecha_fin < fecha_inicio:
                raise serializers.ValidationError(
                    {
                        "fecha_fin": "La fecha de fin debe ser posterior a la fecha de inicio"
                    }
                )

        # Validar fechas de publicidad
        fecha_inicio_pub = attrs.get("fecha_inicio_publicidad")
        fecha_fin_pub = attrs.get("fecha_fin_publicidad")

        if self.instance:
            fecha_inicio_pub = fecha_inicio_pub or self.instance.fecha_inicio_publicidad
            fecha_fin_pub = fecha_fin_pub or self.instance.fecha_fin_publicidad

        if fecha_inicio_pub and fecha_fin_pub:
            if fecha_fin_pub < fecha_inicio_pub:
                raise serializers.ValidationError(
                    {
                        "fecha_fin_publicidad": "La fecha fin de publicidad debe ser posterior a la fecha de inicio"
                    }
                )

        # Validar coordinación y categoría
        coordinacion = attrs.get("coordinacion")
        categoria_curso = attrs.get("categoria_curso")

        if self.instance:
            coordinacion = (
                coordinacion if coordinacion is not None else self.instance.coordinacion
            )
            categoria_curso = (
                categoria_curso
                if categoria_curso is not None
                else self.instance.categoria_curso
            )

        if coordinacion and categoria_curso:
            if categoria_curso.coordinacion != coordinacion:
                raise serializers.ValidationError(
                    {
                        "categoria_curso": f"Esta categoría pertenece a {categoria_curso.get_coordinacion_display()}, "
                        f"no a la coordinación seleccionada."
                    }
                )

        # Validar costos (matrícula no puede ser mayor que el total)
        costo_matricula = attrs.get("costo_matricula")
        costo_total = attrs.get("costo_total")

        if self.instance:
            costo_matricula = (
                costo_matricula
                if costo_matricula is not None
                else self.instance.costo_matricula
            )
            costo_total = (
                costo_total if costo_total is not None else self.instance.costo_total
            )

        if costo_matricula and costo_total:
            if costo_matricula > costo_total:
                raise serializers.ValidationError(
                    {
                        "costo_matricula": "El costo de matrícula no puede ser mayor al costo total"
                    }
                )

        return attrs


# SERIALIZERS PARA INTERESADO


class InteresadoSerializer(serializers.ModelSerializer):
    """
    Serializer para lectura de interesados (Admin).
    """

    curso_titulo = serializers.CharField(source="curso_interes.titulo", read_only=True)
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Interesado
        fields = [
            "id",
            "nombres",
            "apellidos",
            "nombre_completo",
            "email",
            "telefono",
            "curso_interes",
            "curso_titulo",
            "mensaje",
            "acepta_terminos",
            "fecha_registro",
            "atendido",
            "fecha_atencion",
            "notas_seguimiento",
        ]

    def get_nombre_completo(self, obj):
        return obj.get_nombre_completo()


class InteresadoCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear un interesado (formulario público de landing).
    """

    class Meta:
        model = Interesado
        fields = [
            "id",
            "nombres",
            "apellidos",
            "email",
            "telefono",
            "curso_interes",
            "mensaje",
            "acepta_terminos",
        ]
        read_only_fields = ["id"]

    def validate_nombres(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre es requerido")
        return value.strip()

    def validate_apellidos(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("El apellido es requerido")
        return value.strip()

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("El email es requerido")
        return value.lower().strip()

    def validate_telefono(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("El teléfono es requerido")
        cleaned = "".join(c for c in value if c.isdigit() or c == "+")
        if len(cleaned) < 7:
            raise serializers.ValidationError(
                "El teléfono debe tener al menos 7 dígitos"
            )
        return cleaned

    def validate_curso_interes(self, value):
        if not value:
            raise serializers.ValidationError("Debe seleccionar un programa de interés")
        if value.estado != "activo":
            raise serializers.ValidationError(
                "El programa seleccionado no está disponible"
            )
        return value

    def validate_acepta_terminos(self, value):
        """Valida que los términos y condiciones sean aceptados"""
        if not value:
            raise serializers.ValidationError(
                "Debe aceptar los términos y condiciones para continuar"
            )
        return value


# SERIALIZERS PARA ETIQUETAS


class EtiquetaSerializer(serializers.ModelSerializer):
    """
    Serializer para lectura de etiquetas.
    """

    class Meta:
        model = Etiqueta
        fields = [
            "id",
            "nombre",
            "descripcion",
            "activo",
            "creado_en",
            "actualizado_en",
        ]
        read_only_fields = fields


class EtiquetaListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listas (solo lo esencial).
    """

    class Meta:
        model = Etiqueta
        fields = [
            "id",
            "nombre",
        ]
        read_only_fields = fields


class EtiquetaCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear y actualizar etiquetas (Admin).
    """

    class Meta:
        model = Etiqueta
        fields = [
            "id",
            "nombre",
            "descripcion",
            "activo",
        ]
        read_only_fields = ["id"]

    def validate_nombre(self, value):
        """Validar que el nombre no esté vacío y sea único"""
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre de la etiqueta es requerido")

        value = value.strip()

        # Verificar unicidad (excepto si es actualización del mismo registro)
        etiqueta_existente = Etiqueta.objects.filter(nombre__iexact=value)
        if self.instance:
            etiqueta_existente = etiqueta_existente.exclude(id=self.instance.id)

        if etiqueta_existente.exists():
            raise serializers.ValidationError("Ya existe una etiqueta con este nombre")

        return value


# SERIALIZERS PARA POSTS


class PostListSerializer(serializers.ModelSerializer):
    """
    Serializer para listado de posts (GET lista).
    Información resumida para tarjetas/cards.
    """

    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    autor_nombre = serializers.SerializerMethodField()
    imagen_url = serializers.SerializerMethodField()
    etiquetas_info = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "titulo",
            "slug",
            "resumen",
            "tipo",
            "tipo_display",
            "imagen_url",
            "autor",
            "autor_nombre",
            "estado",
            "estado_display",
            "destacado",
            "fecha_publicacion",
            "etiquetas_info",
        ]

    def get_autor_nombre(self, obj):
        if obj.autor:
            return obj.autor.get_nombre_completo()
        return None

    def get_imagen_url(self, obj):
        if obj.imagen_portada:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.imagen_portada.url)
            return obj.imagen_portada.url
        return None

    def get_etiquetas_info(self, obj):
        """Retorna lista simplificada de etiquetas"""
        return [
            {"id": str(etiq.id), "nombre": etiq.nombre}
            for etiq in obj.etiquetas.filter(activo=True)
        ]


class PostDetailSerializer(serializers.ModelSerializer):
    """
    Serializer para detalle de un post (GET por ID o slug).
    Información completa.
    """

    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    autor_nombre = serializers.SerializerMethodField()
    imagen_url = serializers.SerializerMethodField()
    etiquetas_detalle = EtiquetaSerializer(
        source="etiquetas", many=True, read_only=True
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "titulo",
            "slug",
            "resumen",
            "contenido",
            "tipo",
            "tipo_display",
            "imagen_portada",
            "imagen_url",
            "autor",
            "autor_nombre",
            "estado",
            "estado_display",
            "destacado",
            "fecha_publicacion",
            "meta_descripcion",
            "etiquetas_detalle",
            "creado_en",
            "actualizado_en",
        ]

    def get_autor_nombre(self, obj):
        if obj.autor:
            return obj.autor.get_nombre_completo()
        return None

    def get_imagen_url(self, obj):
        if obj.imagen_portada:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.imagen_portada.url)
            return obj.imagen_portada.url
        return None


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear y actualizar posts (POST/PUT/PATCH).
    """

    etiquetas = serializers.SlugRelatedField(
        slug_field="nombre",
        queryset=Etiqueta.objects.filter(activo=True),
        many=True,
        required=False,
        help_text="Nombres de las etiquetas (ej: ['Tecnología', 'Educación'])",
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "titulo",
            "slug",
            "resumen",
            "contenido",
            "tipo",
            "imagen_portada",
            "autor",
            "estado",
            "destacado",
            "fecha_publicacion",
            "meta_descripcion",
            "etiquetas",
        ]
        read_only_fields = ["id"]

    def validate_titulo(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("El título no puede estar vacío")
        return value.strip()

    def validate_resumen(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("El resumen no puede estar vacío")
        if len(value) > 500:
            raise serializers.ValidationError(
                "El resumen no puede exceder 500 caracteres"
            )
        return value.strip()

    def validate_contenido(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("El contenido no puede estar vacío")
        return value.strip()

    def validate_slug(self, value):
        """
        Validar que el slug sea único (excepto para el mismo objeto en actualización)
        """
        if value:
            queryset = Post.objects.filter(slug=value)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError("Ya existe un post con este slug")
        return value

    def validate(self, attrs):
        """
        Si el estado es 'publicado' y no hay fecha_publicacion, asignar fecha actual
        """
        estado = attrs.get("estado")
        fecha_publicacion = attrs.get("fecha_publicacion")

        if estado == "publicado" and not fecha_publicacion:
            from django.utils import timezone

            attrs["fecha_publicacion"] = timezone.now()

        return attrs

    def to_representation(self, instance):
        """
        Personalizar la respuesta para mostrar etiquetas completas
        """
        representation = super().to_representation(instance)
        representation["etiquetas"] = [
            {"id": str(etiq.id), "nombre": etiq.nombre}
            for etiq in instance.etiquetas.filter(activo=True)
        ]
        return representation


# SERIALIZERS PARA AUTORIDADES


class AutoridadListSerializer(serializers.ModelSerializer):
    """
    Serializer para listado de autoridades.
    Información resumida para la sección "Somos ISTEPS".
    """

    cargo_display = serializers.CharField(source="get_cargo_display", read_only=True)
    nombre_completo = serializers.SerializerMethodField()
    foto_url = serializers.SerializerMethodField()

    class Meta:
        model = Autoridad
        fields = [
            "id",
            "nombres",
            "apellidos",
            "titulo_autoridad",
            "nombre_completo",
            "cargo",
            "cargo_display",
            "email",
            "foto_url",
            "orden",
            "activo",
        ]

def get_nombre_completo(self, obj):
    return obj.get_nombre_completo()

def get_foto_url(self, obj):
    if obj.fotografia:
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.fotografia.url)
        return obj.fotografia.url
    return None


class AutoridadDetailSerializer(serializers.ModelSerializer):
    """
    Serializer para detalle completo de una autoridad.
    """

    cargo_display = serializers.CharField(source="get_cargo_display", read_only=True)
    nombre_completo = serializers.SerializerMethodField()
    foto_url = serializers.SerializerMethodField()

    class Meta:
        model = Autoridad
        fields = [
            "id",
            "nombres",
            "apellidos",
            "titulo_autoridad",
            "nombre_completo",
            "cargo",
            "cargo_display",
            "email",
            "fotografia",
            "foto_url",
            "biografia",
            "orden",
            "activo",
            "fecha_inicio",
            "fecha_fin",
            "creado_en",
            "actualizado_en",
        ]

    def get_nombre_completo(self, obj):
        return obj.get_nombre_completo()

    def get_foto_url(self, obj):
        if obj.fotografia:
            url = obj.fotografia.url
            if url.startswith('http'):
                return url
            
            if not url.startswith('/media/'):
                path = url if url.startswith('/') else f'/{url}'
                url = f'/media{path}'
            
            return f"https://web-production-4abfb.up.railway.app{url}"
        return None


class AutoridadCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear y actualizar autoridades.
    """

    class Meta:
        model = Autoridad
        fields = [
            "id",
            "nombres",
            "apellidos",
            "titulo_autoridad",
            "cargo",
            "email",
            "fotografia",
            "biografia",
            "orden",
            "activo",
            "fecha_inicio",
            "fecha_fin",
        ]
        read_only_fields = ["id"]

    def validate_nombres(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Los nombres no pueden estar vacíos")
        return value.strip()

    def validate_apellidos(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Los apellidos no pueden estar vacíos")
        return value.strip()

    def validate_email(self, value):
        if value:
            return value.lower().strip()
        return value

    def validate(self, attrs):
        """
        Validar que fecha_fin sea posterior a fecha_inicio si existe
        """
        fecha_inicio = attrs.get("fecha_inicio")
        fecha_fin = attrs.get("fecha_fin")

        if self.instance:
            fecha_inicio = fecha_inicio or self.instance.fecha_inicio
            fecha_fin = fecha_fin if "fecha_fin" in attrs else self.instance.fecha_fin

        if fecha_inicio and fecha_fin:
            if fecha_fin < fecha_inicio:
                raise serializers.ValidationError(
                    {
                        "fecha_fin": "La fecha de fin debe ser posterior a la fecha de inicio"
                    }
                )

        return attrs


# SERIALIZERS PARA DOCUMENTOS TRANSPARENCIA


class DocumentoTransparenciaListSerializer(serializers.ModelSerializer):
    """
    Serializer para listado de documentos de transparencia.
    """

    categoria_display = serializers.CharField(
        source="get_categoria_display", read_only=True
    )
    subcategoria_display = serializers.CharField(
        source="get_subcategoria_display", read_only=True
    )
    archivo_url = serializers.SerializerMethodField()
    tamano_legible = serializers.SerializerMethodField()

    class Meta:
        model = DocumentoTransparencia
        fields = [
            "id",
            "titulo",
            "descripcion",
            "categoria",
            "categoria_display",
            "subcategoria",
            "subcategoria_display",
            "archivo_url",
            "archivo_nombre",
            "tamano_legible",
            "fecha_documento",
            "subido_en",
        ]

    def get_archivo_url(self, obj):
        if obj.archivo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.archivo.url)
            return obj.archivo.url
        return None

    def get_tamano_legible(self, obj):
        return obj.get_tamano_legible()


class DocumentoTransparenciaDetailSerializer(serializers.ModelSerializer):
    """
    Serializer para detalle completo de un documento.
    """

    categoria_display = serializers.CharField(
        source="get_categoria_display", read_only=True
    )
    subcategoria_display = serializers.CharField(
        source="get_subcategoria_display", read_only=True
    )
    archivo_url = serializers.SerializerMethodField()
    tamano_legible = serializers.SerializerMethodField()
    subido_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = DocumentoTransparencia
        fields = [
            "id",
            "titulo",
            "descripcion",
            "categoria",
            "categoria_display",
            "subcategoria",
            "subcategoria_display",
            "archivo",
            "archivo_url",
            "archivo_nombre",
            "archivo_tamano_bytes",
            "tamano_legible",
            "fecha_documento",
            "subido_por",
            "subido_por_nombre",
            "subido_en",
            "actualizado_en",
        ]

    def get_archivo_url(self, obj):
        if obj.archivo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.archivo.url)
            return obj.archivo.url
        return None

    def get_tamano_legible(self, obj):
        return obj.get_tamano_legible()

    def get_subido_por_nombre(self, obj):
        if obj.subido_por:
            return obj.subido_por.get_nombre_completo()
        return None


class DocumentoTransparenciaCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para subir nuevos documentos de transparencia.
    """

    class Meta:
        model = DocumentoTransparencia
        fields = [
            "id",
            "titulo",
            "descripcion",
            "categoria",
            "subcategoria",
            "archivo",
            "fecha_documento",
        ]
        read_only_fields = ["id"]

    def validate_titulo(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("El título no puede estar vacío")
        return value.strip()

    def validate_archivo(self, value):
        if value:
            # Validar que sea PDF
            if not value.name.lower().endswith(".pdf"):
                raise serializers.ValidationError("Solo se permiten archivos PDF")
            # Validar tamaño máximo (10 MB)
            max_size = 10 * 1024 * 1024
            if value.size > max_size:
                raise serializers.ValidationError("El archivo no puede superar 10 MB")
        return value
