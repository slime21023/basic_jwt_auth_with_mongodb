from fastapi import APIRouter, HTTPException, Header, status
from bunnet import WriteRules
from database import User, Account
from pydantic import BaseModel, EmailStr, Field
from passlib.hash import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Annotated, Union


router = APIRouter(prefix="/api/auth", tags=["auth"])

SECRET_KEY = "6cf2c6727f01c7e73078b36f9fecfff9a788869d036877454524942af4be95db"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120


class SignupInfo(BaseModel):
    email: EmailStr
    first_name: str = Field(max_length=30)
    last_name: str = Field(max_length=30)
    password: str


class LoginInfo(BaseModel):
    email: EmailStr
    password: str


@router.post("/signup")
async def signup(info: SignupInfo):
    user = User.find_one(User.email == info.email).run()
    if user is not None:
        return {"status": "fail", "message": "user_existed"}

    user = User(email=info.email, first_name=info.first_name, last_name=info.last_name)
    password = bcrypt.hash(info.password)

    account = Account(user=user, password=password)
    account.save(link_rule=WriteRules.WRITE)
    return {"status": "ok"}


@router.post("/login")
async def login(info: LoginInfo):
    account = Account.find_one(
        Account.user.email == info.email,
        fetch_links=True
    ).run()

    if account is None:
        return {"status": "fail", "message": "user_no_existed"}
    
    verified = bcrypt.verify(info.password, account.password)
    if not verified:
        return {"status": "fail", "message": "password_wrong"}

    to_encode = {
        "email": account.user.email,
        "sub": str(account.user.id),
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return { "access_token": encoded_jwt, "token_type": "bearer" }


@router.post("/verify_token")
async def verify_token(access_token: Annotated[str, Header()]) -> Union[User]:
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        user = User.get(user_id).run()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    except JWTError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="UNAUTHORIZED")

