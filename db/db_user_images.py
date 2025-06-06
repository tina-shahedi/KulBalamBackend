from fastapi import HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm.session import Session 
from db.models import DbUser, DbUserImage
from fastapi import File, UploadFile
import shutil
import random, string

def upload_user_image(db: Session, user_id: int, image: UploadFile = File(...)):
    user = db.query(DbUser).filter(DbUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found")

    letters = string.ascii_letters
    rand_str = ''.join(random.choice(letters) for i in range(6)) #Generates 6 random letters for img name
    new = f'_{rand_str}.' #Adds the random letters to the file name
    filename = new.join(image.filename.rsplit('.', 1)) #Splits the prefix and adds name in the #1 index (0,1,2...)
    path = f'userimage/{filename}' #Folder path

    with open(path, 'wb') as buffer: #Saves the file in the path
        shutil.copyfileobj(image.file, buffer)

    new_image = DbUserImage(
        file_path=path,
        user_id=user_id
    )
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    return new_image

def get_user_image(db: Session, id: int):
    user_image = db.query(DbUserImage).filter(DbUserImage.user_id == id).first()
    if not user_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image of user id {id} not found."
        )
    return FileResponse(user_image.file_path)

def delete_user_image(db: Session, id: int):
    user_image = db.query(DbUserImage).filter(DbUserImage.id == id).first()
    if not user_image:
        raise HTTPException(status_code=404, detail=f"Image with id {id} not found")
    db.delete(user_image)
    db.commit()
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)