from gps import *
import threading

class GPS(threading.Thread):
        
    def __init__(self, fifo):
        threading.Thread.__init__(self)
        self.gpsd = gps(mode=WATCH_ENABLE)
        self.fifo = fifo
   
    def run(self):
        
        while True:
            self.gpsd.next()
            self.fifo.put({"lat":self.gpsd.fix.latitude, "lon":self.gpsd.fix.longitude, "sat":self.gpsd.satellites})
    
    def stop(self):        

        self._Thread__stop()
        
        
