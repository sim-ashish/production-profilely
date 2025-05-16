from fastapi import APIRouter, Depends, status, BackgroundTasks, HTTPException, Body, Request, Form
from pydantic import EmailStr
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.request_schemas import UserInput, UserUpdate
from app.schemas.response_schemas import UserOutput, Token
from app.service.user_service import UserService
from typing import Annotated
from app.config.database import get_db
from sqlalchemy.orm import Session
from app.dependency import get_current_user
from datetime import timedelta
from app.security.jwt_token import create_access_token
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix='/user',
    tags = ["Users"],
    responses={404:{'detail' : 'endpoint not found'}}
)

DATABASE_OBJECT = Annotated[Session, Depends(get_db)]

@router.get('/send-template', include_in_schema=False)
def template_response(request: Request, token: str, data: str):
    return templates.TemplateResponse(
        request=request, name="change_password.html", context={"token":token, "data":data}
    )


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_user(user: UserInput, background_task: BackgroundTasks, db: DATABASE_OBJECT) -> dict:
    _service = UserService(db, background_task)
    return _service.create(user)


@router.get('/verify', status_code=status.HTTP_200_OK)
def verify_account(token: str, data: str, db: DATABASE_OBJECT) -> dict:
    _service = UserService(db)
    return _service.verify_account(token, data)


@router.get('/me', response_model=UserOutput, response_model_exclude_none = True, status_code=status.HTTP_200_OK)
def my_profile(user: Annotated[UserOutput, Depends(get_current_user)]):
    return user


@router.get('/all', response_model=list[UserOutput], response_model_exclude_none = True, status_code=status.HTTP_200_OK)
def all_users(user: Annotated[UserOutput, Depends(get_current_user)], db: DATABASE_OBJECT):
    super_user = True if user.is_superuser else False
    _service = UserService(db)
    users = _service.get_all_users(user.id, super_user)
    users.append(user)
    return users


@router.get('/{user_id}', response_model=UserOutput, response_model_exclude_none = True, status_code=status.HTTP_200_OK)
def user_profile(user_id: int, user: Annotated[UserOutput, Depends(get_current_user)], db: DATABASE_OBJECT):
    if user_id == user.id:
        return user
    super_user = True if user.is_superuser else False
    _service = UserService(db)
    return _service.get_user_by_id(user_id, super_user)



@router.post("/login", summary='Login User', description="Login user to get access token")
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DATABASE_OBJECT) -> Token:
    _service = UserService(db)
    user = _service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.patch("/", status_code=status.HTTP_204_NO_CONTENT)
def update_profile(data: UserUpdate, user: Annotated[UserOutput, Depends(get_current_user)], db: DATABASE_OBJECT):
    _service = UserService(db)
    return _service.update_data(user.email, data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, user: Annotated[UserOutput, Depends(get_current_user)], db: DATABASE_OBJECT):
    has_permission = True if user.is_superuser or user_id == user.id else False
    _service = UserService(db)
    return _service.delete_user(user_id, has_permission)

@router.post("/forgot-password")
def forgot_password(email: Annotated[EmailStr, Body(examples=['chauashish21@gmail.com'])], background_task: BackgroundTasks, db: DATABASE_OBJECT) -> dict:
    _service = UserService(db, background_task)
    return _service.forgot_password_service(email)


@router.post("/reset-forgot-password", include_in_schema=False)
def reset_forgotted_password(token: Annotated[str, Form()], data: Annotated[str, Form()], new_password: Annotated[str, Form()], db: DATABASE_OBJECT) -> dict:
    _service = UserService(db)
    return _service.verify_and_reset_password(token, data, new_password)


@router.post("/reset-password")
def reset_password(password: Annotated[str, Body(examples=['Refd14565@sd'])], user: Annotated[UserOutput, Depends(get_current_user)], db: DATABASE_OBJECT) -> dict:
    _service = UserService(db)
    return _service.reset_password(user.email, password)



