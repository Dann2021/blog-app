from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
 



class PageBase(SQLModel):
    titre: str = Field(title="Titre", description="Attribut titre")
    slug: str = Field(title="Slug", description="Attribut slug")
    contenu: str = Field(title="Contenu", description="Attribut contenu")
    est_publiee: bool = Field(default=True, title="Est Publiee", description="Attribut est publiee")



class PageCreate(PageBase):
    pass




class PagePublic(PageBase):
    id : int


    modifie_le : datetime







class PageUpdate(SQLModel):
 
    titre: Optional[str] = None
    slug: Optional[str] = None
    contenu: Optional[str] = None
    est_publiee: Optional[bool] = None


