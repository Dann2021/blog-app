from sqlmodel import SQLModel, Field
from typing import List, Optional

 
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.article import ArticlePublic



class CategorieBase(SQLModel):
    nom: str = Field(title="Nom", description="Attribut nom")
    slug: str = Field(title="Slug", description="Attribut slug")
    description: str | None = Field(default=None, title="Description", description="Attribut description")
    couleur: str | None = Field(default=None, title="Couleur", description="Attribut couleur")



class CategorieCreate(CategorieBase):
    pass




class CategoriePublic(CategorieBase):
    id : int




class CategoriePublicAvecArticles(CategoriePublic):
    articles: List["ArticlePublic"] = []






class CategorieUpdate(SQLModel):
 
    nom: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    couleur: Optional[str] = None


