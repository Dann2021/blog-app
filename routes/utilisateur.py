from fastapi import APIRouter, Query, HTTPException
from ..modeles.models import Utilisateur
from sqlmodel import select
from ..database import get_db 
from typing import Annotated



from ..securites.securite import hasher_password


from ..schemas import UtilisateurCreate, UtilisateurPublic, UtilisateurUpdate, UtilisateurPublicAvecArticles, UtilisateurPublicAvecCommentaires, UtilisateurPublicAvecMedias




utilisateur_router = APIRouter(
    prefix="/utilisateurs",
    tags=["utilisateurs"]
)


@utilisateur_router.post("/", response_model=UtilisateurPublic, status_code=201)
async def post_utilisateur(data: UtilisateurCreate, db: get_db):

    payload = data.model_dump(exclude=set())
    payload["password"] = hasher_password(payload["password"])

    utilisateur_db = Utilisateur(**payload)

    db.add(utilisateur_db)
    db.commit()
    db.refresh(utilisateur_db)

    return utilisateur_db


@utilisateur_router.get("/", response_model=list[UtilisateurPublic])
async def get_utilisateurs(db: get_db, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):

    query = select(Utilisateur)
    
    utilisateurs = db.exec(query.offset(offset).limit(limit)).all()
    return utilisateurs



@utilisateur_router.get("/{utilisateur_id}", response_model=UtilisateurPublic)
async def get_utilisateur(utilisateur_id: int, db: get_db):

    utilisateur = db.get(Utilisateur, utilisateur_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur not found")

    return utilisateur



@utilisateur_router.put("/{utilisateur_id}", response_model=UtilisateurPublic)
async def put_utilisateur(utilisateur_id: int, data: UtilisateurUpdate, db: get_db):
    utilisateur_db = db.get(Utilisateur, utilisateur_id)
    if not utilisateur_db:
        raise HTTPException(status_code=404, detail="Utilisateur not found")
    # exclude_unset=True : ne modifie que les champs envoyés (FK scalaires 1-1/1-N incluses)

    payload = data.model_dump(exclude_unset=True)
    utilisateur_db.sqlmodel_update(payload)
    db.add(utilisateur_db)
    db.commit()
    db.refresh(utilisateur_db)

    return utilisateur_db


@utilisateur_router.delete("/{utilisateur_id}")
async def delete_utilisateur(utilisateur_id: int, db: get_db):
    utilisateur = db.get(Utilisateur, utilisateur_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur not found")

    db.delete(utilisateur)
    db.commit()

    return {"ok": True}



@utilisateur_router.get("/{utilisateur_id}/articles", response_model=UtilisateurPublicAvecArticles)
async def get_utilisateur_avec_articles(utilisateur_id: int, db: get_db):
    utilisateur = db.get(Utilisateur, utilisateur_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
 
    return utilisateur

@utilisateur_router.get("/{utilisateur_id}/commentaires", response_model=UtilisateurPublicAvecCommentaires)
async def get_utilisateur_avec_commentaires(utilisateur_id: int, db: get_db):
    utilisateur = db.get(Utilisateur, utilisateur_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
 
    return utilisateur

@utilisateur_router.get("/{utilisateur_id}/medias", response_model=UtilisateurPublicAvecMedias)
async def get_utilisateur_avec_medias(utilisateur_id: int, db: get_db):
    utilisateur = db.get(Utilisateur, utilisateur_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
 
    return utilisateur



