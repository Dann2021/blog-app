from fastapi import APIRouter, Query, HTTPException
from ..modeles.models import Page
from sqlmodel import select
from ..database import get_db 
from typing import Annotated
from ..redis_client import RedisDep, cache_get, cache_set, cache_delete, cache_delete_pattern




from ..schemas import PageCreate, PagePublic, PageUpdate




page_router = APIRouter(
    prefix="/pages",
    tags=["pages"]
)


@page_router.post("/", response_model=PagePublic, status_code=201)
async def post_page(data: PageCreate, db: get_db, redis: RedisDep):

    payload = data.model_dump(exclude=set())

    page_db = Page(**payload)

    db.add(page_db)
    db.commit()
    db.refresh(page_db)
    await cache_delete_pattern(redis, "pages:list:" + "pub" + ":*")

    return page_db


@page_router.get("/", response_model=list[PagePublic])
async def get_pages(db: get_db, redis: RedisDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    cle = "pages:list:" + "pub" + ":" + str(offset) + ":" + str(limit)
    en_cache = await cache_get(redis, cle)
    if en_cache is not None:
        return en_cache

    query = select(Page)
    
    pages = db.exec(query.offset(offset).limit(limit)).all()
    data = [PagePublic.model_validate(x).model_dump(mode="json") for x in pages]
    await cache_set(redis, cle, data, 60)
    return data



@page_router.get("/{page_id}", response_model=PagePublic)
async def get_page(page_id: int, db: get_db, redis: RedisDep):
    cle = "page:" + "pub" + ":" + str(page_id)
    en_cache = await cache_get(redis, cle)
    if en_cache is not None:
        return en_cache

    page = db.get(Page, page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    data = PagePublic.model_validate(page).model_dump(mode="json")
    await cache_set(redis, cle, data, 60)
    return data



@page_router.put("/{page_id}", response_model=PagePublic)
async def put_page(page_id: int, data: PageUpdate, db: get_db, redis: RedisDep):
    page_db = db.get(Page, page_id)
    if not page_db:
        raise HTTPException(status_code=404, detail="Page not found")
    # exclude_unset=True : ne modifie que les champs envoyés (FK scalaires 1-1/1-N incluses)

    payload = data.model_dump(exclude_unset=True)
    page_db.sqlmodel_update(payload)
    db.add(page_db)
    db.commit()
    db.refresh(page_db)
    await cache_delete(redis, "page:" + "pub" + ":" + str(page_id))
    await cache_delete_pattern(redis, "pages:list:" + "pub" + ":*")

    return page_db


@page_router.delete("/{page_id}")
async def delete_page(page_id: int, db: get_db, redis: RedisDep):
    page = db.get(Page, page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    db.delete(page)
    db.commit()
    await cache_delete(redis, "page:" + "pub" + ":" + str(page_id))
    await cache_delete_pattern(redis, "pages:list:" + "pub" + ":*")

    return {"ok": True}





