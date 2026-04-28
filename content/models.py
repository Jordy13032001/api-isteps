import uuid
from django.db import models


class Curso(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único del curso",
    )

    plataforma = models.ForeignKey(
        "integration.Plataforma",
        on_delete=models.CASCADE,
        help_text="Plataforma a la que pertenece el curso",
    )

    codigo_externo = models.CharField(
        max_length=100,
        help_text="ID del curso en la plataforma externa (ej:ID en Moodle)",
    )

    titulo = models.CharField(
        max_length=200,
        help_text="Titulo del curso",
    )

    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripcion del curso",
    )

    COORDINACION_CHOICES = [
        (1, "Vicerrectorado"),
        (2, "Educación Continua"),
    ]

    coordinacion = models.IntegerField(
        choices=COORDINACION_CHOICES,
        null=True,
        blank=True,
        help_text="1=Vicerrectorado, 2=Educación Continua",
    )

    categoria_curso = models.ForeignKey(
        "CategoriaCurso",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cursos",
        help_text="Categoría según la coordinación elegida",
    )

    NIVEL_CHOICES = [
        ("basico", "Básico"),
        ("intermedio", "Intermedio"),
        ("avanzado", "Avanzado"),
    ]

    nivel = models.CharField(
        max_length=50,
        choices=NIVEL_CHOICES,
        blank=True,
        null=True,
        help_text="Nivel de dificultad del curso",
    )

    duracion_valor = models.IntegerField(
        blank=True,
        null=True,
        help_text="Cantidad numérica de la duración",
    )
    
    UNIDAD_DURACION_CHOICES = [
        ("horas", "Horas"),
        ("anios", "Años"),
    ]

    unidad_duracion = models.CharField(
        max_length=10,
        choices=UNIDAD_DURACION_CHOICES,
        default="horas",
        help_text="Define si la duración es en horas o años",
    )

    imagen_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL de la imagen/portada del curso",
    )

    fecha_inicio = models.DateField(
        blank=True,
        null=True,
        help_text="Fecha de inicio del curso",
    )

    fecha_fin = models.DateField(
        blank=True,
        null=True,
        help_text="Fecha de finalización del curso",
    )

    fecha_inicio_publicidad = models.DateField(
        null=True, blank=True, help_text="Fecha desde cuando se publica el curso en web"
    )

    fecha_fin_publicidad = models.DateField(
        null=True, blank=True, help_text="Fecha hasta cuando se muestra el curso en web"
    )

    titulo_obtenido = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Título que obtiene el estudiante",
    )

    JORNADA_CHOICES = [
        ("matutina", "Matutina"),
        ("vespertina", "Vespertina"),
        ("nocturna", "Nocturna"),
        ("intensiva", "Intensiva"),
        ("mixta", "Mixta"),
    ]

    jornada = models.CharField(
        max_length=20,
        choices=JORNADA_CHOICES,
        null=True,
        blank=True,
        help_text="Jornada en la que se imparte el curso",
    )

    MODALIDAD_CHOICES = [
        ("presencial", "Presencial"),
        ("virtual", "Virtual"),
        ("hibrida", "Híbrida"),
        ("dual", "Dual"),
    ]

    modalidad = models.CharField(
        max_length=20,
        choices=MODALIDAD_CHOICES,
        null=True,
        blank=True,
        help_text="Modalidad del curso",
    )

    clases = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Días de clases",
    )

    horario = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Rango de horas",
    )

    costo_matricula = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Costo de Matrícula",
        help_text="Costo de matrícula inicial en USD",
    )

    costo_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Costo por Ciclo / Total",
        help_text="Costo total del curso o costo por cada ciclo/semestre",
    )

    cuotas = models.IntegerField(
        null=True, 
        blank=True, 
        verbose_name="Número de Cuotas",
        help_text="Cantidad de cuotas en las que se puede diferir el pago",
    )

    resolucion = models.TextField(
        null=True, blank=True, help_text="Número de resolución oficial del curso"
    )

    presentacion = models.TextField(
        null=True, blank=True, help_text="Presentación/introducción del curso"
    )

    perfil_profesional = models.TextField(
        null=True, blank=True, help_text="Perfil profesional del egresado"
    )

    malla_curricular = models.ImageField(
        upload_to="cursos/mallas_curriculares/",
        null=True,
        blank=True,
        help_text="Imagen de la malla curricular",
    )

    coordinador = models.ForeignKey(
        "Autoridad",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cursos_coordinados",
        help_text="Coordinador o autoridad responsable del curso",
    )

    ESTADO_CHOICES = [
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
        ("cerrado", "Cerrado"),
    ]

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="activo",
        help_text="Estado actual del curso",
    )

    TIPO_CHOICES = [
        ("carrera", "Carrera (Tercer Nivel)"),
        ("moodle", "Curso Moodle Destacado"),
    ]

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default="carrera",
        help_text="Define si es una Carrera de la institución o un curso destacado de Moodle",
    )

    destacado = models.BooleanField(
        default=False,
        help_text="Indica si el curso debe aparecer en la sección de destacados",
    )

    creado_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación del registro",
    )

    actualizado_en = models.DateTimeField(
        auto_now=True,
        help_text="Fecha de última actualización",
    )

    class Meta:
        db_table = "cursos"
        verbose_name = "Programa Académico (Base)"
        verbose_name_plural = "Programas Académicos (Base)"
        ordering = ["-creado_en"]
        indexes = [
            models.Index(fields=["plataforma"]),
            models.Index(fields=["codigo_externo"]),
            models.Index(fields=["estado"]),
            models.Index(fields=["coordinacion"]),
            models.Index(fields=["categoria_curso"]),
            models.Index(fields=["nivel"]),
            models.Index(fields=["coordinador"]),
            models.Index(fields=["jornada"]),
            models.Index(fields=["modalidad"]),
        ]

