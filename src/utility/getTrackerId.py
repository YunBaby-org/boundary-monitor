def GetTrackerId(routingKey):
    #Pattern: tracker.aaa96148.event.respond.ScanGPS
    data = routingKey.split('.')
    return data[1] if len(data)>=2 else None


