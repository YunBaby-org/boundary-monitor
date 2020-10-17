from .amqphandler import CreateAMQPConnection
from .utility.getTrackerId import GetTrackerId
from .utility.getTrackerRoutingKey import GetRoutingKey
import logging,json
def start():

    #   Setup AMQP connection & channel 
    amqpconnection = CreateAMQPConnection()
    amqpchannel = amqpconnection.channel()

    #   consume boundary monitor queue 
    amqpchannel.basic_consume(queue='monitor.boundary',auto_ack=True,on_message_callback=OnPreConsume)
    amqpchannel.start_consuming()
    logging.info("AMQP connection established")

def OnPreConsume(ch, method, properties, body):
    try:
        OnConsume(ch,method,properties,body)
    except Exception as e :
        print(e)
        logging.error(e)
        logging.error('Failed to handle , message unacked')
        logging.error('Payload content: %s'%str(body))
        #   Todo
        #   nack this message 
        



#   AMQP message callback
#   handle comming message 
def OnConsume(ch, method, properties, body):
    data = json.loads(body)#type dict
    trackerId = GetTrackerId(method.routing_key)
    geodata = dict()
    #   check data format 
    if trackerId == None:
        raise Exception("Unknown tracker id ")
    
    #   handle only Geolocation message
    if data['Response'] == 'ScanGPS' or data['Response'] == 'ScanWifiSignal_Resolved':
        geodata['Longitude'] = data['Result']['Longitude'] 
        geodata['Latitude'] = data['Result']['Latitude']   

 
         
    
