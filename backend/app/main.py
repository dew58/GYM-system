"""
FastAPI application entry point.
Mounts all routers, configures CORS, and seeds the initial admin user.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.core.database import engine, async_session, Base
from app.core.security import hash_password

# Import all models so they are registered with Base.metadata
from app.models import user, member, subscription, payment, trainer, attendance, expense, inventory  # noqa

from app.api.v1 import auth, members, subscriptions, payments, trainers
from app.api.v1 import attendance as attendance_router
from app.api.v1 import expenses, inventory as inventory_router, dashboard, reports

logger = logging.getLogger("gym")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


async def seed_admin():
    """Create the initial super admin user if it does not exist."""
    from sqlalchemy import select
    from app.models.user import User, UserRole

    async with async_session() as session:
        result = await session.execute(select(User).where(User.username == settings.FIRST_ADMIN_USERNAME))
        if not result.scalar_one_or_none():
            admin = User(
                username=settings.FIRST_ADMIN_USERNAME,
                email=settings.FIRST_ADMIN_EMAIL,
                hashed_password=hash_password(settings.FIRST_ADMIN_PASSWORD),
                full_name="System Administrator",
                role=UserRole.SUPER_ADMIN,
            )
            session.add(admin)
            await session.commit()
            logger.info("✅ Default admin user created: %s", settings.FIRST_ADMIN_USERNAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables & seed admin. Shutdown: dispose engine."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_admin()
    logger.info("🏋️ Gym Management System started")
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-ready Gym Management System for Egyptian gyms",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploads
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Mount all API routers under /api/v1
PREFIX = "/api/v1"
app.include_router(auth.router, prefix=PREFIX)
app.include_router(members.router, prefix=PREFIX)
app.include_router(subscriptions.router, prefix=PREFIX)
app.include_router(payments.router, prefix=PREFIX)
app.include_router(trainers.router, prefix=PREFIX)
app.include_router(attendance_router.router, prefix=PREFIX)
app.include_router(expenses.router, prefix=PREFIX)
app.include_router(inventory_router.router, prefix=PREFIX)
app.include_router(dashboard.router, prefix=PREFIX)
app.include_router(reports.router, prefix=PREFIX)


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}
