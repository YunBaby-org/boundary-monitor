import os 
import pika
from dotenv import load_dotenv 


#load env variable
load_dotenv()
def CreateAMQPConnection():
    #init amqp 
    connection = pika.BlockingConnection(pika.ConnectionParameters(os.getenv('RABBITMQ_HOST')))
    return connection
