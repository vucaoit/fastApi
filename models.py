import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from database import Base

class User(Base):
#     String? id;
#   String? userName;
#   String? email;
#   String? password;
#   String? accountState;
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    email = Column(String, unique=True, index=True)
    userName = Column(String,unique=True,index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)

    items = relationship("Item", back_populates="owner")

class Profile(Base):
#     String? id;
#   Location? location;
#   String? userId;
#   String? firstName;
#   String? lastName;
#   String? gender;
#   DateTime? dateOfBirth;
#   String? aboutMe;
#   String? avatar;
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    userId = Column(Integer, unique=True,index=True)
    firstName = Column(String)
    lastName = Column(String)
    gender = Column(Integer)
    dateOfBirth = Column(DateTime, default=datetime.datetime.utcnow)
    aboutMe = Column(String)
    avatar = Column(String) #link table image
    location = relationship("Location", back_populates="id")

class Location(Base):
    __tablename__ = 'location'
    
    id = Column(String, primary_key=True)
    city = Column(String)
    state = Column(String)
    country = Column(String)

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")