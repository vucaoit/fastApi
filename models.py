import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    email = Column(String, unique=True, index=True)
    userName = Column(String,unique=True,index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    profile = relationship("Profile", uselist=False)

class Profile(Base):
    __tablename__ = "profiles"
    email = Column(String,ForeignKey(User.email),primary_key = True)
        # nid = Column(Integer, ForeignKey(Node.nid), primary_key=True)
    fullName = Column(String)
    gender = Column(Integer)
    dateOfBirth = Column(DateTime, default=datetime.datetime.utcnow)
    aboutMe = Column(String)
    avatar = Column(String) #link table image

class Location(Base):
    __tablename__ = 'location'
    
    id = Column(String, primary_key=True)
    city = Column(String)
    state = Column(String)
    country = Column(String)