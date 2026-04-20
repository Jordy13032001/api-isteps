from django.dispatch import receiver
from allauth.account.signals import user_logged_in
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def generate_jwt_on_social_login(sender, request, user, **kwargs):
    """
    Signal que se ejecuta cuando un usuario hace login con Microsoft 365.
    Genera automáticamente los tokens JWT y los guarda en la sesión.
    """
    # Generar tokens JWT
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    # Guardar tokens en la sesión de Django
    request.session["jwt_access_token"] = access_token
    request.session["jwt_refresh_token"] = refresh_token

    logger.info(f"JWT tokens generados automáticamente para usuario: {user.username}")

    # Opcional: También guardar en cookies para que el frontend los use
    # (Se hará en la vista después del redirect)
