from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
 



class AbonneBase(SQLModel):
    email: str = Field(title="Email", description="Attribut email")
    est_actif: bool = Field(default=True, title="Est Actif", description="Attribut est actif")



class AbonneCreate(AbonneBase):
    pass




class AbonnePublic(AbonneBase):
    id : int


    inscrit_le : datetime







class AbonneUpdate(SQLModel):
 
    email: Optional[str] = None
    est_actif: Optional[bool] = None


