from typing import List
from db.hash import Hash
from sqlalchemy.orm.session import Session 
from schemas import UserBase
from db.models import DbPost, DbUser
from fastapi import HTTPException, Response, status
from sqlalchemy.orm import joinedload

def create_user(db: Session, request:UserBase):
    new_user = DbUser(
        username = request.username,
        email = request.email,
        password = Hash.bcrypt(request.password)
    )
    db.add(new_user)  
    db.commit() 
    db.refresh(new_user) 
    return new_user

def get_all_user(db:Session):
    return db.query(DbUser).all() 

def get_user(db:Session, id:int):
    user= db.query(DbUser).filter(DbUser.id == id).first() 
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail= f'User with id {id} not found')  
    return user

def get_username(db: Session, user_id: int):
    user = db.query(DbUser).filter(DbUser.id == user_id).first()
    if user:
        return user.username
    return None

def get_user_by_username(db:Session, username: str):
    user= db.query(DbUser).filter(DbUser.username == username).first() 
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail= f'User with username {username} not found') 
    return user


def update_user(db: Session, id:int, request:UserBase):
    user = db.query(DbUser).filter(DbUser.id == id)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail= f'User with id {id} not found')  
    user.update({
        DbUser.username: request.username,
        DbUser.email: request.email,
        DbUser.password: Hash.bcrypt(request.password)
    })
    db.commit()
    user = db.query(DbUser).filter(DbUser.id == id).first()
    return user

def delete_user(db:Session, id: int):
    user =  db.query(DbUser).filter(DbUser.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail= f'User with id {id} not found') 
    db.delete(user)
    db.commit()
    return Response(status_code=204)

def get_product_by_user_id (db: Session, id: int):
    user = db.query(DbUser).filter(DbUser.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{id}' not found."
        )
    return user

def get_posts_by_user_id(db: Session, id: int):
    user = db.query(DbUser).filter(DbUser.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{id}' not found."
        )
    # Return posts with likes eagerly loaded
    return db.query(DbUser).filter(DbUser.id == id).first().posts

def count_all_users(db: Session) -> int:
    return db.query(DbUser).count()