from optparse import OptionParser
from DmxFtdi import DmxFtdi
import time

#option parser
parser = OptionParser()
parser.add_option("-d", "--dev", dest="dev", default = "1", help="number of laser device")
parser.add_option("-x", "--xcoord", dest="x", default = "0", help="x-coordiante of laser")
parser.add_option("-y", "--ycoord", dest="y", default = "0", help="y-coordiante of laser")
parser.add_option("-t", "--time", dest="time", default = "1", help="duration of pointing in seconds")
(options, args) = parser.parse_args()

x = int(options.x)
y = int(options.y)
count = int(options.time)*10

dmx = DmxFtdi()

dmx.setChannel(1,252) # DMX Betrieb
dmx.setChannel(2,0) # Pattern
dmx.setChannel(3,120) # Zoom
dmx.setChannel(4,0) # Rotation um y
dmx.setChannel(5,0) # Rotation um x
dmx.setChannel(6,0)  # Rotation um z
dmx.setChannel(7,x)  # x-Achse
dmx.setChannel(8,y)  # y-Achse
dmx.setChannel(9,32)  # Farbe: 16=rot, 32=gruen, 48=gelb, 127=wechselnd

for i in xrange(1,count,1):
        dmx.send()
        time.sleep(0.1)

dmx.clearChannels()
dmx.send()
