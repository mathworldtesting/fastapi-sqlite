import pdb
from fastapi import FastAPI, Depends, HTTPException, Path
from fastapi import status
from typing import Annotated
from pydantic import BaseModel, Field
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

# create Pydanic request model
class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=40)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    completed: bool = False


@app.get("/todo/fetch-all")
async def read_all(db: db_dependency, status_code=status.HTTP_200_OK):
    """
    Returns all TODOs in the database.

    This endpoint returns a list of all TODOs in the database. The TODOs are
    returned in the order they were inserted.
    """
    return db.query(models.todos.Todos).all() 


@app.get("/todo/fetch/{id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, id: int = Path(gt=0), ):
    """
    Returns a single TODO from the database.

    This endpoint returns a single TODO from the database based on the
    `todo_id` parameter. If the TODO is not found, a 404 error is returned. 
    """
    todo_model: models.todos.Todos = db.query(models.todos.Todos).filter(models.todos.Todos.id == id).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail="TODO not found")
    return todo_model

@app.post("/todo/create", status_code=status.HTTP_201_CREATED)
async def create_todo(todo_request: TodoRequest, db: db_dependency):
    """
    Creates a new TODO in the database.

    This endpoint creates a new TODO in the database based on the data
    provided in the `todo_request` parameter. The `todo_request` parameter
    must be an instance of the `TodoRequest` model.
    """
    todo_model: models.todos.Todos = models.todos.Todos(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model


@app.put("/todo/update/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo( todo_request: TodoRequest, 
                      db: db_dependency,
                      id: int = Path(gt=0), ):
    """
    Updates a single TODO in the database.

    This endpoint updates a single TODO in the database based on the
    `todo_id` parameter. If the TODO is not found, a 404 error is returned.
    The `todo_request` parameter must be an instance of the `TodoRequest`
    model.
    """
    todo_model: models.todos.Todos = db.query(models.todos.Todos).filter(models.todos.Todos.id == id).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail="TODO not found")
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.completed = todo_request.completed
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model


@app.delete("/todo/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, id: int = Path(gt=0), ):
    """
    Deletes a single TODO from the database.

    This endpoint deletes a single TODO from the database based on the
    `todo_id` parameter. If the TODO is not found, a 404 error is returned.
    """
    todo_model: models.todos.Todos = db.query(models.todos.Todos).filter(models.todos.Todos.id == id).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail="TODO not found")
    db.delete(todo_model)
    db.commit()