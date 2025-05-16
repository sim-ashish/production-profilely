from pydantic import BaseModel, EmailStr

class UserInput(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    bio: str | None = None

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

