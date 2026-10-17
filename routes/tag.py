from fastapi import APIRouter, Query, HTTPException
from ..modeles.models import Tag
from sqlmodel import select
from ..database import get_db 
from typing import Annotated
from ..redis_client import RedisDep, cache_get, cache_set, cache_delete, cache_delete_pattern



from ..modeles.models import Article

from ..schemas import TagCreate, TagPublic, TagUpdate, TagPublicAvecArticle




tag_router = APIRouter(
    prefix="/tags",
    tags=["tags"]
)


@tag_router.post("/", response_model=TagPublic, status_code=201)
async def post_tag(data: TagCreate, db: get_db, redis: RedisDep):

    payload = data.model_dump(exclude={"article_ids"})

    tag_db = Tag(**payload)
    for article_id in data.article_ids:
        article = db.get(Article, article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article introuvable")
        tag_db.articles.append(article)

    db.add(tag_db)
    db.commit()
    db.refresh(tag_db)
    await cache_delete_pattern(redis, "tags:list:" + "pub" + ":*")

    return tag_db


@tag_router.get("/", response_model=list[TagPublic])
async def get_tags(db: get_db, redis: RedisDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    cle = "tags:list:" + "pub" + ":" + str(offset) + ":" + str(limit)
    en_cache = await cache_get(redis, cle)
    if en_cache is not None:
        return en_cache

    query = select(Tag)
    
    tags = db.exec(query.offset(offset).limit(limit)).all()
    data = [TagPublic.model_validate(x).model_dump(mode="json") for x in tags]
    await cache_set(redis, cle, data, 60)
    return data



@tag_router.get("/{tag_id}", response_model=TagPublic)
async def get_tag(tag_id: int, db: get_db, redis: RedisDep):
    cle = "tag:" + "pub" + ":" + str(tag_id)
    en_cache = await cache_get(redis, cle)
    if en_cache is not None:
        return en_cache

    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    data = TagPublic.model_validate(tag).model_dump(mode="json")
    await cache_set(redis, cle, data, 60)
    return data



@tag_router.put("/{tag_id}", response_model=TagPublic)
async def put_tag(tag_id: int, data: TagUpdate, db: get_db, redis: RedisDep):
    tag_db = db.get(Tag, tag_id)
    if not tag_db:
        raise HTTPException(status_code=404, detail="Tag not found")
    # exclude_unset=True : ne modifie que les champs envoyés (FK scalaires 1-1/1-N incluses)

    payload = data.model_dump(exclude_unset=True)
    tag_db.sqlmodel_update(payload)
    db.add(tag_db)
    db.commit()
    db.refresh(tag_db)
    await cache_delete(redis, "tag:" + "pub" + ":" + str(tag_id))
    await cache_delete_pattern(redis, "tags:list:" + "pub" + ":*")

    return tag_db


@tag_router.delete("/{tag_id}")
async def delete_tag(tag_id: int, db: get_db, redis: RedisDep):
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    db.delete(tag)
    db.commit()
    await cache_delete(redis, "tag:" + "pub" + ":" + str(tag_id))
    await cache_delete_pattern(redis, "tags:list:" + "pub" + ":*")

    return {"ok": True}



@tag_router.get("/{tag_id}/article", response_model=TagPublicAvecArticle)
async def get_tag_avec_article(tag_id: int, db: get_db):
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag introuvable")

    return tag




@tag_router.post("/{tag_id}/article/{article_id}", response_model=TagPublicAvecArticle)
async def ajouter_article_a_tag(tag_id: int, article_id: int, db: get_db):
    tag = db.get(Tag, tag_id)
    article = db.get(Article, article_id)
    if not tag or not article:
        raise HTTPException(status_code=404, detail="Tag ou Article introuvable")
 
    if article not in tag.articles:
        tag.articles.append(article)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag

@tag_router.delete("/{tag_id}/article/{article_id}", response_model=TagPublicAvecArticle)
async def retirer_article_de_tag(tag_id: int, article_id: int, db: get_db):
    tag = db.get(Tag, tag_id)
    article = db.get(Article, article_id)
    if not tag or not article:
        raise HTTPException(status_code=404, detail="Tag ou Article introuvable")
 
    if article in tag.articles:
        tag.articles.remove(article)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag
