from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, Boolean, DateTime, Float
from sqlalchemy import Column, Table, Enum
from .database import Base
from enums import OrderStatus
import datetime


# Define the association table for many-to-many relationship
group_membership = Table( 
    'group_membership', Base.metadata,
    Column('membership_id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('username', String),
    Column('group_id', Integer, ForeignKey('groups.id'))
)


class DbUser(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)

    # Explicitly define the foreign key relationship for friendships
    friendships = relationship("DbFriendship", back_populates="user", foreign_keys="[DbFriendship.user_id]")

    images = relationship ('DbUserImage', back_populates='user')

    posts = relationship('DbPost', back_populates='user', cascade="all, delete")

    # Many-to-Many relationship with groups
    groups = relationship("DbGroup", secondary=group_membership, back_populates="members")

    # One-to-Many relationship with group posts
    group_posts = relationship('DbGroupPost', back_populates='author')

    # Relationship with products
    products = relationship ('DbProduct', back_populates='user')

    # Relationship with review
    review = relationship ('DbProductReview', back_populates='creator_username')

    # Relationship with post likes
    post_likes = relationship('DbPostLike', back_populates='user', cascade="all, delete")

class DbUserImage(Base):
    __tablename__= 'user_image'
    id = Column (Integer, primary_key=True, index=True)
    file_path = Column (String)
    user_id = Column (Integer, ForeignKey('users.id'))
    user = relationship('DbUser', back_populates='images')

class DbFriendship(Base):
    __tablename__ = 'friendships'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    sender_username = Column(String)
    friend_id = Column(Integer, ForeignKey('users.id'))
    accepted = Column(Boolean, default=False)  # New field to indicate acceptance status

    user = relationship("DbUser", foreign_keys=[user_id], back_populates="friendships")
    friend = relationship("DbUser", foreign_keys=[friend_id], back_populates="friendships")
    

class DbPost(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    content = Column(String)
    timestamp = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))
    username = Column(String)

    user = relationship('DbUser', back_populates='posts')
    images = relationship ('DbPostImage', back_populates='post')
    comments = relationship('DbComment', back_populates= 'post', cascade="all, delete")
    likes = relationship('DbPostLike', back_populates='post', cascade="all, delete")


class DbPostImage(Base):
    __tablename__= 'post_image'
    id = Column (Integer, primary_key=True, index=True)
    file_path = Column (String)
    post_id = Column (Integer, ForeignKey('posts.id'))
    post = relationship('DbPost', back_populates='images')


class DbComment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    user_id = Column(Integer)
    username = Column(String)
    timestamp = Column(DateTime)
    post_id = Column(Integer, ForeignKey('posts.id'))
    
    post = relationship('DbPost', back_populates= 'comments')
    

class DbGroup(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    created_at = Column(DateTime)
    creator_id = Column(Integer, ForeignKey('users.id'))  
    is_public = Column(Boolean, default=True)
    visibility = Column(String, default="public")

    # One-to-Many relationship with group posts
    group_posts = relationship('DbGroupPost', back_populates='group', cascade="all, delete")

    # Define the 'members' attribute
    members = relationship("DbUser", secondary=group_membership, back_populates="groups")


class DbGroupPost(Base):
    __tablename__ = 'group_posts'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    created_at = Column(DateTime)
    

    author = relationship('DbUser', back_populates='group_posts')  # Many-to-One relationship with user
    group = relationship('DbGroup', back_populates='group_posts')

class DbProduct(Base):
    __tablename__= 'products'
    id = Column (Integer, primary_key=True, index=True)
    product_name = Column (String)
    description = Column (String)
    price = Column (Float)
    quantity = Column (Integer)
    published = Column (Boolean)
    seller_id = Column (Integer, ForeignKey('users.id'))
    user = relationship ('DbUser', back_populates='products')
    images = relationship ('DbProductImage', back_populates='product')
    reviews = relationship ('DbProductReview', back_populates='product')

class DbProductImage(Base):
    __tablename__= 'product_image'
    id = Column (Integer, primary_key=True, index=True)
    file_path = Column (String)
    product_id = Column (Integer, ForeignKey('products.id'))
    product = relationship('DbProduct', back_populates='images')

class DbOrder(Base):
    __tablename__= 'orders'
    id = Column (Integer, primary_key=True, index=True)
    order_status = Column (Enum(OrderStatus), default=OrderStatus.PENDING)
    user_id = Column (Integer, ForeignKey('users.id'))
    total = Column (Float)
    order_lines = relationship('DbOrderLine', back_populates='order')

class DbOrderLine(Base):
    __tablename__= 'order_lines'
    id = Column (Integer, primary_key=True, index=True)
    order_id = Column (Integer, ForeignKey('orders.id'))
    product_id = Column (Integer, ForeignKey('products.id'))
    quantity = Column (Integer)
    total = Column (Float)
    order = relationship('DbOrder', back_populates='order_lines')

class DbProductReview(Base):
    __tablename__= 'products_reviews'
    id = Column (Integer, primary_key=True, index=True)
    product_id = Column (Integer, ForeignKey('products.id'))
    score = Column (Integer)
    comment = Column (String)
    creator_id = Column (Integer, ForeignKey('users.id'))
    creator_username = relationship ('DbUser', back_populates='review')
    product = relationship ('DbProduct', back_populates='reviews')

#5a) Create a database model (table) for 'postlikes'
class DbPostLike(Base):
    __tablename__ = 'post_likes'

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.id')) # a reference to a post, indicating which post was liked
    user_id = Column(Integer, ForeignKey('users.id')) # a reference to the user, indicating who liked the post
    created_at = Column(DateTime, default=datetime.datetime.utcnow) # a datetime field, indicating when a like was created

    post = relationship('DbPost', back_populates='likes')
    user = relationship('DbUser', back_populates='post_likes')