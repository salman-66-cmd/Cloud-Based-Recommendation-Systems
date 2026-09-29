import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.routers import (
    auth, categories, items, recommendations, interactions, ratings, preferences, search, admin
)
from app.recommendation.engine import recommendation_engine
from app.utils.cache import cache

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist
    logger.info("Initializing database schemas...")
    Base.metadata.create_all(bind=engine)

    # Initialize TF-IDF matrix
    db = SessionLocal()
    try:
        recommendation_engine.build_content_model(db)
        logger.info("Recommendation engine TF-IDF vector space precomputed.")
    except Exception as e:
        logger.warning(f"Error during recommendation engine precompute: {e}")
    finally:
        db.close()

    yield

    logger.info("Shutting down application...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-style Cloud-Based Recommendation System Web API with Hybrid, Collaborative, and Content-Based Filtering",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(categories.router, prefix=settings.API_V1_STR)
app.include_router(items.router, prefix=settings.API_V1_STR)
app.include_router(recommendations.router, prefix=settings.API_V1_STR)
app.include_router(interactions.router, prefix=settings.API_V1_STR)
app.include_router(ratings.router, prefix=settings.API_V1_STR)
app.include_router(preferences.router, prefix=settings.API_V1_STR)
app.include_router(search.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health Monitoring"])
@app.get("/api/health", tags=["Health Monitoring"])
def health_check():
    db_status = "disconnected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    redis_status = "connected" if cache.redis_available else "fallback_in_memory"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "redis": redis_status,
        "version": settings.VERSION,
        "service": settings.PROJECT_NAME
    }

@app.get("/", tags=["Root"])
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }
