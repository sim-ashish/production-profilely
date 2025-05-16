from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.request_schemas import UserInput, UserUpdate
from app.schemas.response_schemas import UserOutput
from app.security.hashing import verify_password

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def user_exist(self, email: str) -> bool:
        user_instance = self.db.query(User).filter(User.email == email, User.is_verified == True).first()
        if user_instance:
            return True
        
        return False
    
    def user_exist_with_email(self, email: str) -> bool:
        user_instance = self.db.query(User).filter(User.email == email).first()
        if user_instance:
            return True
        
        return False
    
    def user_exist_by_id(self, id: int) -> bool:
        user_instance = self.db.query(User).filter(User.id == id, User.is_verified == True).first()
        if user_instance:
            return True
        
        return False
    
    def create(self, user: UserInput) -> tuple[User | None, Exception | None]:
        try:
            user_instance = User(**user.model_dump(exclude_none=True))
            self.db.add(user_instance)
            self.db.commit()
            self.db.refresh(user_instance)
        except Exception as e:
            return None, e

        return user_instance, None
    
    def get_user_by_email(self, email) -> User:
        user_instance = self.db.query(User).filter(User.email == email, User.is_verified == True).first()
        return user_instance
    
    def get_user_context(self, email) -> str:
        user_instance = self.db.query(User).filter(User.email == email).first()
        context_data = user_instance.get_context()
        
        return context_data
    
    def verify_profile(self, email) -> dict:
        user_instance = self.db.query(User).filter(User.email == email).first()
        user_instance.is_verified = True

        self.db.commit()
        self.db.refresh(user_instance)

        return {'detail' : 'account verified, now you can login'}

    def get_current_user(self, email: str) -> UserOutput:
        user_instance = self.db.query(User).filter(User.email == email, User.is_verified == True).first()
        user_dict = {key: value for key, value in user_instance.__dict__.items() if not key.startswith('_')}
        user_model = UserOutput(**user_dict)
        if not user_instance.is_superuser:
            return  user_model.copy(update={'is_superuser': None, 'created_at': None})
        
        return user_model
    

    def authenticate_user(self, email: str, password: str) -> bool | User:
        user_instance = self.db.query(User).filter(User.email == email, User.is_verified == True).first()
        if not user_instance:
            return False
        if not verify_password(password, user_instance.password):
            return False
        return user_instance
    

    def all_users(self, exclude_id: int, super_user: bool) -> list[User]:
        if not super_user:
            users = self.db.query(User.first_name, User.last_name, User.email, User.bio).filter(User.id != exclude_id, User.is_verified == True).all()
            return users
        
        users = self.db.query(User).filter(User.id != exclude_id).all()
        return users
    
    
    def get_user(self, user_id: int, super_user: bool) -> User:
        if not super_user:
            user = self.db.query(User.first_name, User.last_name, User.email, User.bio).filter(User.id == user_id, User.is_verified == True).first()
            return user
        
        user = self.db.query(User).filter(User.id == user_id).first()
        return user
    
    def reset_password(self, email: str, new_password: str) -> dict:
        user_instance = self.db.query(User).filter(User.email == email, User.is_verified == True).first()
        user_instance.password = new_password
        self.db.commit()
        self.db.refresh(user_instance)

        return {'detail' : 'your password has been reset successfully'}
    
    def update_data(self, email: str, data: UserUpdate):
        self.db.query(User).filter(User.email == email, User.is_verified == True).update(data.model_dump(exclude_unset = True))
        self.db.commit()
        return
    
    def verify_and_destroy(self, user_id: int):
        user_instance = self.db.query(User).filter(User.id == user_id, User.is_verified == True).first()
        if user_instance:
            self.db.delete(user_instance)
            self.db.commit()
            return True
        
        return False
