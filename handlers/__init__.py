from .common import router as common_router
from .catalog import router as catalog_router
from .admin import router as admin_router
from .suggest import router as suggest_router


all_routers = [common_router, catalog_router, admin_router, suggest_router]