class Carrera(Curso):
    """
    Modelo Proxy para administrar exclusivamente las Carreras en el Django Admin
    """
    class Meta:
        proxy = True
        verbose_name = "Carrera"
        verbose_name_plural = "Carreras"

class CursoMoodle(Curso):
    """
    Modelo Proxy para administrar exclusivamente los cursos destacados de Moodle
    """
    class Meta:
        proxy = True
        verbose_name = "Curso Moodle Destacado"
        verbose_name_plural = "Cursos Moodle Destacados"


    def __str__(self):
        return f"{self.titulo} - {self.plataforma.nombre}"

    def esta_activo(self):
        """Retorna True si el curso está activo"""
        return self.estado == "activo"

    def esta_publicado(self):
        """Retorna True si el curso está en periodo de publicidad"""
        from django.utils import timezone

        hoy = timezone.localdate()

        if not self.fecha_inicio_publicidad and not self.fecha_fin_publicidad:
            return True  # Sin restricción de fechas

        if self.fecha_inicio_publicidad and self.fecha_inicio_publicidad > hoy:
            return False

        if self.fecha_fin_publicidad and self.fecha_fin_publicidad < hoy:
            return False

        return True

    def get_info_completa(self):
        """Retorna información completa del curso"""
        coordinador = (
            f"{self.coordinador.nombre} {self.coordinador.apellido}"
            if self.coordinador
            else "Sin asignar"
        )

        return {
            "titulo": self.titulo,
            "plataforma": self.plataforma.nombre,
            "coordinacion": self.get_coordinacion_display()
            if self.coordinacion
            else "Sin asignar",
            "categoria": self.categoria_curso.nombre
            if self.categoria_curso
            else "Sin categoría",
            "nivel": self.get_nivel_display() if self.nivel else "No especificado",
            "duracion": f"{self.duracion_valor} {self.get_unidad_duracion_display()}"
            if self.duracion_valor
            else "No especificada",
            "coordinador": coordinador,
            "jornada": self.get_jornada_display()
            if self.jornada
            else "No especificada",
            "modalidad": self.get_modalidad_display()
            if self.modalidad
            else "No especificada",
            "clases": self.clases if self.clases else "No especificado",
            "horario": self.horario if self.horario else "No especificado",
            "cuotas": self.cuotas if self.cuotas else "Sin cuotas", 
            "costo_total": f"${self.costo_total}" if self.costo_total else "Gratuito",
            "estado": self.get_estado_display(),
        }


