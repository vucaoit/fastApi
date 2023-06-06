from datetime import datetime
from typing_extensions import Annotated
from sqlalchemy.orm import Session
import jwt
import crud
from jose import JWTError
from fastapi import Depends, HTTPException,status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, ValidationError

SECURITY_ALGORITHM = 'HS256'
SECRET_KEY = '123456'

reusable_oauth2 = HTTPBearer(
    scheme_name='Authorization'
)

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    

def validate_token(http_authorization_credentials=Depends(reusable_oauth2)) -> str:
    """
    Decode JWT token to get username => return username
    """
    try:
        payload = jwt.decode(http_authorization_credentials.credentials, SECRET_KEY, algorithms=[SECURITY_ALGORITHM])
        print(payload)
        if datetime.fromtimestamp(payload.get('exp')) < datetime.now():
            raise HTTPException(status_code=403, detail="Token expired")
        return payload.get('username')
    except(jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=403,
            detail=f"Could not validate credentials",
        )

def get_current_user(token: Annotated[str, Depends(reusable_oauth2)],db:Session)->User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[SECURITY_ALGORITHM])
        print(payload)
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
        token_data = TokenData(username=email)
    except JWTError:
        raise HTTPException(status_code=404, detail="Token Error")
    user = crud.get_user_by_email(db, email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user