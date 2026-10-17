from fastapi import APIRouter, Query, HTTPException
from ..modeles.models import Media
from sqlmodel import select
from ..database import get_db 
from typing import Annotated
from ..redis_client import RedisDep, cache_get, cache_set, cache_delete, cache_delete_pattern

from ..modeles.models import Utilisateur
from fastapi import Depends
from ..securites.securite import get_current_utilisateur


from ..modeles.models import Utilisateur

from ..schemas import MediaCreate, MediaPublic, MediaUpdate, MediaPublicAvecUtilisateur




media_router = APIRouter(
    prefix="/medias",
    tags=["medias"]
)


@media_router.post("/", response_model=MediaPublic, status_code=201)
async def post_media(data: MediaCreate, db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
, redis: RedisDep):
    utilisateur = db.get(Utilisateur, data.utilisateur_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    payload = data.model_dump(exclude=set())
    payload["utilisateur_id"] = current_user.id

    media_db = Media(**payload)

    db.add(media_db)
    db.commit()
    db.refresh(media_db)
    await cache_delete_pattern(redis, "medias:list:" + str(current_user.id) + ":*")

    return media_db


@media_router.get("/", response_model=list[MediaPublic])
async def get_medias(db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
, redis: RedisDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    cle = "medias:list:" + str(current_user.id) + ":" + str(offset) + ":" + str(limit)
    en_cache = await cache_get(redis, cle)
    if en_cache is not None:
        return en_cache

    query = select(Media)
    query = query.where(Media.utilisateur_id == current_user.id)
    
    medias = db.exec(query.offset(offset).limit(limit)).all()
    data = [MediaPublic.model_validate(x).model_dump(mode="json") for x in medias]
    await cache_set(redis, cle, data, 60)
    return data



@media_router.get("/{media_id}", response_model=MediaPublic)
async def get_media(media_id: int, db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
, redis: RedisDep):
    cle = "media:" + str(current_user.id) + ":" + str(media_id)
    en_cache = await cache_get(redis, cle)
    if en_cache is not None:
        return en_cache

    media = db.get(Media, media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    if media.utilisateur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    data = MediaPublic.model_validate(media).model_dump(mode="json")
    await cache_set(redis, cle, data, 60)
    return data



@media_router.put("/{media_id}", response_model=MediaPublic)
async def put_media(media_id: int, data: MediaUpdate, db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
, redis: RedisDep):
    media_db = db.get(Media, media_id)
    if not media_db:
        raise HTTPException(status_code=404, detail="Media not found")
    # exclude_unset=True : ne modifie que les champs envoyés (FK scalaires 1-1/1-N incluses)
    if media_db.utilisateur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    payload = data.model_dump(exclude_unset=True)
    media_db.sqlmodel_update(payload)
    db.add(media_db)
    db.commit()
    db.refresh(media_db)
    await cache_delete(redis, "media:" + str(current_user.id) + ":" + str(media_id))
    await cache_delete_pattern(redis, "medias:list:" + str(current_user.id) + ":*")

    return media_db


@media_router.delete("/{media_id}")
async def delete_media(media_id: int, db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
, redis: RedisDep):
    media = db.get(Media, media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    if media.utilisateur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    db.delete(media)
    db.commit()
    await cache_delete(redis, "media:" + str(current_user.id) + ":" + str(media_id))
    await cache_delete_pattern(redis, "medias:list:" + str(current_user.id) + ":*")

    return {"ok": True}



@media_router.get("/{media_id}/utilisateur", response_model=MediaPublicAvecUtilisateur)
async def get_media_avec_utilisateur(media_id: int, db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
):
    media = db.get(Media, media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media introuvable")
    if media.utilisateur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    return media