class CategoriaCurso(models.Model):
    """
    Categorías de cursos según coordinación.
    - Vicerrectorado: Tercer Nivel, Cuarto Nivel
    - Educación Continua: Gastronomía, Tecnología, etc.
    """

    COORDINACION_CHOICES = [
        (1, "Vicerrectorado"),
        (2, "Educación Continua"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    coordinacion = models.IntegerField(
        choices=COORDINACION_CHOICES, help_text="1=Vicerrectorado, 2=Educación Continua"
    )

    nombre = models.CharField(
        max_length=100,
        help_text="Nombre de la categoría (Tercer Nivel, Gastronomía, etc.)",
    )

    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "categorias_curso"
        verbose_name = "Categoría de Curso"
        verbose_name_plural = "Categorías de Cursos"
        unique_together = [["coordinacion", "nombre"]]

    def __str__(self):
        """Muestra: 'Tercer Nivel (Vicerrectorado)'"""
        return f"{self.nombre} ({self.get_coordinacion_display()})"


class RecursoAcademico(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único del recurso académico",
    )
    curso = models.ForeignKey(
        "Curso",
        on_delete=models.CASCADE,
        related_name="recursos",
        help_text="Curso al que pertenece este recurso",
    )

    plataforma = models.ForeignKey(
        "integration.Plataforma",
        on_delete=models.CASCADE,
        related_name="recursos",
        help_text="Plataforma donde está alojado el recurso",
    )

    codigo_externo = models.CharField(
        max_length=100,
        help_text="ID del recurso en la plataforma externa",
    )

    titulo = models.CharField(
        max_length=255,
        help_text="Título del recurso",
    )

    TIPO_CHOICES = [
        ("video", "Video"),
        ("pdf", "PDF"),
        ("evaluacion", "Evaluación"),
        ("enlace", "Enlace"),
        ("documento", "Documento"),
        ("presentacion", "Presentación"),
    ]

    tipo = models.CharField(
        max_length=50,
        choices=TIPO_CHOICES,
        help_text="Tipo de recurso",
    )

    FORMATO_CHOICES = [
        ("mp4", "MP4"),
        ("pdf", "PDF"),
        ("html", "HTML"),
        ("url", "URL"),
        ("docx", "DOCX"),
        ("pptx", "PPTX"),
        ("xlsx", "XLSX"),
    ]

    formato = models.CharField(
        max_length=20,
        choices=FORMATO_CHOICES,
        blank=True,
        null=True,
        help_text="Formato del archivo",
    )

    url = models.URLField(
        max_length=500,
        help_text="URL del recurso",
    )

    tamano_bytes = models.BigIntegerField(
        blank=True,
        null=True,
        help_text="Tamaño del archivo en bytes",
    )

    duracion_segundos = models.IntegerField(
        blank=True,
        null=True,
        help_text="Duración en segundos (solo para videos)",
    )

    orden = models.IntegerField(
        default=0,
        help_text="Orden de presentación dentro del curso",
    )

    activo = models.BooleanField(
        default=True,
        help_text="Si el recurso está disponible",
    )

    creado_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación del registro",
    )

    class Meta:
        db_table = "recursos_academicos"
        verbose_name = "Recurso Académico"
        verbose_name_plural = "Recursos Académicos"
        ordering = ["curso", "orden"]
        indexes = [
            models.Index(fields=["curso"]),
            models.Index(fields=["plataforma"]),
            models.Index(fields=["tipo"]),
            models.Index(fields=["activo"]),
            models.Index(fields=["orden"]),
        ]

    def __str__(self):
        return f"{self.titulo} ({self.get_tipo_display()}) - {self.curso.titulo}"

    def get_tamano_legible(self):
        """Retorna el tamaño en formato legible"""
        if not self.tamano_bytes:
            return "N/A"

        if self.tamano_bytes < 1024:
            return f"{self.tamano_bytes} bytes"
        elif self.tamano_bytes < 1024 * 1024:
            kb = self.tamano_bytes / 1024
            return f"{kb:.2f} KB"
        else:
            mb = self.tamano_bytes / (1024 * 1024)
            return f"{mb:.2f} MB"

    def get_duracion_legible(self):
        """Retorna la duración en formato legible"""
        if not self.duracion_segundos:
            return "N/A"

        horas = self.duracion_segundos // 3600
        minutos = (self.duracion_segundos % 3600) // 60
        segundos = self.duracion_segundos % 60

        if horas > 0:
            return f"{horas}h {minutos}m {segundos}s"
        elif minutos > 0:
            return f"{minutos}m {segundos}s"
        else:
            return f"{segundos}s"

    def get_info_completa(self):
        """Retorna información completa del recurso"""
        return {
            "titulo": self.titulo,
            "tipo": self.get_tipo_display(),
            "formato": self.get_formato_display() if self.formato else "N/A",
            "curso": self.curso.titulo,
            "plataforma": self.plataforma.nombre,
            "tamaño": self.get_tamano_legible(),
            "duración": self.get_duracion_legible(),
            "orden": self.orden,
            "activo": self.activo,
        }


class AccesoRecurso(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único del acceso",
    )

    recurso = models.ForeignKey(
        "RecursoAcademico",
        on_delete=models.CASCADE,
        related_name="accesos",
        help_text="Recurso que fue accedido",
    )

    usuario = models.ForeignKey(
        "auth_app.Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accesos_recursos",
        help_text="Usuario que accedió al recurso",
    )

    sesion = models.ForeignKey(
        "auth_app.Sesion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accesos_recursos",
        help_text="Sesión en la que se accedió al recurso",
    )

    plataforma = models.ForeignKey(
        "integration.Plataforma",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accesos_recursos",
        help_text="Plataforma donde se accedió al recurso",
    )

    TIPO_ACCESO_CHOICES = [
        ("descarga", "Descarga"),
        ("visualizacion", "Visualización"),
        ("reproduccion", "Reproducción"),
    ]

    tipo_acceso = models.CharField(
        max_length=50,
        choices=TIPO_ACCESO_CHOICES,
        help_text="Tipo de acceso realizado",
    )

    porcentaje_completado = models.IntegerField(
        default=0,
        help_text="Porcentaje completado del recurso (0-100)",
    )

    tiempo_acceso_segundos = models.IntegerField(
        default=0,
        help_text="Tiempo que el usuario pasó con el recurso (en segundos)",
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora del acceso",
    )

    class Meta:
        db_table = "accesos_recursos"
        verbose_name = "Acceso a Recurso"
        verbose_name_plural = "Accesos a Recursos"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["recurso"]),
            models.Index(fields=["usuario"]),
            models.Index(fields=["sesion"]),
            models.Index(fields=["plataforma"]),
            models.Index(fields=["tipo_acceso"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "Anónimo"
        return (
            f"{usuario_str} - {self.get_tipo_acceso_display()} - {self.recurso.titulo}"
        )

    def fue_completado(self):
        """Retorna True si el usuario completó el recurso"""
        return self.porcentaje_completado >= 100

    def get_tiempo_legible(self):
        """Retorna el tiempo de acceso en formato legible"""
        if self.tiempo_acceso_segundos == 0:
            return "0s"

        horas = self.tiempo_acceso_segundos // 3600
        minutos = (self.tiempo_acceso_segundos % 3600) // 60
        segundos = self.tiempo_acceso_segundos % 60

        if horas > 0:
            return f"{horas}h {minutos}m {segundos}s"
        elif minutos > 0:
            return f"{minutos}m {segundos}s"
        else:
            return f"{segundos}s"

    def get_info_completa(self):
        """Retorna información completa del acceso"""
        return {
            "usuario": self.usuario.username if self.usuario else "Anónimo",
            "recurso": self.recurso.titulo,
            "tipo": self.get_tipo_acceso_display(),
            "porcentaje": f"{self.porcentaje_completado}%",
            "tiempo": self.get_tiempo_legible(),
            "completado": self.fue_completado(),
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }


class NoticiasPopup(models.Model):
    """
    Noticias emergentes que se muestran como popup en el portal.
    Estas son distintas a las noticias regulares del blog/CMS.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único de la noticia popup",
    )

    nombre = models.CharField(
        max_length=255,
        help_text="Título de la noticia emergente",
    )

    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Contenido detallado de la noticia (opcional)",
    )

    imagen = models.ImageField(
        upload_to="noticias_popup/%Y/%m/",
        blank=True,
        null=True,
        help_text="Imagen de la noticia popup",
    )

    fecha_inicio = models.DateField(
        help_text="Fecha desde cuando se muestra la noticia",
    )

    fecha_fin = models.DateField(
        help_text="Fecha hasta cuando se muestra la noticia",
    )

    estado = models.BooleanField(
        default=False,
        help_text="Si la noticia está activa (True) o inactiva (False)",
    )

    enlace_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL opcional si la noticia lleva un enlace externo",
    )

    enlace_texto = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Texto del botón del enlace (ej: 'Leer más', 'Inscribirte')",
    )

    creado_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación del registro",
    )

    actualizado_en = models.DateTimeField(
        auto_now=True,
        help_text="Fecha de última actualización",
    )

    class Meta:
        db_table = "noticias_popup"
        verbose_name = "Noticia Popup"
        verbose_name_plural = "Noticias Popup"
        ordering = ["-creado_en"]  
        indexes = [
            models.Index(fields=["estado"]),
            models.Index(fields=["fecha_inicio", "fecha_fin"]),
            models.Index(fields=["creado_en"]),
        ]

    def __str__(self):
        estado = "ACTIVA" if self.estado else "INACTIVA"
        return f"[{estado}] {self.nombre}"

    def esta_vigente(self):
        """Retorna True si la noticia está dentro del rango de fechas"""
        from django.utils import timezone

        hoy = timezone.localdate()
        return self.fecha_inicio <= hoy <= self.fecha_fin

    def debe_mostrarse(self):
        """Retorna True si la noticia debe mostrarse ahora"""
        return self.estado and self.esta_vigente()

    def get_url_imagen(self):
        """Retorna la URL de la imagen o None"""
        if self.imagen:
            return self.imagen.url
        return None

    def get_info_completa(self):
        """Retorna información completa de la noticia"""
        return {
            "nombre": self.nombre,
            "descripcion": self.descripcion or "Sin descripción",
            "estado": "Activa" if self.estado else "Inactiva",
            "vigente": self.esta_vigente(),
            "debe_mostrarse": self.debe_mostrarse(),
            "periodo": f"{self.fecha_inicio} a {self.fecha_fin}",
            "imagen": self.get_url_imagen(),
            "enlace": self.enlace_url or "Sin enlace",
        }


class Interesado(models.Model):
    """
    Formularios de contacto de personas interesadas en programas académicos
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único del interesado",
    )

    # Datos personales
    nombres = models.CharField(
        max_length=100,
        help_text="Nombres del interesado",
    )

    apellidos = models.CharField(
        max_length=100,
        help_text="Apellidos del interesado",
    )

    email = models.EmailField(
        help_text="Correo electrónico de contacto",
    )

    telefono = models.CharField(
        max_length=15,
        help_text="Número de teléfono",
    )

    # Relación con el programa de interés
    curso_interes = models.ForeignKey(
        "Curso",
        on_delete=models.CASCADE,
        related_name="interesados",
        help_text="Programa/Curso de interés",
    )

    mensaje = models.TextField(
        blank=True,
        null=True,
        help_text="Mensaje o consulta adicional del interesado",
    )

    acepta_terminos = models.BooleanField(
        default=False, help_text="Aceptación de términos y condiciones (requerido)"
    )

    # Auditoría
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora del registro de interés",
    )

    atendido = models.BooleanField(
        default=False,
        help_text="Si ya fue contactado por el instituto",
    )

    fecha_atencion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que fue atendido",
    )

    notas_seguimiento = models.TextField(
        blank=True,
        null=True,
        help_text="Notas del equipo sobre el seguimiento",
    )

    class Meta:
        db_table = "interesados"
        verbose_name = "Interesado"
        verbose_name_plural = "Interesados"
        ordering = ["-fecha_registro"]
        indexes = [
            models.Index(fields=["curso_interes"]),
            models.Index(fields=["email"]),
            models.Index(fields=["atendido"]),
            models.Index(fields=["fecha_registro"]),
            models.Index(fields=["acepta_terminos"]),
        ]

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.curso_interes.titulo}"

    def get_nombre_completo(self):
        """Retorna el nombre completo"""
        return f"{self.nombres} {self.apellidos}"


