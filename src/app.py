from .amqphandler import CreateAMQPConnection
from .redishandler import CreateRedisConnection
from .utility.getTrackerId import GetTrackerId
from .utility.getTrackerRoutingKey import GetRoutingKey
from .models import DBsession
from .models.BoundaryModel import Boundary
from .models.TrackerModel import Tracker
from .models.UserModel import User
from .apis.location import inboundary
from .apis.message import SendSMS
from sqlalchemy import text
import logging,json,pytz,datetime,redis 

class Application():
    def start(self):
        #   Setup PostgreSQL connection 
        self.session = DBsession()
        logging.info("PostgreSQL connection established")
       
        #   Setup Redis 
        self.redisPool = CreateRedisConnection()
        self.r = redis.Redis(connection_pool=self.redisPool,decode_responses=True)

        #   Setup AMQP connection & channel 
        self.amqpconnection = CreateAMQPConnection()
        self.amqpchannel = self.amqpconnection.channel()


        #   consume boundary monitor queue 
        self.amqpchannel.basic_consume(queue='monitor.boundary',on_message_callback=self.OnPreConsume)
        logging.info('--------Start Consuming--------')
        self.amqpchannel.start_consuming()

  
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
        
        logging.info('--------Consuming Message from queue--------')
        data = json.loads(body)#type dict
        
        trackerId = GetTrackerId(method.routing_key)
        geodata = dict()
        
        #   check data format 
        if trackerId == None:
            raise Exception("Unknown tracker id ")
        
        #   handle only Geolocation message & ScanWifiSignal_Resolved
        if not((data['Response'] == 'ScanGPS' and data['Status']=='Success') or data['Response'] == 'ScanWifiSignal_Resolved'):
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return 
        
        message_type = data['Response']
        logging.info("this message type is "+message_type)

        #   如果收到的是WIFI定位的結果，若誤差太大我們直接丟掉
        if message_type == 'ScanWifiSignal_Resolved':
            if data['Result']['Radius'] >= 30:
                ch.basic_ack(delivery_tag = method.delivery_tag)
                logging.info('Geolocation API 誤差太大 不使用')
                return 
            geodata['Radius'] = data['Result']['Radius'] 

        geodata['Longitude'] = data['Result']['Longitude'] 
        geodata['Latitude'] = data['Result']['Latitude']         
        logging.info('type: '+message_type+' msg: '+trackerId+' '+str(geodata))

        current_time = datetime.datetime.now(pytz.timezone('Asia/Taipei')).strftime("%Y-%m-%d %H:%M:%S%z")

        #   查詢現在時段所用的電子圍籬
        try:
            boundaryInfo = self.session.query(Boundary).filter(
                text("tracker_id=:trackerid and :current>=time_start and :current<=time_end")
            ).params(trackerid=trackerId,current=str(current_time)).one()
        except Exception as e:
            #   該目標沒有設定電子圍籬
            logging.error('boundary query error')
            logging.error(e)
            logging.warning(trackerId+' no boundary currently')
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return ;

        #   查詢該tracker的資訊
        trackerInfo = self.session.query(Tracker).filter(text("id=:trackerid")).params(trackerid=trackerId).one()


        #   查詢這個tracker的監護人
        ownerInfo = self.session.query(User).filter(text("id=:userid")).params(userid=trackerInfo.user_id ).one()
        
        # message_type ==> ScanGPS 
        #              ==> ScanWifiSignal_Resolved
        if inboundary(geodata,{"Longitude":boundaryInfo.lng,"Latitude":boundaryInfo.lat},boundaryInfo.radius,message_type):
            logging.warning('目標在電子圍籬範圍內')
            self.r.set(trackerId,0)
        else:            
            if self.r.get(trackerId) == None:
                self.r.set(trackerId,0)
            
            if self.r.get(trackerId) == '0':
                #   send SMS message to owner of this tracker 
                msg = trackerInfo.tkrname + ' 已走出電子圍籬範圍，請盡速上本系統查看。'
                retv = SendSMS(ownerInfo.phone,msg)
                logging.warning('已超出範圍 並寄送簡訊')
            else: 
                logging.warning('已超出範圍 但不寄送簡訊')
                
            self.r.incr(trackerId,amount=1)
            if self.r.get(trackerId) == '10':
                self.r.set(trackerId,0)

            #   傳送訊息(超出範圍)給frontend 
            self.amqpchannel.basic_publish(exchange='tracker-event',routing_key='tracker.'+trackerId+'.notification.escaped',body=trackerInfo.tkrname + ' 超出電子圍籬範圍!')
  
        ch.basic_ack(delivery_tag = method.delivery_tag)


