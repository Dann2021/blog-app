from fastapi import APIRouter, Query, HTTPException
from ..modeles.models import Abonne
from sqlmodel import select
from ..database import get_db 
from typing import Annotated
from ..redis_client import RedisDep, cache_get, cache_set, cache_delete, cache_delete_pattern




from ..schemas import AbonneCreate, AbonnePublic, AbonneUpdate




abonne_router = APIRouter(
    prefix="/abonnes",
    tags=["abonnes"]
)


@abonne_router.post("/", response_model=AbonnePublic, status_code=201)
async def post_abonne(data: AbonneCreate, db: get_db, redis: RedisDep):

    payload = data.model_dump(exclude=set())

    abonne_db = Abonne(**payload)

    db.add(abonne_db)
    db.commit()
    db.refresh(abonne_db)
    await cache_delete_pattern(redis, "abonnes:list:" + "pub" + ":*")

    return abonne_db


@abonne_router.get("/", response_model=list[AbonnePublic])
async def get_abonnes(db: get_db, redis: RedisDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    cle = "abonnes:list:" + "pub" + ":" + str(offset) + ":" + str(limit)
    en_cache = await cache_get(redis, cle)
    if en_cache is not None:
        return en_cache

    query = select(Abonne)
    
    abonnes = db.exec(query.offset(offset).limit(limit)).all()
    data = [AbonnePublic.model_validate(x).model_dump(mode="json") for x in abonnes]
    await cache_set(redis, cle, data, 60)
    return data



@abonne_router.get("/{abonne_id}", response_model=AbonnePublic)
async def get_abonne(abonne_id: int, db: get_db, redis: RedisDep):
    cle = "abonne:" + "pub" + ":" + str(abonne_id)
    en_cache = await cache_get(redis, cle)
    if en_cache is not None:
        return en_cache

    abonne = db.get(Abonne, abonne_id)
    if not abonne:
        raise HTTPException(status_code=404, detail="Abonne not found")

    data = AbonnePublic.model_validate(abonne).model_dump(mode="json")
    await cache_set(redis, cle, data, 60)
    return data



@abonne_router.put("/{abonne_id}", response_model=AbonnePublic)
async def put_abonne(abonne_id: int, data: AbonneUpdate, db: get_db, redis: RedisDep):
    abonne_db = db.get(Abonne, abonne_id)
    if not abonne_db:
        raise HTTPException(status_code=404, detail="Abonne not found")
    # exclude_unset=True : ne modifie que les champs envoyés (FK scalaires 1-1/1-N incluses)

    payload = data.model_dump(exclude_unset=True)
    abonne_db.sqlmodel_update(payload)
    db.add(abonne_db)
    db.commit()
    db.refresh(abonne_db)
    await cache_delete(redis, "abonne:" + "pub" + ":" + str(abonne_id))
    await cache_delete_pattern(redis, "abonnes:list:" + "pub" + ":*")

    return abonne_db


@abonne_router.delete("/{abonne_id}")
async def delete_abonne(abonne_id: int, db: get_db, redis: RedisDep):
    abonne = db.get(Abonne, abonne_id)
    if not abonne:
        raise HTTPException(status_code=404, detail="Abonne not found")

    db.delete(abonne)
    db.commit()
    await cache_delete(redis, "abonne:" + "pub" + ":" + str(abonne_id))
    await cache_delete_pattern(redis, "abonnes:list:" + "pub" + ":*")

    return {"ok": True}





