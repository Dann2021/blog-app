from datetime import timedelta, datetime, timezone
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from ..database import get_db
from ..modeles.models import Utilisateur
from pwdlib import PasswordHash
from ..config import settings



# Configuration de l'authentification OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# creation d'une instance de PasswordHash pour hasher les password
password_hash = PasswordHash.recommended()



# Vérifier si le hash est correct
def verifier_password(password:str, passwordhasher: str) -> bool:
    return password_hash.verify(password, passwordhasher)

# hashage
def hasher_password(password: str) -> str:
    return password_hash.hash(password)



# création d'une fonction pour récupérer un utilisateur par son id
def get_utilisateurby_id(db: get_db, utilisateur_id: int):
    return db.get(Utilisateur, utilisateur_id)


# création des token
def creer_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expires_minutes)

    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def creer_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expires_days)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def get_current_utilisateur(db: get_db,token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token,settings.secret_key, algorithms=[settings.algorithm])
        utilisateur_id_raw = payload.get("sub")
        if utilisateur_id_raw is None:
            raise credentials_exception
        utilisateur_id = int(utilisateur_id_raw)

    except (jwt.PyJWTError, ValueError):
        raise credentials_exception

    utilisateur = get_utilisateurby_id(db, utilisateur_id=utilisateur_id)
    if utilisateur is None:
        raise credentials_exception
    return utilisateur
