# routers/__init__.py
from .auth import router as auth_router
from .transactions import router as transactions_router  
from .communes import router as communes_router
from .stats import router as stats_router
from .market import router as market_router
from .users import router as users_router

__all__ = [
    "auth_router",
    "transactions_router", 
    "communes_router",
    "stats_router",
    "market_router",
    "users_router"
]
