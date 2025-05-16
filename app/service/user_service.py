from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.repository.user_repository import UserRepository
from app.schemas.request_schemas import UserInput, UserUpdate
from app.schemas.response_schemas import UserOutput
from app.utils.email_util import send_email_background
from app.security import hashing, encode_decode



class UserService:

    def __init__(self, db: Session, background_task:BackgroundTasks = None):
        self.background_task = background_task
        self.repository = UserRepository(db)


    def create(self, user: UserInput) -> dict | HTTPException:
        if self.repository.user_exist_with_email(user.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='user with same email already registered')
        
        user.password = hashing.hash_password(user.password)        # hashing the password before creating instance
        user_instance, db_exception = self.repository.create(user)

        if user_instance:
            token = hashing.hash_data(user_instance.get_context())
            identity = encode_decode.encode_data(user_instance.email)

            self.background_task.add_task(                          # sending email verify mail to the registered user
                send_email_background,
                'Account Verification',
                user_instance.email,
                'verify_email_template.html',
                {'token': token, 'data': identity}
                )
            
            # return user_instance
            return {'success' : 'profile created, a verification link has been send to your registered email'}
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'{db_exception}')
        

    def verify_account(self, token, data) -> dict | HTTPException:
        email = encode_decode.decode_data(data.strip()).strip()
        if not self.repository.user_exist_with_email(email):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
        
        user_context = self.repository.get_user_context(email)

        try:
            if hashing.verify_data(user_context, token):
                return self.repository.verify_profile(email)
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="link has expired or invalid")
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='link has expired or invalid')
        

    def get_current_user(self, email: str):
        if not self.repository.user_exist(email):
            return None
        
        return self.repository.get_current_user(email)
    
    def authenticate_user(self, email: str, password: str):
        return self.repository.authenticate_user(email, password)
    
    def get_all_users(self, exclude_id: int, super_user: bool):
        return self.repository.all_users(exclude_id, super_user)
    
    def get_user_by_id(self, user_id: int, super_user: bool):
        if not self.repository.user_exist_by_id(user_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
        
        return self.repository.get_user(user_id, super_user)
    
    def forgot_password_service(self, email: str)-> dict:
        if not self.repository.user_exist(email):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
        
        user_context = self.repository.get_user_context(email)
        token = hashing.hash_data(user_context)
        identity = encode_decode.encode_data(email)
        self.background_task.add_task(                          # sending email verify mail to the registered user
                send_email_background,
                'Forgot Password Mail',
                email,
                'forgot_password_template.html',
                {'token': token, 'data': identity}
                )
        
        return {'detail' : 'A mail has been send to reset your password'}


    def verify_and_reset_password(self, token: str, data: str, new_password: str) -> dict:
        email = encode_decode.decode_data(data.strip()).strip()
        if not self.repository.user_exist(email):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
        
        user_context = self.repository.get_user_context(email)

        try:
            if hashing.verify_data(user_context, token):
                new_password = hashing.hash_password(new_password)
                return self.repository.reset_password(email, new_password)
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="link has expired or invalid")
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='link has expired or invalid')
        

    def reset_password(self, email, password) -> dict:
        new_password = hashing.hash_password(password)
        return self.repository.reset_password(email, new_password)
    
    def update_data(self, email: str, data: UserUpdate):
        return self.repository.update_data(email, data)
    
    def delete_user(self, user_id: str, has_permission: bool):
        if not has_permission:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Permission Denied')
        if self.repository.verify_and_destroy(user_id):
            return
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
