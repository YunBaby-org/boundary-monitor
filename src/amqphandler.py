import os ,pika,logging
from dotenv import load_dotenv 


#load env variable
load_dotenv()
def CreateAMQPConnection():
    #init amqp 
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST'),port=os.getenv('RABBITMQ_PORT')))
    logging.info('AMQP connection established')
    return connection

