from typing import List
from db.db_friendship import get_friendship_by_user
from schemas import PostDisplay, UserBase,UserDisplay, UserProductDisplay, Friendship, UserImage, ImageInUser
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm.session import Session
from db.database import get_db
from db import db_user, db_user_images
from auth.oauth2 import get_current_user
from db.models import DbFriendship
from router.post_likes import get_post_with_likes

#User router

router = APIRouter(
    prefix= '/users',
    tags=['user']
)

#Create User
@router.post('/', response_model=UserDisplay)
def create_user(request: UserBase, db: Session = Depends(get_db)):
    return db_user.create_user(db, request)

#Inert image
@router.post('/{id}/images', response_model=UserImage)
def upload_profile_image(id: int, image: UploadFile = File(...), db: Session = Depends (get_db)):
    return db_user_images.upload_user_image(db, id, image)

@router.get('/{id}/userimage')
def get_image(id: int, db: Session = Depends (get_db)):
    return db_user_images.get_user_image(db, id)

#Read All Users
@router.get('', response_model=List[UserDisplay])
def get_all_users(db: Session= Depends(get_db)):
    return db_user.get_all_user(db)

#Read a user
@router.get('/{id}', response_model=UserDisplay)
def get_user(id: int, db:Session =  Depends(get_db)):
    return db_user.get_user(db, id)

#Update User
@router.put('/{id}', response_model=UserDisplay)
def update_user(id: int, request:UserBase, db:Session = Depends(get_db)):
    return db_user.update_user(db, id, request)

# Delete User
@router.delete('/{id}')
def delete_user(id:int, db:Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    return db_user.delete_user(db, id)

@router.get("/{id}/posts", response_model=List[PostDisplay])
def get_posts_by_user(id: int, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    posts = db_user.get_posts_by_user_id(db, id)
    return [get_post_with_likes(post, current_user.id) for post in posts]

#Get product by user id
@router.get('/{id}/products', response_model=UserProductDisplay)
def get_product_by_user_id (id: int, db: Session = Depends (get_db)):
    return db_user.get_product_by_user_id (db, id)

@router.get("/{id}/friends", response_model=List[Friendship])
def get_friends(id: int, db: Session = Depends(get_db)):
    """Get a list of friendships for a given user."""
    friendships = db.query(DbFriendship).filter(
        (DbFriendship.user_id == id)
    ).all()
    
    all_friendships = []
    is_accepted = False
    for friendship in friendships:
        if friendship.user_id == id:
            friendship_list= get_friendship_by_user(db, friendship.user_id, friendship.friend_id)
            for friendship_l in friendship_list:
                if friendship_l.accepted == 1:
                    is_accepted = True
                else:
                     raise HTTPException(status_code=400, detail="No friend found.")

        else:
            raise HTTPException(status_code=400, detail="something went wrong.")
        if  is_accepted:
            all_friendships.append({
                    "user_id": friendship.user_id,
                    "friend_id": friendship.friend_id,
                    "id": friendship.id,
                    "sender_username": friendship.sender_username
                })
    
    return all_friendships
