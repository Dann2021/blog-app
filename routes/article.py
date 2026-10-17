from fastapi import APIRouter, Query, HTTPException
from ..modeles.models import Article
from sqlmodel import select
from ..database import get_db 
from typing import Annotated
from ..redis_client import RedisDep, cache_get, cache_set, cache_delete, cache_delete_pattern

from ..modeles.models import Utilisateur
from fastapi import Depends
from ..securites.securite import get_current_utilisateur


from ..modeles.models import Utilisateur
from ..modeles.models import Categorie
from ..modeles.models import Tag

from ..schemas import ArticleCreate, ArticlePublic, ArticleUpdate, ArticlePublicAvecCommentaires, ArticlePublicAvecTags, ArticlePublicAvecUtilisateur, ArticlePublicAvecCategorie




article_router = APIRouter(
    prefix="/articles",
    tags=["articles"]
)


@article_router.post("/", response_model=ArticlePublic, status_code=201)
async def post_article(data: ArticleCreate, db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
, redis: RedisDep):
    utilisateur = db.get(Utilisateur, data.utilisateur_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    categorie = db.get(Categorie, data.categorie_id)
    if not categorie:
        raise HTTPException(status_code=404, detail="Categorie introuvable")

    payload = data.model_dump(exclude={"tags_ids"})
    payload["utilisateur_id"] = current_user.id

    article_db = Article(**payload)
    for tag_id in data.tags_ids:
        tag = db.get(Tag, tag_id)
        if not tag:
            raise HTTPException(status_code=404, detail="Tag introuvable")
        article_db.tags.append(tag)

    db.add(article_db)
    db.commit()
    db.refresh(article_db)
    await cache_delete_pattern(redis, "articles:list:" + str(current_user.id) + ":*")

    return article_db


@article_router.get("/", response_model=list[ArticlePublic])
async def get_articles(db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
, redis: RedisDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    cle = "articles:list:" + str(current_user.id) + ":" + str(offset) + ":" + str(limit)
    en_cache = await cache_get(redis, cle)
    if en_cache is not None:
        return en_cache

    query = select(Article)
    query = query.where(Article.utilisateur_id == current_user.id)
    
    articles = db.exec(query.offset(offset).limit(limit)).all()
    data = [ArticlePublic.model_validate(x).model_dump(mode="json") for x in articles]
    await cache_set(redis, cle, data, 60)
    return data



@article_router.get("/{article_id}", response_model=ArticlePublic)
async def get_article(article_id: int, db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
, redis: RedisDep):
    cle = "article:" + str(current_user.id) + ":" + str(article_id)
    en_cache = await cache_get(redis, cle)
    if en_cache is not None:
        return en_cache

    article = db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    if article.utilisateur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    data = ArticlePublic.model_validate(article).model_dump(mode="json")
    await cache_set(redis, cle, data, 60)
    return data



@article_router.put("/{article_id}", response_model=ArticlePublic)
async def put_article(article_id: int, data: ArticleUpdate, db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
, redis: RedisDep):
    article_db = db.get(Article, article_id)
    if not article_db:
        raise HTTPException(status_code=404, detail="Article not found")
    # exclude_unset=True : ne modifie que les champs envoyés (FK scalaires 1-1/1-N incluses)
    if article_db.utilisateur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    payload = data.model_dump(exclude_unset=True)
    article_db.sqlmodel_update(payload)
    db.add(article_db)
    db.commit()
    db.refresh(article_db)
    await cache_delete(redis, "article:" + str(current_user.id) + ":" + str(article_id))
    await cache_delete_pattern(redis, "articles:list:" + str(current_user.id) + ":*")

    return article_db


@article_router.delete("/{article_id}")
async def delete_article(article_id: int, db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
, redis: RedisDep):
    article = db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    if article.utilisateur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    db.delete(article)
    db.commit()
    await cache_delete(redis, "article:" + str(current_user.id) + ":" + str(article_id))
    await cache_delete_pattern(redis, "articles:list:" + str(current_user.id) + ":*")

    return {"ok": True}



@article_router.get("/{article_id}/commentaires", response_model=ArticlePublicAvecCommentaires)
async def get_article_avec_commentaires(article_id: int, db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
):
    article = db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article introuvable")
    if article.utilisateur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")
 
    return article

@article_router.get("/{article_id}/tags", response_model=ArticlePublicAvecTags)
async def get_article_avec_tags(article_id: int, db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
):
    article = db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article introuvable")
    if article.utilisateur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")
 
    return article

@article_router.get("/{article_id}/utilisateur", response_model=ArticlePublicAvecUtilisateur)
async def get_article_avec_utilisateur(article_id: int, db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
):
    article = db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article introuvable")
    if article.utilisateur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    return article

@article_router.get("/{article_id}/categorie", response_model=ArticlePublicAvecCategorie)
async def get_article_avec_categorie(article_id: int, db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
):
    article = db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article introuvable")
    if article.utilisateur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    return article




@article_router.post("/{article_id}/tags/{tag_id}", response_model=ArticlePublicAvecTags)
async def ajouter_tags_a_article(article_id: int, tag_id: int, db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
):
    article = db.get(Article, article_id)
    tag = db.get(Tag, tag_id)
    if not article or not tag:
        raise HTTPException(status_code=404, detail="Article ou Tag introuvable")
    if article.utilisateur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")
 
    if tag not in article.tags:
        article.tags.append(tag)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article

@article_router.delete("/{article_id}/tags/{tag_id}", response_model=ArticlePublicAvecTags)
async def retirer_tags_de_article(article_id: int, tag_id: int, db: get_db  , current_user: Annotated[Utilisateur, Depends(get_current_utilisateur)]
):
    article = db.get(Article, article_id)
    tag = db.get(Tag, tag_id)
    if not article or not tag:
        raise HTTPException(status_code=404, detail="Article ou Tag introuvable")
    if article.utilisateur_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")
 
    if tag in article.tags:
        article.tags.remove(tag)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article
