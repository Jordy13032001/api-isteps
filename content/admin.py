from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from .models import (
    Curso,
    RecursoAcademico,
    AccesoRecurso,
    NoticiasPopup,
    CategoriaCurso,
    Interesado,
    Autoridad,
    Post,
    DocumentoTransparencia,
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
# ADMIN PARA CURSO CON FILTRO DINÁMICO
# ============================================
@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ["titulo", "tipo", "coordinacion", "categoria_curso", "plataforma", "costo_total", "cuotas", "destacado", "estado"]
    list_filter = ["tipo", "destacado", "coordinacion", "categoria_curso", "plataforma", "estado", "nivel", "modalidad"]
    search_fields = ["titulo", "codigo_externo"]
    ordering = ["-creado_en"]
    fieldsets = ( 
        (
            "Información Básica",
            {
                "fields": (
                    "plataforma",
                    "codigo_externo",
                    "titulo",
                    "tipo",
                    "descripcion",
                    "imagen_url",
                )
            },
        ),
        ("Clasificación", {"fields": ("coordinacion", "categoria_curso", "nivel", "titulo_obtenido")}),
        (
            "Detalles Académicos y Duración",
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
            "Contenido y Documentación",
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

    def get_urls(self):
        """Agrega URL personalizada para obtener categorías por AJAX"""
        urls = super().get_urls()
        custom_urls = [
            path(
                "ajax/categorias/<int:coordinacion_id>/",
                self.admin_site.admin_view(self.get_categorias_ajax),
                name="curso_get_categorias",
            ),
        ]
        return custom_urls + urls

    def get_categorias_ajax(self, request, coordinacion_id):
        """Endpoint AJAX que retorna categorías filtradas por coordinación"""
        categorias = CategoriaCurso.objects.filter(
            coordinacion=coordinacion_id, activo=True
        ).values("id", "nombre")

        return JsonResponse(list(categorias), safe=False) 