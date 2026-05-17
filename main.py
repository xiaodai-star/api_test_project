from fastapi import FastAPI
from api import user_api

app = FastAPI()
app.include_router(user_api.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)