class Etiqueta(models.Model):
    """
    Etiquetas/Tags para clasificar posts (noticias, blogs, publicaciones).
    Relación N:M con Post.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único de la etiqueta",
    )

    nombre = models.CharField(
        max_length=50,
        unique=True,
        help_text="Nombre de la etiqueta (ej: Tecnología, Educación)",
    )

    descripcion = models.TextField(
        blank=True, null=True, help_text="Descripción opcional de la etiqueta"
    )

    activo = models.BooleanField(
        default=True, help_text="Si la etiqueta está activa y disponible para usar"
    )

    creado_en = models.DateTimeField(auto_now_add=True, help_text="Fecha de creación")

    actualizado_en = models.DateTimeField(
        auto_now=True, help_text="Fecha de última actualización"
    )

    class Meta:
        db_table = "etiquetas"
        verbose_name = "Etiqueta"
        verbose_name_plural = "Etiquetas"
        ordering = ["nombre"]
        indexes = [
            models.Index(fields=["nombre"]),
            models.Index(fields=["activo"]),
        ]

    def __str__(self):
        return self.nombre


class Post(models.Model):
    """
    Sistema de gestión de contenido: Noticias, Blogs y Publicaciones Científicas
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único del post",
    )

    titulo = models.CharField(
        max_length=255,
        help_text="Título del post",
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text="URL amigable (se genera automáticamente del título)",
    )

    resumen = models.TextField(
        max_length=500,
        help_text="Resumen corto para vista previa en tarjetas",
    )

    contenido = models.TextField(
        help_text="Contenido completo del post (puede incluir HTML)",
    )

    TIPO_CHOICES = [
        ("noticia", "Noticia"),
        ("blog", "Blog"),
        ("publicacion", "Publicación Científica"),
        ("hitos_logros", "Hitos y Logros"),
    ]

    tipo = models.CharField(
        max_length=50,
        choices=TIPO_CHOICES,
        help_text="Tipo de contenido",
    )

    clasificacion = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=[
            ("institucional", "Institucional"),
            ("academico", "Académico"),
            ("eventos", "Eventos"),
            ("deportes", "Deportes"),
            ("comunicados", "Comunicados"),
        ],
        help_text="Clasificación de la noticia",
    )

    autor_texto = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Nombre libre del autor (usado cuando el autor no es un usuario del sistema)",
    )

    archivo_pdf = models.FileField(
        upload_to="posts_pdfs/%Y/%m/",
        blank=True,
        null=True,
        help_text="Archivo PDF asociado al post (opcional, útil para Revistas o Blogs)",
    )

    imagen_portada = models.ImageField(
        upload_to="posts/%Y/%m/",
        blank=True,
        null=True,
        help_text="Imagen principal del post",
    )

    autor = models.ForeignKey(
        "auth_app.Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts_autor",
        help_text="Autor del post",
    )

    ESTADO_CHOICES = [
        ("borrador", "Borrador"),
        ("publicado", "Publicado"),
        ("archivado", "Archivado"),
    ]

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="borrador",
        help_text="Estado de publicación",
    )

    destacado = models.BooleanField(
        default=False,
        help_text="Si es True, aparece en el banner principal",
    )

    fecha_publicacion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha de publicación (visible para usuarios)",
    )

    # SEO
    meta_descripcion = models.CharField(
        max_length=160,
        blank=True,
        null=True,
        help_text="Meta descripción para SEO",
    )

    # ========== RELACIÓN N:M CON ETIQUETAS ==========

    etiquetas = models.ManyToManyField(
        "Etiqueta",
        blank=True,
        related_name="posts",
        help_text="Etiquetas asociadas al post",
    )

    # Auditoría
    creado_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación",
    )

    actualizado_en = models.DateTimeField(
        auto_now=True,
        help_text="Fecha de última actualización",
    )

    class Meta:
        db_table = "posts"
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ["-fecha_publicacion", "-creado_en"]
        indexes = [
            models.Index(fields=["tipo"]),
            models.Index(fields=["estado"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["destacado"]),
            models.Index(fields=["fecha_publicacion"]),
            models.Index(fields=["creado_en"]),
        ]

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.titulo}"

    def save(self, *args, **kwargs):
        """Generar slug automáticamente si no existe"""
        if not self.slug:
            from django.utils.text import slugify

            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def esta_publicado(self):
        """Retorna True si el post está publicado"""
        return self.estado == "publicado"

    def get_url_imagen(self):
        """Retorna la URL de la imagen o None"""
        if self.imagen_portada:
            return self.imagen_portada.url
        return None

    def get_info_completa(self):
        """Retorna información completa del post"""
        autor_nombre = self.autor.get_nombre_completo() if self.autor else "Sin autor"
        return {
            "titulo": self.titulo,
            "slug": self.slug,
            "tipo": self.get_tipo_display(),
            "estado": self.get_estado_display(),
            "autor": autor_nombre,
            "destacado": self.destacado,
            "fecha_publicacion": self.fecha_publicacion.strftime("%Y-%m-%d")
            if self.fecha_publicacion
            else "No publicado",
            "imagen": self.get_url_imagen(),
            "etiquetas": [etiqueta.nombre for etiqueta in self.etiquetas.all()],
        }


