from typing import Any
from fastapi import FastAPI, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session, aliased
from database import SessionLocal, engine, Base
import models
import schemas

app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserBase, db: Session = Depends(get_db)):
    added_interests = []
    try:
        if user.interests:
            for interest in user.interests:
                interest_exists = db.query(models.Interest).filter(
                    models.Interest.name == interest.name).first()
                if interest_exists:
                    added_interests.append(interest_exists)

                    continue
                db_interest = models.Interest(name=interest.name)
                db.add(db_interest)
                db.commit()
                added_interests.append(db_interest)

        user_to_add = user.dict()
        user_to_add['interests'] = added_interests

        db_user = models.User(**user_to_add)
    except ValidationError:
        raise HTTPException(status_code=400, detail="Invalid Email")

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    for i in added_interests:
        i.user_id = db_user.id
    db.commit()

    db.refresh(db_user)
    return db_user


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 10,
               db: Session = Depends(get_db)):

    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, q: schemas.UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.age = q.age
    user.city = q.city
    user.email = q.email
    user.gender = q.gender
    user.name = q.name

    db.flush()
    db.commit()
    db.refresh(user)
    return user


@app.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return user


@app.get("/users/{user_id}/matches", response_model=list[schemas.User])
def get_user_matches(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    ul1 = aliased(models.user_interests)
    ul2 = aliased(models.user_interests)

    subq = (select(ul1.interest_id)
            .where(ul1.user_id == user.id)).subquery()

    q = select(ul2.user_id).join(
        subq, ul2.interest_id == subq.c.interest_id).where(ul2.user_id != user.id)

    matches = db.execute(q).all()
    res =[]
    for m in matches:
        res.append(db.query(models.User).filter(models.User.id == m[0]).first().__dict__)
    
    print(res)
    return res
