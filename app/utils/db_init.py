from app.config.database import engine
from app.models.user import User

def create_models():
    User.metadata.create_all(bind = engine)