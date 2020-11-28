import math,os,requests,logging
from dotenv import load_dotenv

def Haversine(target,boundary):
    #   haversine formula 
    earthRadius = 6371000 # meters 
    dLat = float(math.radians(boundary["Latitude"]-target["Latitude"]))
    dLng = float(math.radians(boundary["Longitude"]-target["Longitude"]))
    a = float(math.sin(dLat/2)*math.sin(dLat/2)+math.cos(math.radians(target["Latitude"]))*math.cos(math.radians(boundary["Latitude"]))*math.sin(dLng/2)*math.sin(dLng/2))
    c = float(2*math.atan2(math.sqrt(a),math.sqrt(1-a)))
    dist = float(earthRadius*c) 
    return math.fabs(dist)

def inboundary(target,boundary,radius,message_type):
    if message_type == 'ScanGPS':#  GPS
        dist = Haversine(target,boundary)
        logging.info('msg type: '+message_type+' distance: '+str(dist)+' radius: '+str(radius))
        return True if dist<=radius else False

    elif message_type == 'ScanWifiSignal_Resolved':#    WIFI from GeoAPI
        dist = Haversine(target,boundary)
        logging.info('msg type: '+message_type+' distance: '+str(dist)+' radius: '+str(radius))
        return True if (dist-target["Radius"])<=radius else False

