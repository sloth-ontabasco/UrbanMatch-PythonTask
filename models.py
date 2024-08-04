from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship 
from database import Base

class user_interests(Base):
    __tablename__ = 'users_interests'
    user_id = Column( Integer, ForeignKey('users.id'),primary_key=True)
    interest_id = Column( Integer, ForeignKey('interests.id'),primary_key=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    email = Column(String, unique=True, index=True)
    city = Column(String, index=True)
    interests = relationship("Interest",secondary=user_interests.__tablename__,backref="users",uselist=False)

class Interest(Base):
    __tablename__ = "interests"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String,  index=True)
    user_id =Column( Integer,ForeignKey("users.id"))
