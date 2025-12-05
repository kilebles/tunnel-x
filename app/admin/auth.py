from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.core.settings import config


class AdminAuth(AuthenticationBackend):
    """Авторизация для админ-панели."""
    
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        
        if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
            request.session.update({"authenticated": True})
            return True
        
        return False
    
    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True
    
    async def authenticate(self, request: Request) -> bool:
        return request.session.get("authenticated", False)