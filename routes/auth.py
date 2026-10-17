
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from ..securites.securite import verifier_password, creer_access_token, creer_refresh_token
from ..modeles.models import Utilisateur
from ..database import get_db


 

auth_router = APIRouter(prefix="/token", tags=["auth"])

@auth_router.post("")
async def login(response: Response,form_data: Annotated[OAuth2PasswordRequestForm, Depends()],session: get_db):

    utilisateur = session.exec(select(Utilisateur).where(Utilisateur.email == form_data.username)).first()

    if not utilisateur or not verifier_password(form_data.password, utilisateur.password):
        raise HTTPException(
            status_code=401,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

   
    access_token = creer_access_token(data={"sub": str(utilisateur.id)})
    refresh_token = creer_refresh_token(data={"sub": str(utilisateur.id)})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/token",
    )

    return {"access_token": access_token, "token_type": "bearer"}
