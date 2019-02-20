import location
import gobject
import threading


class GPS_N900(threading.Thread, gobject.GObject):
    
    def __init__(self, fifo):
        threading.Thread.__init__(self)
        gobject.GObject.__init__(self)
        # Init gps
        self.loop = gobject.MainLoop()
        self.control = location.GPSDControl.get_default()
        self.device = location.GPSDevice()
        self.control.set_properties(preferred_method=location.METHOD_USER_SELECTED, preferred_interval=location.INTERVAL_DEFAULT)
        
        
        self.control.connect('error-verbose', self.on_error, self.loop)
        self.device.connect('changed', self.on_changed, self.control)
        self.control.connect('gpsd-stopped', self.on_stop, self.control)
        gobject.idle_add(self.start_location, self.control)
        
        # Output pipe
        self.fifo = fifo
        
    def run(self):
        
        self.loop.run()
    
    
    def stop(self):        
        print "Quitting GPS"
        
        self._Thread__stop()
        
    def on_error(self, error, data ):
        
        data.quit()
        
    def on_changed(self, device, data):
        
        # if self.stop_fifo.empty():
        #    pass
        #else:
        #   self.control.stop()
            
        if not device:
            return
        
        if device.fix:
            if device.fix[1] & location.GPS_DEVICE_LATLONG_SET:
                
                (lat, lon) = device.fix[4:6]
                
                
                self.fifo.put({"lat":lat, "lon":lon, "sat":device.satellites_in_use})
                
             

    def on_stop(self, control, data):
        
        print "Quitting..."
        data.quit()
        
    def start_location(self, data):
        
        data.start()
        return False



        
