#I created a new router post_likes.py with endpoints POST /post-likes/{post_id}/like & DELETE /post-likes/{post_id}/unlike

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db import models
from typing import List
from schemas import PostDisplay
from auth.oauth2 import get_current_user

router = APIRouter(
    prefix='/post-likes',
    tags=['post-likes']
)

# 5b) A user should be able to 'like' another users posts (not his own)
@router.post('/{post_id}/like')
def like_post(post_id: int, db: Session = Depends(get_db), current_user: models.DbUser = Depends(get_current_user)):
    # Check if post exists
    post = db.query(models.DbPost).filter(models.DbPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user is trying to like their own post
    if post.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot like your own post")
    
    # Check if like already exists
    existing_like = db.query(models.DbPostLike).filter(
        models.DbPostLike.post_id == post_id,
        models.DbPostLike.user_id == current_user.id
    ).first()
    
    if existing_like:
        raise HTTPException(status_code=400, detail="Post already liked")
    
    # Create new like
    new_like = models.DbPostLike(
        post_id=post_id,
        user_id=current_user.id
    )
    
    db.add(new_like)
    db.commit()
    db.refresh(new_like)
    
    return {"message": "Post liked successfully"}

#5c) A user should be able to 'unlike' any post he has an active 'like' on.
@router.delete('/{post_id}/unlike')
def unlike_post(post_id: int, db: Session = Depends(get_db), current_user: models.DbUser = Depends(get_current_user)):
    # Check if like exists
    like = db.query(models.DbPostLike).filter(
        models.DbPostLike.post_id == post_id,
        models.DbPostLike.user_id == current_user.id
    ).first()
    
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
    
    db.delete(like)
    db.commit()
    
    return {"message": "Post unliked successfully"}

def get_post_with_likes(post: models.DbPost, current_user_id: int = None) -> PostDisplay:
    """Helper function to convert a DbPost to PostDisplay with like information"""
    like_count = len(post.likes)
    is_liked = False
    if current_user_id:
        is_liked = any(like.user_id == current_user_id for like in post.likes)
    
    return PostDisplay(
        id=post.id,
        content=post.content,
        user=post.user,
        user_id=post.user_id,
        images=post.images,
        timestamp=post.timestamp,
        like_count=like_count,
        is_liked_by_current_user=is_liked
    ) 