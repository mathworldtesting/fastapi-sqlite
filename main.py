from fastapi import FastAPI
import models.todos_model
from database.sqlite import engine
from routers.auth import router as auth
from routers.todo import router as todo

app = FastAPI()

models.todos_model.Base.metadata.create_all(bind=engine)
app.include_router(auth)
app.include_router(todo, prefix="/todo", tags=["todo"])
