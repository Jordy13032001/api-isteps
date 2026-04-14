import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal_isteps.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from content.models import Curso, CategoriaCurso
from integration.models import Plataforma
import uuid

User = get_user_model()
User.objects.filter(username='testadmin').delete()
admin = User.objects.create_superuser('testadmin', 'test@test.com', 'testpwd')

# Create necessary foreign keys for Curso
plataforma, _ = Plataforma.objects.get_or_create(nombre='Moodle', url_base='https://moodle.test')
categoria, _ = CategoriaCurso.objects.get_or_create(nombre='Gastronomía', coordinacion=2)

c = Client(SERVER_NAME='localhost')
c.force_login(admin)

data = {
    "plataforma": str(plataforma.id),
    "codigo_externo": "CURSO-TST-1",
    "titulo": "Curso de Prueba Post Fix",
    "descripcion": "Descripción del curso de prueba",
    "coordinacion": 2,
    "categoria_curso": str(categoria.id),
    "nivel": "basico",
    "duracion_valor": 40,
    "unidad_duracion": "horas",
    "estado": "activo"
}

try:
    print("Enviando POST para crear curso...")
    response = c.post('/api/academico/programas/', data, content_type='application/json')
    print("Status code:", response.status_code)
    try:
        print("Response JSON:", response.json())
    except:
        print("Response content:", response.content.decode('utf-8')[:500])
except Exception as e:
    import traceback
    traceback.print_exc()

# Eliminar el curso creado
Curso.objects.filter(codigo_externo="CURSO-TST-1").delete()
