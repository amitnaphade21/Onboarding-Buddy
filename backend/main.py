from fastapi import FastAPI
from api.chat import router
from api.users import router as users_router


from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.include_router(router)
app.include_router(users_router)
@app.get("/")
def health():
    return {"status": "ok"}
