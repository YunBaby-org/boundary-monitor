def GetRoutingKey(trackerId):
    return 'tracker.%s.notification.escaped'%(trackerId)

