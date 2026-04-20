from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import login, logout
from auth_app.models import Usuario, PreferenciasUsuario

# Importar desde api.serializers.auth_serializers (estructura con subcarpetas)
from api.serializers.auth_serializers import (
    UsuarioPerfilSerializer,
    UsuarioActualizarSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    PreferenciasSerializer,
)


class LoginAPIView(APIView):
    """
    POST /api/auth/login/

    Endpoint de login que devuelve JWT tokens.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]

            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)

            # Actualizar last_login
            login(request, user)

            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": UsuarioPerfilSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    """
    POST /api/auth/logout/

    Endpoint de logout que invalida el refresh token.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")

            if not refresh_token:
                return Response(
                    {"error": "Se requiere el refresh token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            logout(request)

            return Response({"message": "Logout exitoso"}, status=status.HTTP_200_OK)

        except TokenError:
            return Response(
                {"error": "Token inválido o expirado"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PerfilUsuarioAPIView(APIView):
    """
    GET /api/usuario/perfil/

    Obtiene el perfil del usuario autenticado.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UsuarioPerfilSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ActualizarPerfilAPIView(APIView):
    """
    PUT /api/usuario/perfil/actualizar/
    PATCH /api/usuario/perfil/actualizar/

    Actualiza el perfil del usuario autenticado.
    """

    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        serializer = UsuarioActualizarSerializer(
            request.user, data=request.data, partial=False
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                UsuarioPerfilSerializer(request.user).data, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        serializer = UsuarioActualizarSerializer(
            request.user, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                UsuarioPerfilSerializer(request.user).data, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CambiarPasswordAPIView(APIView):
    """
    POST /api/usuario/cambiar-password/

    Cambia la contraseña del usuario autenticado.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user

            if not user.check_password(serializer.validated_data["old_password"]):
                return Response(
                    {"old_password": "Contraseña actual incorrecta"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(serializer.validated_data["new_password"])
            user.save()

            return Response(
                {"message": "Contraseña actualizada exitosamente"},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PreferenciasUsuarioAPIView(APIView):
    """
    GET /api/usuario/preferencias/
    PUT /api/usuario/preferencias/

    Gestiona las preferencias del usuario.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            preferencias = request.user.preferencias
            serializer = PreferenciasSerializer(
                {
                    "idioma": preferencias.idioma,
                    "tema": preferencias.tema,
                    "zona_horaria": preferencias.zona_horaria,
                    "notificaciones_email": preferencias.notificaciones_email,
                    "dashboard_layout": preferencias.dashboard_layout,
                }
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        except PreferenciasUsuario.DoesNotExist:
            preferencias = PreferenciasUsuario.objects.create(usuario=request.user)
            serializer = PreferenciasSerializer(
                {
                    "idioma": preferencias.idioma,
                    "tema": preferencias.tema,
                    "zona_horaria": preferencias.zona_horaria,
                    "notificaciones_email": preferencias.notificaciones_email,
                    "dashboard_layout": preferencias.dashboard_layout,
                }
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = PreferenciasSerializer(data=request.data, partial=True)

        if serializer.is_valid():
            preferencias, created = PreferenciasUsuario.objects.get_or_create(
                usuario=request.user
            )

            for field, value in serializer.validated_data.items():
                setattr(preferencias, field, value)

            preferencias.save()

            return Response(
                PreferenciasSerializer(
                    {
                        "idioma": preferencias.idioma,
                        "tema": preferencias.tema,
                        "zona_horaria": preferencias.zona_horaria,
                        "notificaciones_email": preferencias.notificaciones_email,
                        "dashboard_layout": preferencias.dashboard_layout,
                    }
                ).data,
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerificarTokenAPIView(APIView):
    """
    POST /api/auth/verificar-token/

    Verifica si un access token es válido.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get("token")

        if not token:
            return Response(
                {"error": "Token requerido"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from rest_framework_simplejwt.tokens import AccessToken

            access_token = AccessToken(token)
            user_id = access_token["user_id"]

            user = Usuario.objects.get(id=user_id)

            return Response(
                {"valid": True, "user": UsuarioPerfilSerializer(user).data},
                status=status.HTTP_200_OK,
            )

        except (TokenError, InvalidToken, Usuario.DoesNotExist):
            return Response(
                {"valid": False, "error": "Token inválido o expirado"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def usuario_info(request):
    """
    GET /api/usuario/info/

    Endpoint simple que devuelve información básica del usuario.
    """
    return Response(
        {
            "username": request.user.username,
            "email": request.user.email,
            "nombre_completo": request.user.get_nombre_completo(),
            "is_staff": request.user.is_staff,
            "is_authenticated": True,
        }
    )


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """
    GET /api/health/

    Endpoint de health check.
    """
    return Response(
        {"status": "ok", "message": "Portal ISTEPS API funcionando correctamente"}
    )


# ============================================
# VISTAS PARA INTEGRACIÓN MICROSOFT 365 + JWT
# ============================================


class ObtenerTokenDesdeSesionAPIView(APIView):
    """
    GET /api/auth/social-token/

    Obtiene tokens JWT si el usuario ya está autenticado con Microsoft 365.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # Verificar si el usuario está autenticado
        if not request.user.is_authenticated:
            return Response(
                {
                    "error": "Usuario no autenticado. Debe hacer login con Microsoft 365 primero."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Intentar obtener tokens desde la sesión
        access_token = request.session.get("jwt_access_token")
        refresh_token = request.session.get("jwt_refresh_token")

        # Si no hay tokens en sesión, generarlos ahora
        if not access_token or not refresh_token:
            refresh = RefreshToken.for_user(request.user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Guardar en sesión
            request.session["jwt_access_token"] = access_token
            request.session["jwt_refresh_token"] = refresh_token

        return Response(
            {
                "access": access_token,
                "refresh": refresh_token,
                "user": UsuarioPerfilSerializer(request.user).data,
            },
            status=status.HTTP_200_OK,
        )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def verificar_autenticacion(request):
    """
    GET /api/auth/verificar-autenticacion/

    Verifica si el usuario tiene sesión activa.
    Retorna True/False y datos del usuario si está autenticado.
    """
    return Response(
        {
            "autenticado": True,
            "usuario": {
                "id": str(request.user.id),
                "username": request.user.username,
                "email": request.user.email,
                "nombre_completo": request.user.get_nombre_completo(),
                "is_staff": request.user.is_staff,
            },
        }
    )
