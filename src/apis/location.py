import math,os,requests 
from dotenv import load_dotenv


def inboundary(target,boundary,radius):
    print(target)
    print(boundary)
    #   haversine formula 
    earthRadius = 6371000 # meters 
    dLat = float(math.radians(boundary["Latitude"]-target["Latitude"]))
    dLng = float(math.radians(boundary["Longitude"]-target["Longitude"]))
    a = float(math.sin(dLat/2)*math.sin(dLat/2)+math.cos(math.radians(target["Latitude"]))*math.cos(math.radians(boundary["Latitude"]))*math.sin(dLng/2)*math.sin(dLng/2))
    c = float(2*math.atan2(math.sqrt(a),math.sqrt(1-a)))
    dist = float(earthRadius*c)
    print('distance ',dist)
    return True if math.fabs(dist)<=radius else False


