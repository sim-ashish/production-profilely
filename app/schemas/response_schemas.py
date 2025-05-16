from pydantic import BaseModel, EmailStr, computed_field
from datetime import datetime

class UserOutput(BaseModel):
    id: int | None = None
    first_name: str
    last_name: str
    email: EmailStr
    is_superuser: bool | None = None
    bio: str | None = None
    created_at: datetime | None = None
    

    @computed_field
    @property
    def fullname(self) -> str:
        return f'{self.first_name} {self.last_name}'
    
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_email: str

