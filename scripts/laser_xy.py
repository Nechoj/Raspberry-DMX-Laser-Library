from optparse import OptionParser
from DmxPro import DmxPro

#option parser
parser = OptionParser()
parser.add_option("-d", "--dev", dest="dev", default = "1", help="number of laser device")
parser.add_option("-x", "--xcoord", dest="x", default = "0", help="x-coordiante of laser")
parser.add_option("-y", "--ycoord", dest="y", default = "0", help="y-coordiante of laser")
(options, args) = parser.parse_args()

x = int(options.x)
y = int(options.y)

dmx = DmxPro('/dev/ttyUSB0')

dmx.setChannel(1,252) # DMX mode
dmx.setChannel(2,152) # pattern; 152 = horizontal line
dmx.setChannel(3,120) # zoom
dmx.setChannel(4,0) # rotation y
dmx.setChannel(5,0) # rotation x
dmx.setChannel(6,0)  # rotation z
dmx.setChannel(7,x)  # move to x position
dmx.setChannel(8,y)  # move to y position
dmx.setChannel(9,32)  # color: 16=red, 32=green, 48=yellow (both), 127=changing

dmx.send()
