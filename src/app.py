from .amqphandler import CreateAMQPConnection
from .utility.getTrackerId import GetTrackerId
from .utility.getTrackerRoutingKey import GetRoutingKey
from .models import DBsession
from .models.BoundaryModel import Boundary
from .models.TrackerModel import Tracker
from .models.UserModel import User
from .apis.location import inboundary
from .apis.message import SendSMS
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

            

    #   AMQP message callback
    def OnConsume(self,ch, method, properties, body):
        data = json.loads(body)#type dict
        trackerId = GetTrackerId(method.routing_key)
        geodata = dict()
        
        #   check data format 
        if trackerId == None:
            raise Exception("Unknown tracker id ")
        
        #   handle only Geolocation message
        if not(data['Response'] == 'ScanGPS' or data['Response'] == 'ScanWifiSignal_Resolved'):
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return 

        geodata['Longitude'] = data['Result']['Longitude'] 
        geodata['Latitude'] = data['Result']['Latitude']         
        print(trackerId+' '+str(geodata))
      
        current_time = datetime.datetime.now(pytz.timezone('Asia/Taipei')).strftime("%Y-%m-%d %H:%M:%S%z")

        try:
            boundaryInfo = self.session.query(Boundary).filter(
                text("tracker_id=:trackerid and :current>=time_start and :current<=time_end")
            ).params(trackerid=trackerId,current=str(current_time)).one()
            print('----------------------------------------')
            print(boundaryInfo.id,boundaryInfo.lat,boundaryInfo.lng,boundaryInfo.radius)
        except Exception as e:
            #   no boundary's info(stop directly)
            logging.warning(trackerId+' no boundary currently')
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return ;

        #   query this tracker's info
        trackerInfo = self.session.query(Tracker).filter(text("id=:trackerid")).params(trackerid=trackerId).one()


        # query the owner of this tracker (we need owner's phone number to send SMS message )
        ownerInfo = self.session.query(User).filter(text("id=:userid")).params(userid=trackerInfo.user_id ).one()
        
       
        if inboundary(geodata,{"Longitude":boundaryInfo.lng,"Latitude":boundaryInfo.lat},boundaryInfo.radius):
            print('在範圍內')
        else:
            #   send SMS message to owner of this tracker 
            msg = trackerInfo.tkrname + ' 已超出電子圍籬範圍'
            retv = SendSMS(ownerInfo.phone,msg)
            print('已超出範圍 並寄送簡訊')
  
        ch.basic_ack(delivery_tag = method.delivery_tag)