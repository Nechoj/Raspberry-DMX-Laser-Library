from optparse import OptionParser
from DmxFtdi import DmxFtdi
import time

#option parser
parser = OptionParser()
parser.add_option("-x", "--xcoord", dest="x", default = "0", help="x-coordiante of laser")
parser.add_option("-y", "--ycoord", dest="y", default = "0", help="y-coordiante of laser")
parser.add_option("-t", "--time", dest="time", default = "1", help="duration of laser pointing in seconds")
(options, args) = parser.parse_args()

x = int(options.x)
y = int(options.y)
count = int(options.time)*10

dmx = DmxFtdi()

dmx.setChannel(1,252) # DMX mode
dmx.setChannel(2,0) # pattern; 152 = horizontal line
dmx.setChannel(3,120) # zoom
dmx.setChannel(4,0) # rotation y
dmx.setChannel(5,0) # rotation x
dmx.setChannel(6,0)  # rotation z
dmx.setChannel(7,x)  # move to x position
dmx.setChannel(8,y)  # move to y position
dmx.setChannel(9,32)  # color: 16=red, 32=green, 48=yellow (both), 127=changing

for i in range(count): # repeat command every 1/10 sec
        dmx.send()
        time.sleep(0.1)

dmx.clearChannels()
dmx.send()
