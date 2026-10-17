from fastapi import APIRouter, Query, HTTPException
from ..modeles.models import Contact
from sqlmodel import select
from ..database import get_db 
from typing import Annotated
from ..redis_client import RedisDep, cache_get, cache_set, cache_delete, cache_delete_pattern




from ..schemas import ContactCreate, ContactPublic, ContactUpdate




contact_router = APIRouter(
    prefix="/contacts",
    tags=["contacts"]
)


@contact_router.post("/", response_model=ContactPublic, status_code=201)
async def post_contact(data: ContactCreate, db: get_db, redis: RedisDep):

    payload = data.model_dump(exclude=set())

    contact_db = Contact(**payload)

    db.add(contact_db)
    db.commit()
    db.refresh(contact_db)
    await cache_delete_pattern(redis, "contacts:list:" + "pub" + ":*")

    return contact_db


@contact_router.get("/", response_model=list[ContactPublic])
async def get_contacts(db: get_db, redis: RedisDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    cle = "contacts:list:" + "pub" + ":" + str(offset) + ":" + str(limit)
    en_cache = await cache_get(redis, cle)
    if en_cache is not None:
        return en_cache

    query = select(Contact)
    
    contacts = db.exec(query.offset(offset).limit(limit)).all()
    data = [ContactPublic.model_validate(x).model_dump(mode="json") for x in contacts]
    await cache_set(redis, cle, data, 60)
    return data



@contact_router.get("/{contact_id}", response_model=ContactPublic)
async def get_contact(contact_id: int, db: get_db, redis: RedisDep):
    cle = "contact:" + "pub" + ":" + str(contact_id)
    en_cache = await cache_get(redis, cle)
    if en_cache is not None:
        return en_cache

    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    data = ContactPublic.model_validate(contact).model_dump(mode="json")
    await cache_set(redis, cle, data, 60)
    return data



@contact_router.put("/{contact_id}", response_model=ContactPublic)
async def put_contact(contact_id: int, data: ContactUpdate, db: get_db, redis: RedisDep):
    contact_db = db.get(Contact, contact_id)
    if not contact_db:
        raise HTTPException(status_code=404, detail="Contact not found")
    # exclude_unset=True : ne modifie que les champs envoyés (FK scalaires 1-1/1-N incluses)

    payload = data.model_dump(exclude_unset=True)
    contact_db.sqlmodel_update(payload)
    db.add(contact_db)
    db.commit()
    db.refresh(contact_db)
    await cache_delete(redis, "contact:" + "pub" + ":" + str(contact_id))
    await cache_delete_pattern(redis, "contacts:list:" + "pub" + ":*")

    return contact_db


@contact_router.delete("/{contact_id}")
async def delete_contact(contact_id: int, db: get_db, redis: RedisDep):
    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()
    await cache_delete(redis, "contact:" + "pub" + ":" + str(contact_id))
    await cache_delete_pattern(redis, "contacts:list:" + "pub" + ":*")

    return {"ok": True}





