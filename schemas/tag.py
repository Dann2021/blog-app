from sqlmodel import SQLModel, Field
from typing import List, Optional

 
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.article import ArticlePublic



class TagBase(SQLModel):
    nom: str = Field(title="Nom", description="Attribut nom")
    slug: str = Field(title="Slug", description="Attribut slug")



class TagCreate(TagBase):


    article_ids: List[int] = []






class TagPublic(TagBase):
    id : int






class TagPublicAvecArticle(TagPublic):
    article: List["ArticlePublic"] = []




class TagUpdate(SQLModel):
 
    nom: Optional[str] = None
    slug: Optional[str] = None


