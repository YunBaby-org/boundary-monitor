import os ,redis,logging
from dotenv import load_dotenv 


#load env variable
load_dotenv()
def CreateRedisConnection():
    #init redis
    pool = redis.ConnectionPool(host=os.getenv('REDIS_HOST'),port=6379,decode_responses=True)

    logging.info('Redis pool ok')
    return pool

