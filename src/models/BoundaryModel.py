from . import session
from sqlalchemy import Column,String,Integer,DateTime,Float,SmallInteger
from sqlalchemy.ext.declarative import declarative_base 
Base = declarative_base()

class Boundary(Base):
    __tablename__ = 'boundary'
    id = Column(String(50),primary_key=True) #boundary's id 
    tracker_id = Column(String(50))
    time_start = Column(DateTime())
    time_end = Column(DateTime())
    lat = Column(Float())
    lng = Column(Float())
    radius = Column(SmallInteger())

    def insert(self):#for testing 
        session.add(self)
        session.commit()