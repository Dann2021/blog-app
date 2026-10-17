from fastapi import APIRouter, Query, HTTPException
from ..modeles.models import Categorie
from sqlmodel import select
from ..database import get_db 
from typing import Annotated
from ..redis_client import RedisDep, cache_get, cache_set, cache_delete, cache_delete_pattern




from ..schemas import CategorieCreate, CategoriePublic, CategorieUpdate, CategoriePublicAvecArticles




categorie_router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)


@categorie_router.post("/", response_model=CategoriePublic, status_code=201)
async def post_categorie(data: CategorieCreate, db: get_db, redis: RedisDep):

    payload = data.model_dump(exclude=set())

    categorie_db = Categorie(**payload)

    db.add(categorie_db)
    db.commit()
    db.refresh(categorie_db)
    await cache_delete_pattern(redis, "categories:list:" + "pub" + ":*")

    return categorie_db


@categorie_router.get("/", response_model=list[CategoriePublic])
async def get_categories(db: get_db, redis: RedisDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    cle = "categories:list:" + "pub" + ":" + str(offset) + ":" + str(limit)
    en_cache = await cache_get(redis, cle)
    if en_cache is not None:
        return en_cache

    query = select(Categorie)
    
    categories = db.exec(query.offset(offset).limit(limit)).all()
    data = [CategoriePublic.model_validate(x).model_dump(mode="json") for x in categories]
    await cache_set(redis, cle, data, 60)
    return data



@categorie_router.get("/{categorie_id}", response_model=CategoriePublic)
async def get_categorie(categorie_id: int, db: get_db, redis: RedisDep):
    cle = "categorie:" + "pub" + ":" + str(categorie_id)
    en_cache = await cache_get(redis, cle)
    if en_cache is not None:
        return en_cache

    categorie = db.get(Categorie, categorie_id)
    if not categorie:
        raise HTTPException(status_code=404, detail="Categorie not found")

    data = CategoriePublic.model_validate(categorie).model_dump(mode="json")
    await cache_set(redis, cle, data, 60)
    return data



@categorie_router.put("/{categorie_id}", response_model=CategoriePublic)
async def put_categorie(categorie_id: int, data: CategorieUpdate, db: get_db, redis: RedisDep):
    categorie_db = db.get(Categorie, categorie_id)
    if not categorie_db:
        raise HTTPException(status_code=404, detail="Categorie not found")
    # exclude_unset=True : ne modifie que les champs envoyés (FK scalaires 1-1/1-N incluses)

    payload = data.model_dump(exclude_unset=True)
    categorie_db.sqlmodel_update(payload)
    db.add(categorie_db)
    db.commit()
    db.refresh(categorie_db)
    await cache_delete(redis, "categorie:" + "pub" + ":" + str(categorie_id))
    await cache_delete_pattern(redis, "categories:list:" + "pub" + ":*")

    return categorie_db


@categorie_router.delete("/{categorie_id}")
async def delete_categorie(categorie_id: int, db: get_db, redis: RedisDep):
    categorie = db.get(Categorie, categorie_id)
    if not categorie:
        raise HTTPException(status_code=404, detail="Categorie not found")

    db.delete(categorie)
    db.commit()
    await cache_delete(redis, "categorie:" + "pub" + ":" + str(categorie_id))
    await cache_delete_pattern(redis, "categories:list:" + "pub" + ":*")

    return {"ok": True}



@categorie_router.get("/{categorie_id}/articles", response_model=CategoriePublicAvecArticles)
async def get_categorie_avec_articles(categorie_id: int, db: get_db):
    categorie = db.get(Categorie, categorie_id)
    if not categorie:
        raise HTTPException(status_code=404, detail="Categorie introuvable")
 
    return categorie



