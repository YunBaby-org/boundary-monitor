from sqlalchemy import Column,String,Integer,DateTime,Float,SmallInteger
from sqlalchemy.ext.declarative import declarative_base 
Base = declarative_base()

class Tracker(Base):
    __tablename__ = 'trackers'
    id = Column(String(50),primary_key=True) #boundary's id 
    tkrname = Column(String(50))
    phone = Column(String(10))
    user_id = Column(String(50))


