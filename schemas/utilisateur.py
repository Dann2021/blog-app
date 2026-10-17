from sqlmodel import SQLModel, Field
from typing import List, Optional
from datetime import datetime
 
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.article import ArticlePublic
    from schemas.commentaire import CommentairePublic
    from schemas.media import MediaPublic



class UtilisateurBase(SQLModel):
    nom: str = Field(title="Nom", description="Attribut nom")
    email: str = Field(title="Email", description="Attribut email")
    bio: str | None = Field(default=None, title="Bio", description="Attribut bio")
    avatar_url: str | None = Field(default=None, title="Avatar Url", description="Attribut avatar url")
    role: str = Field(default="auteur", title="Role", description="Attribut role")
    est_actif: bool = Field(default=True, title="Est Actif", description="Attribut est actif")



class UtilisateurCreate(UtilisateurBase):
    password : str








class UtilisateurPublic(UtilisateurBase):
    id : int


    cree_le : datetime


class UtilisateurPublicAvecArticles(UtilisateurPublic):
    articles: List["ArticlePublic"] = []

class UtilisateurPublicAvecCommentaires(UtilisateurPublic):
    commentaires: List["CommentairePublic"] = []

class UtilisateurPublicAvecMedias(UtilisateurPublic):
    medias: List["MediaPublic"] = []






class UtilisateurUpdate(SQLModel):
 
    nom: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    role: Optional[str] = None
    est_actif: Optional[bool] = None


