from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine('postgresql://postgres:toby5566@localhost/postgres',echo=True)
DBsession = sessionmaker(bind=engine)
session = DBsession()
