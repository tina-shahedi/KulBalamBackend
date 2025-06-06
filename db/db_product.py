from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm.session import Session 
from db.models import DbProduct
from schemas import ProductBase, TestProductBase

def test_products(db: Session, request: TestProductBase, user_id):
    new_product = DbProduct(
        product_name=request.product_name, 
        description=request.description,
        price=request.price,
        quantity=request.quantity,
        seller_id=user_id,
        published=request.published
    )
    db.add(new_product) 
    db.commit()
    db.refresh(new_product)
    return new_product

def insert_product (db: Session, request: ProductBase, user_id):
    new_product = DbProduct(
        product_name = request.product_name, 
        description = request.description,
        price = request.price,
        quantity = request.quantity,
        seller_id = user_id,
        published = request.published
    )
    db.add(new_product) 
    db.commit()
    db.refresh(new_product)
    return new_product

def get_all_products (db: Session, nameFilter: str, user_id: Optional[int]=None, price_order: Optional[str]=None) -> List[DbProduct]:
    productsQuery = db.query(DbProduct)
    if(nameFilter != ''):
        productsQuery = productsQuery.filter(DbProduct.product_name.icontains(nameFilter))
    if(user_id):
        productsQuery = productsQuery.filter(DbProduct.seller_id == user_id)
    if price_order == 'asc':
        productsQuery = productsQuery.order_by(DbProduct.price.asc())
    if price_order == 'desc':
        productsQuery = productsQuery.order_by(DbProduct.price.desc())
    return productsQuery.all()

def count_all_products(db: Session) -> int: 
    return db.query(DbProduct).count()

def get_product_by_id(db: Session, id: int):
    product = db.query(DbProduct).filter(DbProduct.id == id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Product with id {id} not found.'
        )
    return product

def update_product(db: Session, id: int, product_name: str, description: str, price: float, quantity: int):
    product = db.query(DbProduct).filter(DbProduct.id == id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Product with id {id} not found.'
        )

    product.product_name = product_name
    product.description = description
    product.price = price
    product.quantity = quantity
    db.commit()
    return product

def delete_product(db: Session, id: int, current_user_id: int):
    product = db.query(DbProduct).filter(DbProduct.id == id).first()
    if product is None:
        raise HTTPException(status_code=404, detail=f'Product with id {id} not found')
    if product.seller_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to delete this product")
    db.delete(product)
    db.commit()
    return HTTPException(status_code=status.HTTP_204_NO_CONTENT)