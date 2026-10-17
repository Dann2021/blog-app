from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from .routes.auth import auth_router
from .database import create_db_and_tables

from .redis_client import create_redis

from fastapi.middleware.cors import CORSMiddleware

from .routes.utilisateur import utilisateur_router
from .routes.categorie import categorie_router
from .routes.tag import tag_router
from .routes.article import article_router
from .routes.commentaire import commentaire_router
from .routes.media import media_router
from .routes.page import page_router
from .routes.abonne import abonne_router
from .routes.contact import contact_router
    



@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    app.state.redis = await create_redis()
    yield
    await app.state.redis.aclose()


# Creation de l'instance app 
app = FastAPI(lifespan=lifespan, title="blog-app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_credentials=False,
    allow_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allow_headers=['*'],
)


app.include_router(auth_router)
app.include_router(utilisateur_router)
app.include_router(categorie_router)
app.include_router(tag_router)
app.include_router(article_router)
app.include_router(commentaire_router)
app.include_router(media_router)
app.include_router(page_router)
app.include_router(abonne_router)
app.include_router(contact_router)



@app.get("/health",tags=["health"])
async def check_status_api():
    return JSONResponse({"status": "ok "}, status_code=200)


