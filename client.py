import time

class Client:
    
    client_id = 0
    
    def __init__(self, mac, first_ssid, ssi_signal,lat=None, lon=None ):
        
        self.probe_count = 1;
        self.firstlat = lat
        self.firstlon = lon
        self.lastlat = self.firstlat
        self.lastlon = self.firstlon
        
        self.firstsignal = ssi_signal
        self.bestsignal = ssi_signal
        self.bestlat = self.firstlat
        self.bestlon = self.firstlon
        
        self.ssi_signal = ssi_signal
        self.ssid_list = []
        self.mac = mac
        self.ssid = first_ssid
        self.firsttime = time.time()
        self.lasttime = time.time()
        self.besttime = time.time()
        
        self.client_id = Client.client_id
        Client.client_id += 1
        
        
        self.ssid_list.append(self.ssid)
        
        
    def addSSID(self, ssid):
      
        self.ssid = ssid
        self.ssid_list.append(self.ssid)
        
    def updateTime(self):
        
        self.lasttime = time.time()
        
    def updateLocation(self, lat, lon):
        
        self.lastlat = lat
        self.lastlon = lon
    
    def updateSignal(self, signal):
        self.ssi_signal = signal
        
        # Update bestsignal and coordinates
        if self.ssi_signal > self.bestsignal:
            
            self.bestsignal = self.ssi_signal
            self.bestlat = self.lastlat
            self.bestlon = self.lastlon
            self.besttime = self.lasttime
        
    def updateProbeCount(self):
        
        self.probe_count += 1
        
        
        
