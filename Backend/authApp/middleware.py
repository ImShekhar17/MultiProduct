import logging
from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)

@database_sync_to_async
def get_user_from_token(token_string):
    """
    Validates the JWT token and returns the user object.
    Professional approach uses simplejwt's AccessToken for validation.
    """
    try:
        access_token = AccessToken(token_string)
        user_id = access_token.get('user_id')
        if not user_id:
            return AnonymousUser()
        
        # In a high-load system, we might cache this lookup or use the payload
        return User.objects.get(id=user_id)
    except Exception as e:
        logger.debug(f"WebSocket JWT Auth failed: {e}")
        return AnonymousUser()

class JWTAuthMiddleware:
    """
    Custom middleware that takes a JWT token from the query string or 
    header and authenticates the user.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Close old database connections to prevent leakages
        close_old_connections()

        # Try to get token from header or query string
        token = None
        
        # 1. Try Query String (Meta/Amazon standard for WS handshakes)
        query_string = scope.get("query_string", b"").decode("utf-8")
        query_params = parse_qs(query_string)
        if "token" in query_params:
            token = query_params["token"][0]
        
        # 2. Try Headers if not in query string
        if not token:
            headers = dict(scope.get("headers", []))
            if b"authorization" in headers:
                try:
                    auth_header = headers[b"authorization"].decode("utf-8")
                    if auth_header.startswith("Bearer "):
                        token = auth_header.split(" ")[1]
                except Exception:
                    pass

        if token:
            scope["user"] = await get_user_from_token(token)
        else:
            scope["user"] = AnonymousUser()

        return await self.app(scope, receive, send)

def JWTAuthMiddlewareStack(app):
    """Utility to wrap the app in the JWT middleware."""
    return JWTAuthMiddleware(app)
