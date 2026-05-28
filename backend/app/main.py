from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Music of the World API")

# =====================
# CORS
# =====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "https://my-diplom-front.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================
# ROUTES (SAFE IMPORT)
# =====================

try:
    from app.routers.auth import router as auth_router
    from app.routers.users import router as users_router
    from app.routers.articles import router as articles_router
    from app.routers.comments import router as comments_router
    from app.routers.reactions import router as reactions_router
    from app.routers.admin import router as admin_router
    from app.routers.contact import router as contact_router
    from app.routers.countries import router as countries_router
    from app.routers.cultures import router as cultures_router
    from app.routers.genres import router as genres_router
    from app.routers.instruments import router as instruments_router
    from app.routers.music import router as music_router

    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(articles_router)
    app.include_router(comments_router)
    app.include_router(reactions_router)
    app.include_router(admin_router)
    app.include_router(contact_router)
    app.include_router(countries_router)
    app.include_router(cultures_router)
    app.include_router(genres_router)
    app.include_router(instruments_router)
    app.include_router(music_router)

except Exception as e:
    print("Router import error:", e)

# =====================
# DB INIT (SAFE)
# =====================

def init_db():
    try:
        from app.core.database import Base, engine
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print("DB init error:", e)

@app.on_event("startup")
def startup():
    init_db()

# =====================
# TEST ROUTES
# =====================

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}