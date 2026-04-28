from django.contrib import admin
from django import forms
from django.urls import path
from django.http import JsonResponse
from .models import (
    Curso,
    Carrera,
    CursoMoodle,
    RecursoAcademico,
    AccesoRecurso,
    NoticiasPopup,
    CategoriaCurso,
    Interesado,
    Autoridad,
    Post,
    DocumentoTransparencia,
    ImagenCarrusel,
    BotonSoporte,
)

admin.site.register(RecursoAcademico)
admin.site.register(AccesoRecurso)
admin.site.register(NoticiasPopup)
admin.site.register(Interesado)
admin.site.register(Autoridad)
admin.site.register(Post)
admin.site.register(DocumentoTransparencia)


@admin.register(CategoriaCurso)
class CategoriaCursoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "coordinacion", "activo", "creado_en"]
    list_filter = ["coordinacion", "activo"]
    search_fields = ["nombre"]
    ordering = ["coordinacion", "nombre"]


# ============================================
# ADMIN PARA CARRERA (Proxy de Curso)
# ============================================
class CarreraForm(forms.ModelForm):
    class Meta:
        model = Carrera
        exclude = ["tipo", "codigo_externo", "plataforma"]

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.tipo = "carrera"
        
        # Autogenerar un cÃÂ³digo externo dummy para cumplir con el modelo
        if not instance.codigo_externo:
            import uuid
            instance.codigo_externo = f"carrera-{uuid.uuid4().hex[:8]}"
            
        # Asignar la primera plataforma disponible (normalmente la del instituto)
        if not getattr(instance, 'plataforma_id', None):
            from integration.models import Plataforma
            plat = Plataforma.objects.first()
            instance.plataforma = plat
            
        if commit:
            instance.save()
        return instance

@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    form = CarreraForm
    list_display = ["titulo", "coordinacion", "categoria_curso", "costo_total", "cuotas", "destacado", "estado"]
    list_filter = ["destacado", "coordinacion", "categoria_curso", "estado", "nivel", "modalidad"]
    search_fields = ["titulo"]
    ordering = ["-creado_en"]
    
    fieldsets = ( 
        (
            "InformaciÃÂ³n BÃÂ¡sica",
            {
                "fields": (
                    "titulo",
                    "descripcion",
                    "imagen_url",
                )
            },
        ),
        ("ClasificaciÃÂ³n", {"fields": ("coordinacion", "categoria_curso", "nivel", "titulo_obtenido")}),
        (
            "Detalles AcadÃÂ©micos y DuraciÃÂ³n",
            {
                "fields": (
                    "duracion_valor",
                    "unidad_duracion",
                    "modalidad",
                    "jornada",
                    "clases",
                    "horario",
                    "coordinador",
                )
            },
        ),
        (
            "Costos y Financiamiento",
            {
                "fields": (
                    "costo_matricula",
                    "costo_total",
                    "cuotas",
                )
            },
        ),
        (
            "Fechas y Publicidad",
            {
                "fields": (
                    "fecha_inicio",
                    "fecha_fin",
                    "fecha_inicio_publicidad",
                    "fecha_fin_publicidad",
                    "destacado",
                    "estado",
                )
            },
        ),
        (
            "Contenido y DocumentaciÃÂ³n",
            {
                "classes": ("collapse",),
                "fields": (
                    "resolucion",
                    "presentacion",
                    "perfil_profesional",
                    "malla_curricular",
                )
            },
        ),
    )

    class Media:
        js = ("admin/js/filtro_categoria_curso.js",)

    def get_queryset(self, request):
        """Filtra para mostrar solo las carreras"""
        return super().get_queryset(request).filter(tipo="carrera")

    def get_urls(self):
        """Agrega URL personalizada para obtener categorÃÂ­as por AJAX"""
        urls = super().get_urls()
        custom_urls = [
            path(
                "ajax/categorias/<int:coordinacion_id>/",
                self.admin_site.admin_view(self.get_categorias_ajax),
                name="carrera_get_categorias",
            ),
        ]
        return custom_urls + urls

    def get_categorias_ajax(self, request, coordinacion_id):
        """Endpoint AJAX que retorna categorÃÂ­as filtradas por coordinaciÃÂ³n"""
        categorias = CategoriaCurso.objects.filter(
            coordinacion=coordinacion_id, activo=True
        ).values("id", "nombre")

        return JsonResponse(list(categorias), safe=False)


