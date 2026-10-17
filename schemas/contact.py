from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
 



class ContactBase(SQLModel):
    nom: str = Field(title="Nom", description="Attribut nom")
    email: str = Field(title="Email", description="Attribut email")
    sujet: str = Field(title="Sujet", description="Attribut sujet")
    message: str = Field(title="Message", description="Attribut message")
    est_lu: bool = Field(default=False, title="Est Lu", description="Attribut est lu")



class ContactCreate(ContactBase):
    pass




class ContactPublic(ContactBase):
    id : int


    envoye_le : datetime







class ContactUpdate(SQLModel):
 
    nom: Optional[str] = None
    email: Optional[str] = None
    sujet: Optional[str] = None
    message: Optional[str] = None
    est_lu: Optional[bool] = None


