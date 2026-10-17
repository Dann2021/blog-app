from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
 
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.utilisateur import UtilisateurPublic
    from schemas.article import ArticlePublic



class CommentaireBase(SQLModel):
    contenu: str = Field(title="Contenu", description="Attribut contenu")
    est_approuve: bool = Field(default=False, title="Est Approuve", description="Attribut est approuve")



class CommentaireCreate(CommentaireBase):

    utilisateur_id : int
    article_id : int







class CommentairePublic(CommentaireBase):
    id : int
    utilisateur_id : int
    article_id : int


    cree_le : datetime




class CommentairePublicAvecUtilisateur(CommentairePublic):
    utilisateur: Optional["UtilisateurPublic"] = None

class CommentairePublicAvecArticle(CommentairePublic):
    article: Optional["ArticlePublic"] = None




class CommentaireUpdate(SQLModel):
 
    contenu: Optional[str] = None
    est_approuve: Optional[bool] = None
    utilisateur_id : Optional[int] = None
    article_id : Optional[int] = None


