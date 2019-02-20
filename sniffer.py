import socket
import threading
import client

class Sniffer(threading.Thread):

    def __init__(self, fifo, fifo_gps, iface):
        threading.Thread.__init__(self)
        self.fifo = fifo
        self.fifo_gps = fifo_gps
        self.rawSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x003))
        self.iface = iface
        self.clients = {}

    def run(self):

        self.rawSocket.bind((self.iface, 0x003))

        while True:

            (self.lat, self.lon, self.sat) = self.checkGPS(self.fifo_gps)

            self.pkt = self.rawSocket.recvfrom(2048)[0]
                #subtype: 4
            if self.pkt[26] == "\x40":


                self.ssi_signal = int(self.pkt[22].encode('hex'),16)
                self.ssi_signal = -(256 - self.ssi_signal)
                self.length = int(self.pkt[51].encode('hex'), 16)
                self.ssid = self.pkt[52:52+self.length]
                if self.ssid.isalnum() == False:
                    self.ssid = "" 
                self.client_mac = self.pkt[36:42].encode('hex')

                self.client_mac = self.gen_mac(self.client_mac)

                if self.client_mac not in self.clients.keys(): # New mac

                    self.clients.update({self.client_mac:client.Client(self.client_mac, self.ssid, self.ssi_signal, self.lat, self.lon)})

                else: # Old mac, new ssid
                    if self.ssid not in self.clients.get(self.client_mac).ssid_list:

                        self.clients.get(self.client_mac).addSSID(self.ssid)
                    else:
                        self.clients.get(self.client_mac).updateTime()

                self.clients.get(self.client_mac).updateSignal(self.ssi_signal)
                self.clients.get(self.client_mac).updateProbeCount()
                if self.lat > 0 and self.lon > 0:
                    self.clients.get(self.client_mac).updateLocation()

                self.fifo.put(self.clients)

    def checkGPS(self, fifo):

        lat = 0
        lon = 0
        sat = 0
        if fifo.empty():
            pass
        else:

            data = fifo.get()

            lat = data.get('lat')
            lon = data.get('lon')
            sat = data.get('sat')
            # Put data back for main program in case gps data flow is slow
            self.fifo_gps.put(data)

        return (lat,lon,sat)

    def stop(self):
        print "Quitting sniffer"
        self.rawSocket.close()
        self._Thread__stop()

    def gen_mac(self,text):
        mac = ''
        for x in range(0,len(text)):
            if x % 2 == 1:
                mac += '%s:' % text[x]
            if x % 2 == 0:
                mac += text[x]

        return mac[0:len(mac)-1]
