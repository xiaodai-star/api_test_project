from fastapi import FastAPI
from api.user_api import router as user_router

app = FastAPI(title = "hello,fastapi")
app.include_router(user_router)

