from rest_framework import serializers
from auth_app.models import Usuario
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializador completo del modelo Usuario.
    """

    class Meta:
        model = Usuario
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "nombres",
            "apellidos",
            "cedula",
            "telefono",
            "fecha_nacimiento",
            "estado",
            "is_staff",
            "is_active",
            "is_superuser",
            "date_joined",
            "last_login",
            "creado_en",
            "actualizado_en",
        ]
        read_only_fields = [
            "id",
            "username",
            "email",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
            "creado_en",
            "actualizado_en",
        ]


class UsuarioPerfilSerializer(serializers.ModelSerializer):
    """
    Serializador para el perfil público del usuario.
    """

    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            "id",
            "username",
            "email",
            "nombres",
            "apellidos",
            "nombre_completo",
            "cedula",
            "telefono",
            "fecha_nacimiento",
            "estado",
            "is_staff",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "username",
            "email",
            "is_staff",
            "date_joined",
        ]

    def get_nombre_completo(self, obj):
        return obj.get_nombre_completo()


class UsuarioActualizarSerializer(serializers.ModelSerializer):
    """
    Serializador para actualizar el perfil del usuario.
    """

    class Meta:
        model = Usuario
        fields = [
            "nombres",
            "apellidos",
            "cedula",
            "telefono",
            "fecha_nacimiento",
        ]

    def validate_cedula(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("La cédula debe contener solo números")
        if value and len(value) != 10:
            raise serializers.ValidationError("La cédula debe tener 10 dígitos")
        return value

    def validate_telefono(self, value):
        if (
            value
            and not value.replace("+", "").replace("-", "").replace(" ", "").isdigit()
        ):
            raise serializers.ValidationError(
                "El teléfono contiene caracteres inválidos"
            )
        return value


class LoginSerializer(serializers.Serializer):
    """
    Serializador para el login.
    """

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        # Intentar autenticar
        user = authenticate(username=username, password=password)

        if user is None:
            # Intentar con email
            try:
                usuario = Usuario.objects.get(email=username)
                user = authenticate(username=usuario.username, password=password)
            except Usuario.DoesNotExist:
                pass

        if user is None:
            raise serializers.ValidationError("Credenciales inválidas")

        if not user.is_active:
            raise serializers.ValidationError("Usuario inactivo")

        attrs["user"] = user
        return attrs


class TokenSerializer(serializers.Serializer):
    """
    Serializador para la respuesta de tokens JWT.
    """

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = UsuarioPerfilSerializer(read_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializador para cambiar contraseña.
    """

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Las contraseñas no coinciden"}
            )

        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError(
                {"new_password": "La nueva contraseña debe ser diferente a la actual"}
            )

        return attrs

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "La contraseña debe tener al menos 8 caracteres"
            )
        return value


class PreferenciasSerializer(serializers.Serializer):
    """
    Serializador para preferencias del usuario.
    """

    idioma = serializers.ChoiceField(
        choices=[("es", "Español"), ("en", "English")], default="es"
    )
    tema = serializers.ChoiceField(
        choices=[("claro", "Claro"), ("oscuro", "Oscuro"), ("auto", "Automático")],
        default="claro",
    )
    zona_horaria = serializers.CharField(default="America/Guayaquil")
    notificaciones_email = serializers.BooleanField(default=True)
    dashboard_layout = serializers.JSONField(required=False)
