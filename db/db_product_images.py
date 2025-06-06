from fastapi import HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm.session import Session 
from db.models import DbProduct, DbProductImage
from fastapi import File, UploadFile
import shutil
import random, string

def upload_product_image(db: Session, product_id: int, image: UploadFile = File(...)):
    product = db.query(DbProduct).filter(DbProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found")

    letters = string.ascii_letters
    rand_str = ''.join(random.choice(letters) for i in range(6)) #Generates 6 random letters for img name
    new = f'_{rand_str}.' #Adds the random letters to the file name
    filename = new.join(image.filename.rsplit('.', 1)) #Splits the prefix and adds name in the #1 index (0,1,2...)
    path = f'productimages/{filename}' #Folder path

    with open(path, 'wb') as buffer: #Saves the file in the path
        shutil.copyfileobj(image.file, buffer)

    new_image = DbProductImage(
        file_path=path,
        product_id=product_id
    )
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    return new_image

def get_product_image(db: Session, id: int):
    product_image = db.query(DbProductImage).filter(DbProductImage.id == id).first()
    if not product_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with id {id} not found."
        )
    return FileResponse(product_image.file_path)

def delete_product_image(db: Session, id: int):
    product_image = db.query(DbProductImage).filter(DbProductImage.id == id).first()
    if not product_image:
        raise HTTPException(status_code=404, detail=f"Image with id {id} not found")
    db.delete(product_image)
    db.commit()
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)