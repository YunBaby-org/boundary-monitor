from .amqphandler import CreateAMQPConnection
from .utility.getTrackerId import GetTrackerId
from .utility.getTrackerRoutingKey import GetRoutingKey
from .models import DBsession
from .models.BoundaryModel import Boundary
import logging,json

class Application():
    def start(self):
        #   Setup PostgreSQL connection 
        self.session = DBsession()
        logging.info("PostgreSQL connection established")
        #   Setup AMQP connection & channel 
        self.amqpconnection = CreateAMQPConnection()
        self.amqpchannel = self.amqpconnection.channel()

        #   consume boundary monitor queue 
        self.amqpchannel.basic_consume(queue='monitor.boundary',auto_ack=True,on_message_callback=self.OnPreConsume)
        self.amqpchannel.start_consuming()
        logging.info("AMQP connection established")

    def OnPreConsume(self,ch, method, properties, body):
        try:
            self.OnConsume(ch,method,properties,body)
        except Exception as e :
            print(e)
            logging.error(e)
            logging.error('Failed to handle , message unacked')
            logging.error('Payload content: %s'%str(body))
            #   Todo
            #   nack this message 
            

    #   AMQP message callback
    #   handle comming message 
    def OnConsume(self,ch, method, properties, body):
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
        print(geodata)
        
        #   Get this tracker's current boundary
        
 
        
