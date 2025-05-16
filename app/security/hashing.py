from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)



def hash_data(data: str) -> str:
    return pwd_context.hash(data)

def verify_data(raw_data: str, hashed_data: str) -> bool:
    return pwd_context.verify(raw_data, hashed_data)