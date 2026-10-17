from sqlmodel import SQLModel, Field
from typing import List, Optional
from datetime import datetime
 
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.commentaire import CommentairePublic
    from schemas.tag import TagPublic
    from schemas.utilisateur import UtilisateurPublic
    from schemas.categorie import CategoriePublic



class ArticleBase(SQLModel):
    titre: str = Field(title="Titre", description="Attribut titre")
    slug: str = Field(title="Slug", description="Attribut slug")
    extrait: str | None = Field(default=None, title="Extrait", description="Attribut extrait")
    contenu: str = Field(title="Contenu", description="Attribut contenu")
    image_couverture: str | None = Field(default=None, title="Image Couverture", description="Attribut image couverture")
    statut: str = Field(default="brouillon", title="Statut", description="Attribut statut")
    est_mis_en_avant: bool = Field(default=False, title="Est Mis En Avant", description="Attribut est mis en avant")
    temps_lecture: int = Field(default=1, title="Temps Lecture", description="Attribut temps lecture")
    nombre_vues: int = Field(default=0, title="Nombre Vues", description="Attribut nombre vues")
    date_publication: datetime | None = Field(default=None, title="Date Publication", description="Attribut date publication")



class ArticleCreate(ArticleBase):

    utilisateur_id : int
    categorie_id : int

    tags_ids: List[int] = []






class ArticlePublic(ArticleBase):
    id : int
    utilisateur_id : int
    categorie_id : int


    cree_le : datetime
    modifie_le : datetime


class ArticlePublicAvecCommentaires(ArticlePublic):
    commentaires: List["CommentairePublic"] = []

class ArticlePublicAvecTags(ArticlePublic):
    tags: List["TagPublic"] = []



class ArticlePublicAvecUtilisateur(ArticlePublic):
    utilisateur: Optional["UtilisateurPublic"] = None

class ArticlePublicAvecCategorie(ArticlePublic):
    categorie: Optional["CategoriePublic"] = None




class ArticleUpdate(SQLModel):
 
    titre: Optional[str] = None
    slug: Optional[str] = None
    extrait: Optional[str] = None
    contenu: Optional[str] = None
    image_couverture: Optional[str] = None
    statut: Optional[str] = None
    est_mis_en_avant: Optional[bool] = None
    temps_lecture: Optional[int] = None
    nombre_vues: Optional[int] = None
    date_publication: Optional[datetime] = None
    utilisateur_id : Optional[int] = None
    categorie_id : Optional[int] = None


