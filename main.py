from fastapi import FastAPI, Depends
from typing import Annotated
from sqlalchemy.orm import Session
import models.todos
from models import todos
from database.sqlite import engine, SessionLocal


app = FastAPI()

models.todos.Base.metadata.create_all(bind=engine)


def get_db():
    """
    Yields a database session object.
    
    This function is meant to be used as a FastAPI dependency. It yields a
    database session object that can be used to query the database. The
    session is automatically closed when the context manager is exited.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/")
async def read_all(db: db_dependency):
    """
    Returns all TODOs in the database.

    This endpoint returns a list of all TODOs in the database. The TODOs are
    returned in the order they were inserted.
    """
    return db.query(models.todos.Todos).all() 
    