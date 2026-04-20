from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("api/", include("api.urls")),
    path("oauth/", include("oauth2_provider.urls", namespace="oauth2_provider")),
]

# AÑADIDO: Obliga a Django a mostrar las imágenes de la carpeta /media/ en producción
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]