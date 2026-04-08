from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.http import HttpResponse
import os

def check_media_files(request):
    try:
        import glob
        files = glob.glob(os.path.join(settings.MEDIA_ROOT, '**/*'), recursive=True)
        return HttpResponse("<br>".join(files))
    except Exception as e:
        return HttpResponse(str(e))

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("api/", include("api.urls")),
    path("oauth/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    path('media-debug/', check_media_files),
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]

# 🔥 MEDIA en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)