# ============================================
# ADMIN PARA CURSO MOODLE (Proxy de Curso)
# ============================================
class CursoMoodleForm(forms.ModelForm):
    class Meta:
        model = CursoMoodle
        fields = ["codigo_externo", "destacado", "estado"]
        labels = {
            "codigo_externo": "ID Curso Moodle",
        }
        help_texts = {
            "codigo_externo": "ID numÃÂ©rico del curso en la plataforma Moodle",
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.tipo = "moodle"
        
        # Generar tÃÂ­tulo por defecto si no existe
        if not instance.titulo:
            instance.titulo = f"Curso Moodle Destacado #{instance.codigo_externo}"
            
        # Asignar plataforma por defecto si no existe
        if not getattr(instance, 'plataforma_id', None):
            from integration.models import Plataforma
            plat = Plataforma.objects.filter(nombre__icontains='moodle').first()
            if not plat:
                plat = Plataforma.objects.first()
            instance.plataforma = plat
            
        if commit:
            instance.save()
        return instance


@admin.register(CursoMoodle)
class CursoMoodleAdmin(admin.ModelAdmin):
    form = CursoMoodleForm
    list_display = ["titulo", "codigo_externo", "plataforma", "destacado", "estado"]
    list_filter = ["destacado", "estado"]
    search_fields = ["codigo_externo", "titulo"]
    ordering = ["-creado_en"]

    fieldsets = (
        (
            "Vincular con Moodle",
            {
                "fields": (
                    "codigo_externo",
                ),
                "description": "Ingrese ÃÂºnicamente el ID del curso para vincularlo con Moodle.",
            },
        ),
        (
            "Visibilidad en la Web",
            {
                "fields": (
                    "destacado",
                    "estado",
                )
            },
        ),
    )

    def get_queryset(self, request):
        """Filtra para mostrar solo los cursos de moodle"""
        return super().get_queryset(request).filter(tipo="moodle")
@admin.register(ImagenCarrusel)
class ImagenCarruselAdmin(admin.ModelAdmin):
    list_display = ["seccion", "titulo_o_id", "url_destino_preview", "orden", "activo", "creado_en"]
    list_filter = ["seccion", "activo"]
    search_fields = ["titulo", "seccion"]
    ordering = ["seccion", "orden"]
    
    def titulo_o_id(self, obj):
        return obj.titulo if obj.titulo else f"Imagen #{str(obj.id)[:8]}"
    titulo_o_id.short_description = "TÃ­tulo"
    
    def url_destino_preview(self, obj):
        if obj.url_destino:
            return f"{obj.url_destino[:30]}..." if len(obj.url_destino) > 30 else obj.url_destino
        return "-"
    url_destino_preview.short_description = "Enlace de RedirecciÃ³n"

@admin.register(BotonSoporte)
class BotonSoporteAdmin(admin.ModelAdmin):
    list_display = ["nombre", "enlace_url", "activo"]
    
    # Prevenir que se agreguen más botones
    def has_add_permission(self, request):
        return False
        
    # Prevenir que se eliminen los botones existentes
    def has_delete_permission(self, request, obj=None):
        return False
        
    exclude = ["plataforma"]

    def get_readonly_fields(self, request, obj=None):
        # Que el nombre y el icono no se puedan cambiar, solo la URL y si está activo
        if obj:
            return ["nombre", "icono", "orden"]
        return []
