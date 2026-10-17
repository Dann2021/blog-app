from fastapi import APIRouter, Query, HTTPException
from ..modeles.models import Commentaire
from sqlmodel import select
from ..database import get_db 
from typing import Annotated
from ..redis_client import RedisDep, cache_get, cache_set, cache_delete, cache_delete_pattern

from ..modeles.models import Utilisateur
from fastapi import Depends
from ..securites.securite import get_current_utilisateur


from ..modeles.models import Utilisateur
from ..modeles.models import Article

from ..schemas import CommentaireCreate, CommentairePublic, CommentaireUpdate, CommentairePublicAvecUtilisateur, CommentairePublicAvecArticle




commentaire_router = APIRouter(
    prefix="/commentaires",
    tags=["commentaires"]
)


@commentaire_router.post("/", response_model=CommentairePublic, status_code=201)
async def post_commentaire(data: CommentaireCreate, db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
, redis: RedisDep):
    utilisateur = db.get(Utilisateur, data.utilisateur_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    article = db.get(Article, data.article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article introuvable")

    payload = data.model_dump(exclude=set())
    payload["utilisateur_id"] = current_user.id

    commentaire_db = Commentaire(**payload)

    db.add(commentaire_db)
    db.commit()
    db.refresh(commentaire_db)
    await cache_delete_pattern(redis, "commentaires:list:" + str(current_user.id) + ":*")

    return commentaire_db


@commentaire_router.get("/", response_model=list[CommentairePublic])
async def get_commentaires(db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
, redis: RedisDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    cle = "commentaires:list:" + str(current_user.id) + ":" + str(offset) + ":" + str(limit)
    en_cache = await cache_get(redis, cle)
    if en_cache is not None:
        return en_cache

    query = select(Commentaire)
    query = query.where(Commentaire.utilisateur_id == current_user.id)
    
    commentaires = db.exec(query.offset(offset).limit(limit)).all()
    data = [CommentairePublic.model_validate(x).model_dump(mode="json") for x in commentaires]
    await cache_set(redis, cle, data, 60)
    return data



@commentaire_router.get("/{commentaire_id}", response_model=CommentairePublic)
async def get_commentaire(commentaire_id: int, db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
, redis: RedisDep):
    cle = "commentaire:" + str(current_user.id) + ":" + str(commentaire_id)
    en_cache = await cache_get(redis, cle)
    if en_cache is not None:
        return en_cache

    commentaire = db.get(Commentaire, commentaire_id)
    if not commentaire:
        raise HTTPException(status_code=404, detail="Commentaire not found")
    if commentaire.utilisateur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    data = CommentairePublic.model_validate(commentaire).model_dump(mode="json")
    await cache_set(redis, cle, data, 60)
    return data



@commentaire_router.put("/{commentaire_id}", response_model=CommentairePublic)
async def put_commentaire(commentaire_id: int, data: CommentaireUpdate, db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
, redis: RedisDep):
    commentaire_db = db.get(Commentaire, commentaire_id)
    if not commentaire_db:
        raise HTTPException(status_code=404, detail="Commentaire not found")
    # exclude_unset=True : ne modifie que les champs envoyés (FK scalaires 1-1/1-N incluses)
    if commentaire_db.utilisateur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    payload = data.model_dump(exclude_unset=True)
    commentaire_db.sqlmodel_update(payload)
    db.add(commentaire_db)
    db.commit()
    db.refresh(commentaire_db)
    await cache_delete(redis, "commentaire:" + str(current_user.id) + ":" + str(commentaire_id))
    await cache_delete_pattern(redis, "commentaires:list:" + str(current_user.id) + ":*")

    return commentaire_db


@commentaire_router.delete("/{commentaire_id}")
async def delete_commentaire(commentaire_id: int, db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
, redis: RedisDep):
    commentaire = db.get(Commentaire, commentaire_id)
    if not commentaire:
        raise HTTPException(status_code=404, detail="Commentaire not found")
    if commentaire.utilisateur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    db.delete(commentaire)
    db.commit()
    await cache_delete(redis, "commentaire:" + str(current_user.id) + ":" + str(commentaire_id))
    await cache_delete_pattern(redis, "commentaires:list:" + str(current_user.id) + ":*")

    return {"ok": True}



@commentaire_router.get("/{commentaire_id}/utilisateur", response_model=CommentairePublicAvecUtilisateur)
async def get_commentaire_avec_utilisateur(commentaire_id: int, db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
):
    commentaire = db.get(Commentaire, commentaire_id)
    if not commentaire:
        raise HTTPException(status_code=404, detail="Commentaire introuvable")
    if commentaire.utilisateur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    return commentaire

@commentaire_router.get("/{commentaire_id}/article", response_model=CommentairePublicAvecArticle)
async def get_commentaire_avec_article(commentaire_id: int, db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
):
    commentaire = db.get(Commentaire, commentaire_id)
    if not commentaire:
        raise HTTPException(status_code=404, detail="Commentaire introuvable")
    if commentaire.utilisateur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    return commentaire



