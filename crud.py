from sqlalchemy import select
from sqlalchemy.orm import Session

import models
import schemas



def get_user_by_id(db: Session, id: int):
    return db.query(models.User).filter(models.User.id == id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.userName == username).first()

def is_email_exist(db: Session, email: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if(user):
        return True
    return False
    
def get_user_by_email(db: Session, email: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    profile = db.query(models.Profile).filter(models.Profile.email == email).first()
    user.profile = profile
    user.password = ""
    return user
def get_profile_by_email(db: Session, email: str):
    user = db.query(models.User).with_entities(models.User.id).filter(models.User.email == email).first()
    profile = db.query(models.Profile).filter(models.Profile.email == email).first()
    profile.user_id = user.id
    return profile

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    user1 = get_user(db,user.email)
    db_profile = models.Profile(email=user.email,user_id= user1.id, fullName=user.fullName,avatar = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Golden_retriever_eating_pigs_foot.jpg/170px-Golden_retriever_eating_pigs_foot.jpg")
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return get_user_by_email(db= db,email=user.email)


def get_user(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_profile(db: Session,email: str,fullName: str):
    db_profile = models.Profile(email = email,fullName = fullName,avatar = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Golden_retriever_eating_pigs_foot.jpg/170px-Golden_retriever_eating_pigs_foot.jpg")
    print(db_profile.avatar)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


# def get_items(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Item).offset(skip).limit(limit).all()


# def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
#     db_item = models.Item(**item.dict(), owner_id=user_id)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item