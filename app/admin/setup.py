from sqladmin import Admin

from app.db.session import engine
from app.core.settings import config
from app.admin.auth import AdminAuth
from app.admin.views import (
    UserAdmin, 
    SubscriptionAdmin, 
    WalletAdmin,
    DiscountAdmin,
    PromoCodeAdmin,
    BroadcastAdmin
)


def setup_admin(app):
    """Настраивает админ-панель."""
    
    authentication_backend = AdminAuth(secret_key=config.SECRET_KEY)
    
    admin = Admin(
        app,
        engine,
        title="Tunnel-X Admin",
        base_url="/admin",
        authentication_backend=authentication_backend,
    )
    
    admin.add_view(UserAdmin)
    admin.add_view(SubscriptionAdmin)
    admin.add_view(WalletAdmin)
    admin.add_view(DiscountAdmin)
    admin.add_view(PromoCodeAdmin)
    admin.add_view(BroadcastAdmin)
    
    return admin