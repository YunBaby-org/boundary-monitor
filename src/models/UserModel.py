from sqlalchemy import Column,String,Integer,DateTime,Float,SmallInteger
from sqlalchemy.ext.declarative import declarative_base 
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(String(50),primary_key=True) #boundary's id 
    username = Column(String(50))
    email = Column(String(50))
    phone = Column(String(10))
    password = Column(String(90))

