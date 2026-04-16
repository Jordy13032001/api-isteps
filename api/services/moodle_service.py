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

        cursos = []

        for curso in data:
            if curso.get("visible") != 1:
                continue

            if curso.get("id") == 1:
                continue

            cursos.append({
                "id": curso.get("id"),
                "titulo": curso.get("fullname"),
                "descripcion": curso.get("summary"),
                "fecha": curso.get("startdate"),
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