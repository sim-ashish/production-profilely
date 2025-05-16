from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.router import user_router
from app.utils.db_init import create_models

description = """
Profilely API helps you do awesome stuff. 🚀

## User

* You can **create your profile** (_implemented_).
* You can **verify your account using email verification link** (_implemented_).
* You can **login to your account** (_implemented_).
* You can **update your profile** (_implemented_).
* You can **reset your password** (_implemented_).
* You can **forgot reset your password** (_implemented_).
* You can **delete your acount or anyone's if you are admin** (_implemented_).

"""


app = FastAPI(
    debug = True,
    title = "Todo App",
    description = description,
    summary="User's favorite app for todos.",
    version="1.0.0",
    contact={
        "name": "Ashish Chaudhary",
        "url": "https://github.com/sim-ashish",
        "email": "chauashish21@gmail.com",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup()-> None:
     create_models()

app.include_router(user_router.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", tags = ['Documentation'], summary="documentation", include_in_schema= False)
def main():
     return RedirectResponse(url="/docs")