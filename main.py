#!/usr/bin/python2
import curses
import Queue
import sniffer
import time
import platform
import sys
import logging

logging.basicConfig(filename='clientSniffer.log',level=logging.INFO, 
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s %(levelname)-8s %(message)s')

class TUI:

    OS = ""
    CLIENTS = {}
    MODE_LIST = ['DEFAULT', 'GPS']
    OUTPUT_MODE = "DEFAULT"
    GPS = False
    IFACE = ""
    LAT = 0
    LON = 0
    SATELLITES = 0

    def __init__(self,iface):
        
        logging.info("TUI initialized")
       
       # Detect Nokia  N900 power kernel -> N900 does not use gpsd
        if 'power' in platform.release():
            from gpsN900 import GPS
            self.OS = "N900"
        else:
            from gpsGPSD import GPS
            self.OS = "LINUX"

        logging.info("Using: %s", self.OS)
        self.iface = iface

        self.fifo_gps = Queue.Queue()
        self.fifo_sniffer = Queue.Queue()
        
        self.window = curses.initscr()
        curses.noecho()
        # hide cursor (instant crash)
        # curses.curs_set(0)
        self.window.nodelay(1)
        
        try:
            self.sniffer = sniffer.Sniffer(self.fifo_sniffer, self.fifo_gps, self.iface)
            self.sniffer.start()
            #if 'LINUX' in OS:
             #   gps_thread = GPS(fifo_gps)
            #if 'N900' in OS:
            #    gps_thread = GPS(fifo_gps)
              #  gps_thread.start()

               # GPS = True

            while True:
                ch = self.window.getch()
                self.handleOutputMode(ch)
               
               # if 'LINUX' in OS:
                #    handleGPSMode(ch, gps_thread)

                self.handleSnifferdata() # Handle received data

        except KeyboardInterrupt:
            curses.echo()
            curses.nocbreak()
            curses.endwin()
            self.sniffer.stop()
        except:
            curses.echo()
            curses.nocbreak()
            curses.endwin()
            self.sniffer.stop()
            raise

    def handleGPSdata(self):
        
        if self.fifo_gps.empty():
            pass

        else:
            data = self.fifo_gps.get()
            self.LAT = data.get('lat')
            self.LON = data.get('lon')
            self.SATELLITES = data.get('sat')


    def handleSnifferdata(self):

        if self.fifo_sniffer.empty():
            pass
        else:
            self.CLIENTS = self.fifo_sniffer.get()
        self.init_output()

    def get_client_keys(self, clients):

        # Output last 10 clients, otherwise curses will crash.

        keys = []
        if 10 >= len(clients) > 0:

            raw = sorted(clients.items(), key=lambda x: x[1].lasttime)
            for x in range(len(raw)):

                keys.append(raw[x][0])

            return keys[::-1]

        if len(clients) > 10:

            raw = sorted(clients.items(), key=lambda x: x[1].lasttime)[len(clients)-10:]
            for x in range(len(raw)):

                keys.append(raw[x][0])

        return keys[::-1]

    def parse_probes(self, probe_list):
        
        probe_string = ""

        # Remove empty probes
        for x in probe_list:
            if len(x) ==  0:
                probe_list.remove(x)
        # Generate vertical string
        for x in probe_list:
            probe_string += x +", "

        return probe_string[:-2]


    def default_output(self, keys):

        output = ''
        if self.GPS == True:
            output += '[Default] [GPS ON]\n'
        else:
            output += '[Default] [GPS OFF]\n'
        output += '-' * 70 + "\n"
        output += '%-4s | %-13s [%d] | %-3s | %-4s | %s\n' % ("Id", "Clients", len(self.CLIENTS), "-dBm", "Count", "Probes")
        output += '-' * 70 + "\n"

        for key in keys:

            probes = self.parse_probes(self.CLIENTS.get(key).ssid_list)

            output += "%-4d | %-12s | %-4s | %-5d | %s \n" % (self.CLIENTS.get(key).client_id, self.CLIENTS.get(key).mac, self.CLIENTS.get(key).ssi_signal,self.CLIENTS.get(key).probe_count, probes)

        try:

            self.window.addstr(1,0,output)
            self.window.refresh()
        except TypeError:
            logging.error("Could not refresh the window")


    def gps_output(self,keys):

        output = ''
        if self.LON > 0 and self.LAT > 0 and self.SATELLITES > 0:
            output += '[GPS] [Lat: %f Lon:%f Satellites:%d]\n' % (self.LAT, self.LON, self.SATELLITES)
        else:
            output += '[GPS] [No GPS data]\n'
        output += '-' * 70 + "\n"
        output += '%-4s | %-15s | %-15s | %-15s | %s\n' % ("Id", "First location", "Last location", "Best location", "Probes")
        output += '-' * 70 + "\n"


        for key in keys:

            probes = self.parse_probes(self.CLIENTS.get(key).ssid_list)
            if len(probes) == 0:
                ssid_count = 0
            else:
                ssid_count = len(probes.split(","))

            first = self.gen_time_dist_signal_string(int(time.time() - self.CLIENTS.get(key).firsttime), self.CLIENTS.get(key).firstsignal)
            last =  self.gen_time_dist_signal_string(int(time.time() - self.CLIENTS.get(key).lasttime), self.CLIENTS.get(key).ssi_signal)
            best = self.gen_time_dist_signal_string(int(time.time() - self.CLIENTS.get(key).besttime),self.CLIENTS.get(key).bestsignal)


            output += "%-4d | %-13s | %-13s | %-13s | %d \n" % (self.CLIENTS.get(key).client_id, first , last , best, ssid_count)

        try:

            self.window.addstr(1,0,output)
            self.window.refresh()
        except TypeError:
            logging.error("Could not refresh the window")

    def gen_time_dist_signal_string(self, sec, signal):

        string = ''
        string += '[%s]' % time.strftime('%H:%M:%S', time.gmtime(sec))
        string += '[%s]' % signal
        return string

    def init_output(self):

        keys = self.get_client_keys(self.CLIENTS)

        if 'DEFAULT' in self.OUTPUT_MODE:
            self.default_output(keys)
        if 'GPS' in self.OUTPUT_MODE:
            self.gps_output(keys)

    def handleOutputMode(self, ch):

        if ch == ord('m'):

            if self.MODE_LIST.index(self.OUTPUT_MODE) + 1 == len(self.MODE_LIST):
                self.OUTPUT_MODE = self.MODE_LIST[0]
            else:
                self.OUTPUT_MODE = self.MODE_LIST[self.MODE_LIST.index(self.OUTPUT_MODE) + 1]

    def handleGPSMode(self, ch, gps_thread):

        if ch == ord('g') and 'LINUX' in self.OS:

            if self.GPS == True:

                # Turn gps off
                self.GPS = False
                gps_thread.stop()
            else:
                # Turn gps on
                self.GPS = True
                gps_thread.start()

def printHelp():

    print "Usage: %s <interface>" % (sys.argv[0])


if __name__=='__main__':

    if len(sys.argv) < 2:
        print "Missing interface"
        printHelp()
        sys.exit(0)

    iface = sys.argv[1]
    TUI(iface)

