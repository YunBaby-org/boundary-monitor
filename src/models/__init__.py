from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv 
load_dotenv()


engine = create_engine('postgresql://%s:%s@%s/postgres'%(os.getenv("DB_USER"),os.getenv("DB_PASS"),os.getenv("DB_HOST")),echo=False)
DBsession = sessionmaker(bind=engine)

#session = DBsession()
