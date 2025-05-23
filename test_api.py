from fastapi.testclient import TestClient
from app.config.database import get_db
from main import app
from sqlalchemy import create_engine, StaticPool, text
from sqlalchemy.orm import sessionmaker
from app.models.user import Base, User
from app.security import hashing

DATABASE_URL = "sqlite:///:memory"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread":False,
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db

    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

auth_token = None # For JWT token


def setup():
    print("Setting up the database...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create test session
    session = TestingSessionLocal()

    try:
        # Create a new user
        db_item = User(
            first_name='Ashish',
            last_name='Chaudhary',
            email='chauashish21@gmail.com',
            password=hashing.hash_password('hello123@dinoPG'),
            bio='Foosball',
            is_verified=True,
            is_superuser=True,
        )
        db_item2 = User(
            first_name='Prem',
            last_name='Mehra',
            email='premmehra@gmail.com',
            password=hashing.hash_password('hello123@dinoPG'),
            bio='Foosball',
            is_verified=True,
        )
        session.add_all([db_item, db_item2])
        session.commit()  # This assigns an ID to db_item

        # Now safely use the actual user ID (don't assume it's 1)
        session.execute(
            text("UPDATE users SET is_verified = true WHERE id = :id"),
            {"id": db_item.id}
        )

        session.commit()
        print("Test user created and verified.")
    except Exception as e:
        session.rollback()
        print("Error during setup:", e)
    finally:
        session.close()


def test_main():
    response = client.get('/')
    assert response.status_code == 200


def test_password_validation():
    response = client.post("/user/", json={
        "bio": "Football, Tennis, Foosball",
        "email": "chauashish21@gmail.com",
        "first_name": "Ashish",
        "last_name": "Chaudhary",
        "password": "hello"
    })
    assert response.status_code == 422


def test_already_exist_user():
    response = client.post("/user/", json={
        "bio": "Football, Tennis, Foosball",
        "email": "chauashish21@gmail.com",
        "first_name": "Ashish",
        "last_name": "Chaudhary",
        "password": "hello123@dinoPG"
    })
    assert response.status_code == 400
    assert response.json() == {'detail': 'user with same email already registered'}


def test_user_create():
    response = client.post("/user/", json={
        "bio": "Football, Tennis, Foosball",
        "email": "ashishchaudhary9193@gmail.com",
        "first_name": "Ashish",
        "last_name": "Chaudhary",
        "password": "hello123@dinoPG"
        })
    assert response.status_code == 201
    assert response.json() == {'success': 'profile created, a verification link has been send to your registered email'}

def test_user_login():
    response = client.post("/user/login", data={
        'username':'chauashish21@gmail.com',
        'password' : 'hello123@dinoPG'
    })
    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'
    global auth_token
    auth_token = data['access_token']
    assert auth_token is not None

def test_user_login_invalid():
    response = client.post("/user/login", data={
        'username':'chauashish21@gmail.com',
        'password' : 'wrongpassword',
    })
    assert response.status_code == 401
    assert response.json() == {'detail': 'Incorrect email or password'}
    assert 'WWW-Authenticate' in response.headers

def test_current_user():
    response = client.get('/user/me', headers={
        'Authorization': f'Bearer {auth_token}'
    })
    assert response.status_code == 200
    assert response.json()['email'] == 'chauashish21@gmail.com'
    assert response.json()['bio'] == 'Foosball'
    assert response.json()['is_superuser'] == True

def test_invalid_token():
    response = client.get('/user/me', headers={
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJleGFtcGxlX2lzcyIsImlhdCI6MTYzMzg2NDg3NCwiZXhwIjoxNjMzOTU3Mzc0LCJ1c2VySWQiOiIxMjMiLCJyb2xlIjoiYWRtaW4ifQ.uKqU9dTB6gKwG6jQCuXYAiMNdfNRw98Hw_IWuA5MaMo'
    })
    assert response.status_code == 401
    assert response.json() == {'detail': 'Could not validate credentials'}

def test_user_delete():
    response = client.delete('/user/2', headers={'Authorization': f'Bearer {auth_token}'})
    assert response.status_code == 204
    # Check if the user is actually deleted
    response = client.get('/user/2', headers={'Authorization': f'Bearer {auth_token}'})
    assert response.status_code == 404
    assert response.json() == {'detail': 'user not found'}

def teardown():
    Base.metadata.drop_all(bind=engine)