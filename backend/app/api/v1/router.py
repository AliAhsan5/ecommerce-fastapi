from fastapi import APIRouter

from app.api.v1.addresses import router as addresses_router
from app.api.v1.admin import router as admin_router
from app.api.v1.auth import router as auth_router
from app.api.v1.brands import router as brands_router
from app.api.v1.categories import router as categories_router
from app.api.v1.products import router as products_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.variants import router as variants_router
from app.api.v1.cart import router as cart_router
from app.api.v1.orders import router as orders_router
from app.api.v1.admin_orders import (
    router as admin_orders_router,
)

from app.api.v1.audit_logs import (
    router as audit_logs_router,
)

from app.api.v1.admin_catalog import (
    router as admin_catalog_router,
)

from app.api.v1.admin_inventory import (
    router as admin_inventory_router,
)

from app.api.v1.admin_dashboard import (
    router as admin_dashboard_router,
)

from app.api.v1.chat import (
    router as chat_router,
)


api_router = APIRouter()


api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"],
)


api_router.include_router(
    addresses_router,
    prefix="/addresses",
    tags=["Addresses"],
)


api_router.include_router(
    categories_router,
    prefix="/categories",
    tags=["Categories"],
)


api_router.include_router(
    brands_router,
    prefix="/brands",
    tags=["Brands"],
)


api_router.include_router(
    products_router,
    prefix="/products",
    tags=["Products"],
)


api_router.include_router(
    admin_router,
    prefix="/admin",
    tags=["Admin"],
)


api_router.include_router(
    variants_router,
    prefix="/variants",
    tags=["Product Variants"],
)


api_router.include_router(
    inventory_router,
    prefix="/inventory",
    tags=["Inventory"],
)


api_router.include_router(
    cart_router,
    prefix="/cart",
    tags=["Shopping Cart"],
)


api_router.include_router(
    orders_router,
    prefix="/orders",
    tags=["Orders"],
)


api_router.include_router(
    admin_orders_router,
    prefix="/admin/orders",
    tags=["Admin Orders"],
)


api_router.include_router(
    audit_logs_router,
    prefix="/admin/audit-logs",
    tags=["Admin Audit Logs"],
)


api_router.include_router(
    admin_catalog_router,
    prefix="/admin",
    tags=["Admin Catalog"],
)


api_router.include_router(
    admin_inventory_router,
    prefix="/admin/inventory",
    tags=["Admin Inventory"],
)


api_router.include_router(
    admin_dashboard_router,
    prefix="/admin/dashboard",
    tags=["Admin Dashboard"],
)


api_router.include_router(
    chat_router,
    prefix="/chat",
    tags=["AI Chat"],
)


@api_router.get("/test")
def test_api():
    return {
        "message": "API v1 is working"
    }