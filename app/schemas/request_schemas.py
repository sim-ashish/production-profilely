from pydantic import BaseModel, EmailStr, field_validator, ValidationError
import re

class UserInput(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    bio: str | None = None

    @field_validator('password', mode='before')  
    @classmethod
    def is_valid(cls, value: str) -> str:
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).{8,}$'
        if re.match(pattern, value):
            return value
        raise ValueError('Password must be 8 characters long, should include a upper case, a lower case, a digit and a special character!')

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "first_name": "Joey",
                    "last_name": "Pollard",
                    "email": "pollardjoey@gmail.com",
                    "password": "pollard@2236joey",
                    "bio" : "Football, Tennis, Foosball"
                }
            ]
        }
    }

class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    bio: str | None = None

