#userid username email password phone address
from . import session
from sqlalchemy import Column,String,Integer
from sqlalchemy.ext.declarative import declarative_base 
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    userid = Column(String(100),primary_key=True)
    username = Column(String(100))
    email = Column(String(100))
    password = Column(String(100))
    phone = Column(String(100))
    address = Column(String(100))

    def insert(self):
        session.add(self)
        session.commit()