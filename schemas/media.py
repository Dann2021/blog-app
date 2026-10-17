from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
 
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.utilisateur import UtilisateurPublic



class MediaBase(SQLModel):
    nom_fichier: str = Field(title="Nom Fichier", description="Attribut nom fichier")
    url: str = Field(title="Url", description="Attribut url")
    type_mime: str = Field(title="Type Mime", description="Attribut type mime")
    taille: int = Field(default=0, title="Taille", description="Attribut taille")
    texte_alternatif: str | None = Field(default=None, title="Texte Alternatif", description="Attribut texte alternatif")



class MediaCreate(MediaBase):

    utilisateur_id : int







class MediaPublic(MediaBase):
    id : int
    utilisateur_id : int


    cree_le : datetime




class MediaPublicAvecUtilisateur(MediaPublic):
    utilisateur: Optional["UtilisateurPublic"] = None




class MediaUpdate(SQLModel):
 
    nom_fichier: Optional[str] = None
    url: Optional[str] = None
    type_mime: Optional[str] = None
    taille: Optional[int] = None
    texte_alternatif: Optional[str] = None
    utilisateur_id : Optional[int] = None


