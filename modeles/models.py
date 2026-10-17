from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from typing import Optional
from typing import  List
from sqlmodel import Relationship




class ArticleTagLink(SQLModel, table=True):
    article_id : Optional[int] = Field(default=None, foreign_key="article.id", primary_key=True)
    tag_id : Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)





class Utilisateur(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str 
    email: str  = Field(unique=True)
    password: str 
    bio: Optional[str]  = Field(nullable=True, default=None)
    avatar_url: Optional[str]  = Field(nullable=True, default=None)
    role: str  = Field(default="auteur")
    est_actif: bool  = Field(default=True)
    cree_le: datetime  = Field(default_factory=lambda: datetime.now(timezone.utc))
    articles: List["Article"] = Relationship(back_populates="utilisateur")
    commentaires: List["Commentaire"] = Relationship(back_populates="utilisateur")
    medias: List["Media"] = Relationship(back_populates="utilisateur")




class Categorie(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str  = Field(unique=True)
    slug: str  = Field(unique=True)
    description: Optional[str]  = Field(nullable=True, default=None)
    couleur: Optional[str]  = Field(nullable=True, default=None)
    articles: List["Article"] = Relationship(back_populates="categorie")



class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str  = Field(unique=True)
    slug: str  = Field(unique=True)
    articles: List["Article"] = Relationship(back_populates="tags", link_model=ArticleTagLink)



class Article(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titre: str 
    slug: str  = Field(unique=True)
    extrait: Optional[str]  = Field(nullable=True, default=None)
    contenu: str 
    image_couverture: Optional[str]  = Field(nullable=True, default=None)
    statut: str  = Field(default="brouillon")
    est_mis_en_avant: bool  = Field(default=False)
    temps_lecture: int  = Field(default=1)
    nombre_vues: int  = Field(default=0)
    date_publication: Optional[datetime]  = Field(nullable=True, default=None)
    cree_le: datetime  = Field(default_factory=lambda: datetime.now(timezone.utc))
    modifie_le: datetime  = Field(default_factory=lambda: datetime.now(timezone.utc))
    commentaires: List["Commentaire"] = Relationship(back_populates="article")
    tags: List["Tag"] = Relationship(back_populates="articles", link_model=ArticleTagLink)
    utilisateur_id: Optional[int] = Field(default=None, foreign_key="utilisateur.id")
    utilisateur: Optional["Utilisateur"] = Relationship(back_populates="articles")
    categorie_id: Optional[int] = Field(default=None, foreign_key="categorie.id")
    categorie: Optional["Categorie"] = Relationship(back_populates="articles")



class Commentaire(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    contenu: str 
    est_approuve: bool  = Field(default=False)
    cree_le: datetime  = Field(default_factory=lambda: datetime.now(timezone.utc))
    utilisateur_id: Optional[int] = Field(default=None, foreign_key="utilisateur.id")
    utilisateur: Optional["Utilisateur"] = Relationship(back_populates="commentaires")
    article_id: Optional[int] = Field(default=None, foreign_key="article.id")
    article: Optional["Article"] = Relationship(back_populates="commentaires")



class Media(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom_fichier: str 
    url: str 
    type_mime: str 
    taille: int  = Field(default=0)
    texte_alternatif: Optional[str]  = Field(nullable=True, default=None)
    cree_le: datetime  = Field(default_factory=lambda: datetime.now(timezone.utc))
    utilisateur_id: Optional[int] = Field(default=None, foreign_key="utilisateur.id")
    utilisateur: Optional["Utilisateur"] = Relationship(back_populates="medias")



class Page(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titre: str 
    slug: str  = Field(unique=True)
    contenu: str 
    est_publiee: bool  = Field(default=True)
    modifie_le: datetime  = Field(default_factory=lambda: datetime.now(timezone.utc))



class Abonne(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str  = Field(unique=True)
    est_actif: bool  = Field(default=True)
    inscrit_le: datetime  = Field(default_factory=lambda: datetime.now(timezone.utc))



class Contact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str 
    email: str 
    sujet: str 
    message: str 
    est_lu: bool  = Field(default=False)
    envoye_le: datetime  = Field(default_factory=lambda: datetime.now(timezone.utc))