class Autoridad(models.Model):
    """
    Equipo directivo e institucional del ISTEPS
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único de la autoridad",
    )

    nombres = models.CharField(
        max_length=100,
        help_text="Nombres de la autoridad",
    )

    apellidos = models.CharField(
        max_length=100,
        help_text="Apellidos de la autoridad",
    )
    titulo_autoridad = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Título académico o profesional (ej: PhD., Msc., Ing., Dr.)",
    )

    CARGO_CHOICES = [
        ("rector", "Rector"),
        ("vicerrector", "Vicerrector"),
        ("coordinador_academico", "Coordinador Académico"),
        ("secretario_general", "Secretario General"),
        ("director_carrera", "Director de Carrera"),
        ("coordinador_investigacion", "Coordinador de Investigación"),
        ("representante_docente", "Representante Docentes"),
        ("representante_estudiante", "Representante Estudiantes"),
        ("consejo_regentes", "Consejo de Regentes"),
    ]

    cargo = models.CharField(
        max_length=100,
        choices=CARGO_CHOICES,
        help_text="Cargo que desempeña",
    )

    email = models.EmailField(blank=True, null=True)

    fotografia = models.ImageField(
        upload_to="autoridades/",
        blank=True,
        null=True,
        help_text="Fotografía oficial de la autoridad",
    )

    biografia = models.TextField(
        blank=True,
        null=True,
        help_text="Biografía profesional y trayectoria",
    )

    orden = models.IntegerField(
        default=0,
        help_text="Orden de visualización en la web (menor = primero)",
    )

    activo = models.BooleanField(
        default=True,
        help_text="Si la autoridad está actualmente en el cargo",
    )

    fecha_inicio = models.DateField(
        help_text="Fecha de inicio en el cargo",
    )

    fecha_fin = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha de fin del cargo (NULL si está activo)",
    )

    # Auditoría
    creado_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación del registro",
    )

    actualizado_en = models.DateTimeField(
        auto_now=True,
        help_text="Fecha de última actualización",
    )

    class Meta:
        db_table = "autoridades"
        verbose_name = "Autoridad"
        verbose_name_plural = "Autoridades"
        ordering = ["orden", "apellidos"]
        indexes = [
            models.Index(fields=["cargo"]),
            models.Index(fields=["activo"]),
            models.Index(fields=["orden"]),
        ]

    def __str__(self):
        return f"{self.get_nombre_completo()} - {self.get_cargo_display()}"

    def clean(self):
        from django.core.exceptions import ValidationError
        # Validar el email requerido según el cargo
        if self.cargo != "consejo_regentes" and not self.email:
            raise ValidationError({
                "email": "Este cargo requiere correo institucional."
            })
        super().clean()

    def get_nombre_completo(self):
        """Retorna el nombre completo"""
        return f"{self.nombres} {self.apellidos}"

    def get_url_foto(self):
        """Retorna la URL de la foto o None"""
        if self.fotografia:
            return self.fotografia.url
        return None

    def get_info_completa(self):
        """Retorna información completa de la autoridad"""
        return {
            "nombre_completo": self.get_nombre_completo(),
            "cargo": self.get_cargo_display(),
            "email": self.email,
            "fotografia": self.get_url_foto(),
            "biografia": self.biografia or "Sin biografía",
            "activo": self.activo,
            "periodo": f"Desde {self.fecha_inicio}"
            + (f" hasta {self.fecha_fin}" if self.fecha_fin else " (Actual)"),
        }


class DocumentoTransparencia(models.Model):
    """
    Repositorio de documentos legales y de transparencia institucional
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único del documento",
    )

    titulo = models.CharField(
        max_length=255,
        help_text="Título del documento",
    )

    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción del contenido del documento",
    )

    CATEGORIA_CHOICES = [
        ("normativa institucional", "Normativa Institucional"),
        ("información económica", "Infromación Económica"),
        ("rendición de cuentas", "Rendición de Cuentas"),
        ("planificación institucional", "Planificación Institucional"),
    ]

    categoria = models.CharField(
        max_length=100,
        choices=CATEGORIA_CHOICES,
        help_text="Categoría principal del documento",
    )

    SUBCATEGORIA_CHOICES = [
        ("presupuesto", "Presupuesto"),
        ("reglamentos", "Reglamentos"),
        ("actas", "Actas"),
        ("informes", "Informes"),
        ("convenios", "Convenios"),
        ("resoluciones", "Resoluciones"),
        ("normativa", "Normativa"),
        ("financiero", "Financiero"),
        ("estatutos", "Estatutos"),
        ("politicas", "Políticas"),
        ("protocolos", "Protocolos"),
        ("manuales", "Manuales"),
        ("guias", "Guías"),
        ("remuneraciones", "Remuneraciones"),
        ("estados_financieros", "Estados Financieros"),
        ("planificacion_operativa", "Planificación Operativa"),
        ("planificacion_estrategica", "Planificación Estratégica"),
    ]

    subcategoria = models.CharField(
        max_length=100,
        choices=SUBCATEGORIA_CHOICES,
        help_text="Subcategoría del documento",
    )

    archivo = models.FileField(
        upload_to="transparencia/%Y/",
        help_text="Archivo PDF del documento",
    )

    archivo_nombre = models.CharField(
        max_length=255,
        blank=True,
        help_text="Nombre original del archivo",
    )

    archivo_tamano_bytes = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Tamaño del archivo en bytes",
    )

    fecha_documento = models.DateField(
        help_text="Fecha del documento (fecha de emisión)",
    )

    # Auditoría
    subido_por = models.ForeignKey(
        "auth_app.Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documentos_subidos",
        help_text="Usuario que subió el documento",
    )

    subido_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de carga del documento",
    )

    actualizado_en = models.DateTimeField(
        auto_now=True,
        help_text="Fecha de última actualización",
    )

    class Meta:
        db_table = "documentos_transparencia"
        verbose_name = "Documento de Transparencia"
        verbose_name_plural = "Documentos de Transparencia"
        ordering = ["-fecha_documento", "-subido_en"]
        indexes = [
            models.Index(fields=["categoria"]),
            models.Index(fields=["subcategoria"]),
            models.Index(fields=["fecha_documento"]),
            models.Index(fields=["subido_en"]),
        ]

    def __str__(self):
        return f"[{self.get_categoria_display()}] {self.titulo}"

    def save(self, *args, **kwargs):
        """Guardar nombre y tamaño del archivo automáticamente"""
        if self.archivo:
            self.archivo_nombre = self.archivo.name
            self.archivo_tamano_bytes = self.archivo.size
        super().save(*args, **kwargs)

    def get_url_archivo(self):
        """Retorna la URL del archivo"""
        if self.archivo:
            return self.archivo.url
        return None

    def get_tamano_legible(self):
        """Retorna el tamaño en formato legible"""
        if not self.archivo_tamano_bytes:
            return "N/A"

        if self.archivo_tamano_bytes < 1024:
            return f"{self.archivo_tamano_bytes} bytes"
        elif self.archivo_tamano_bytes < 1024 * 1024:
            kb = self.archivo_tamano_bytes / 1024
            return f"{kb:.2f} KB"
        else:
            mb = self.archivo_tamano_bytes / (1024 * 1024)
            return f"{mb:.2f} MB"

    def get_info_completa(self):
        """Retorna información completa del documento"""
        subidor = (
            self.subido_por.get_nombre_completo() if self.subido_por else "Sistema"
        )
        return {
            "titulo": self.titulo,
            "categoria": self.get_categoria_display(),
            "subcategoria": self.get_subcategoria_display(),
            "descripcion": self.descripcion or "Sin descripción",
            "archivo": self.get_url_archivo(),
            "tamaño": self.get_tamano_legible(),
            "fecha_documento": self.fecha_documento.strftime("%Y-%m-%d"),
            "subido_por": subidor,
            "subido_en": self.subido_en.strftime("%Y-%m-%d %H:%M:%S"),
        }
