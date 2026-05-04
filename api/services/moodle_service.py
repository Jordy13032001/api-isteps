import os
import requests

MOODLE_URL = os.getenv("MOODLE_API_URL")
MOODLE_TOKEN = os.getenv("MOODLE_API_TOKEN")


def obtener_cursos_publicos():
    # 🚨 Validar variables de entorno
    if not MOODLE_URL or not MOODLE_TOKEN:
        return {
            "error": "Faltan variables de entorno MOODLE_URL o MOODLE_TOKEN"
        }

    params = {
        "wstoken": MOODLE_TOKEN,
        "wsfunction": "core_course_get_courses",
        "moodlewsrestformat": "json",
    }

    try:
        response = requests.get(MOODLE_URL, params=params, timeout=10)

        # 🔥 Debug útil
        if response.status_code != 200:
            return {
                "error": "Error HTTP",
                "status": response.status_code,
                "detalle": response.text
            }

        try:
            data = response.json()
        except Exception:
            return {
                "error": "Respuesta no es JSON",
                "detalle": response.text
            }

        # 🚨 Moodle devolvió error
        if isinstance(data, dict) and data.get("exception"):
            return {
                "error": "Error Moodle",
                "detalle": data
            }

        from content.models import Curso
        destacados_ids = set(Curso.objects.filter(destacado=True, tipo='moodle').values_list('codigo_externo', flat=True))

        from django.core.cache import cache
        from concurrent.futures import ThreadPoolExecutor

        def fetch_moodle_count(m_id):
            cache_key = f"moodle_enrolled_count_{m_id}"
            cached_count = cache.get(cache_key)
            if cached_count is not None:
                return m_id, cached_count
            
            # Si no está en caché, consultar a Moodle
            try:
                params_count = {
                    "wstoken": MOODLE_TOKEN,
                    "wsfunction": "core_enrol_get_enrolled_users",
                    "moodlewsrestformat": "json",
                    "courseid": m_id,
                }
                res = requests.get(MOODLE_URL, params=params_count, timeout=5)
                m_data = res.json()
                if isinstance(m_data, list):
                    # Solo contar estudiantes
                    count = sum(1 for u in m_data if u.get("roles") and any(r["shortname"] == "student" for r in u["roles"]))
                else:
                    count = 0
                
                cache.set(cache_key, count, timeout=3600) # 1 hora de caché
                return m_id, count
            except:
                return m_id, 0

        # Obtener todos los cursos tipo 'moodle' de Django para mapear inscritos_count (manual override)
        moodle_django_data = {
            str(c.codigo_externo): c.inscritos_count 
            for c in Curso.objects.filter(tipo='moodle')
        }

        # Filtrar solo cursos válidos para consulta
        cursos_validos = [c for c in data if c.get("visible") == 1 and c.get("id") != 1]
        
        # Consultar conteos en paralelo (máximo 10 hilos para no saturar)
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(fetch_moodle_count, [c.get("id") for c in cursos_validos]))
        
        moodle_counts = dict(results)

        cursos = []
        for curso in cursos_validos:
            moodle_id = str(curso.get("id"))
            
            # Prioridad: 1. Manual en Django (si es > 0) | 2. Moodle Real | 3. Cero
            db_count = moodle_django_data.get(moodle_id, 0)
            final_count = db_count if db_count > 0 else moodle_counts.get(curso.get("id"), 0)

            cursos.append({
                "id": curso.get("id"),
                "titulo": curso.get("fullname"),
                "descripcion": curso.get("summary"),
                "fecha": curso.get("startdate"),
                "destacado": moodle_id in destacados_ids,
                "inscritos_count": final_count
            })

        return cursos

    except requests.exceptions.RequestException as e:
        return {
            "error": "Error de conexión",
            "detalle": str(e)
        }

def obtener_estudiantes_curso(course_id):
    if not MOODLE_URL or not MOODLE_TOKEN:
        return []

    params = {
        "wstoken": MOODLE_TOKEN,
        "wsfunction": "core_enrol_get_enrolled_users",
        "moodlewsrestformat": "json",
        "courseid": course_id,
    }

    try:
        response = requests.get(MOODLE_URL, params=params, timeout=10)
        data = response.json()

        if isinstance(data, dict) and data.get("exception"):
            return []

        estudiantes = [
            {
                "nombre": u.get("fullname"),
                "foto": u.get("profileimageurl"),
            }
            for u in data
            if u.get("roles") and any(r["shortname"] == "student" for r in u["roles"])
        ]

        return estudiantes

    except Exception:
        return []