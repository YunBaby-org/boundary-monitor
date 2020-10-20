from .amqphandler import CreateAMQPConnection
from .utility.getTrackerId import GetTrackerId
from .utility.getTrackerRoutingKey import GetRoutingKey
from .models import DBsession
from .models.BoundaryModel import Boundary
from .apis.location import inboundary
from sqlalchemy import text
import logging,json,pytz,datetime 

class Application():
    def start(self):
        #   Setup PostgreSQL connection 
        self.session = DBsession()
        logging.info("PostgreSQL connection established")
        #   Setup AMQP connection & channel 
        self.amqpconnection = CreateAMQPConnection()
        self.amqpchannel = self.amqpconnection.channel()

        #   consume boundary monitor queue 
        self.amqpchannel.basic_consume(queue='monitor.boundary',on_message_callback=self.OnPreConsume)
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

        
        #   query target's boundary information by current time
        current_time = datetime.datetime.now(pytz.timezone('Asia/Taipei')).strftime("%Y-%m-%d %H:%M:%S%z")
      
        query_data = self.session.query(Boundary).filter(
            text("tracker_id=:trackerid and :current>=time_start and :current<=time_end")
        ).params(trackerid=trackerId,current=str(current_time)).one()


        
        print('target in boundary? ',inboundary(geodata,{"Longitude":query_data.lng,"Latitude":query_data.lat},query_data.radius))
        ch.basic_ack(delivery_tag = method.delivery_tag)

        
 
        
