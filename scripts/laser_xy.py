from optparse import OptionParser
from Laser import LaserManagement

LM = LaserManagement()

#option parser
parser = OptionParser()
parser.add_option("-l", "--laser", dest="l", default = "1", help="number of laser")
parser.add_option("-x", "--xcoord", dest="x", default = "0", help="x-coordiante of laser")
parser.add_option("-y", "--ycoord", dest="y", default = "0", help="y-coordiante of laser")
(options, args) = parser.parse_args()

l = int(options.l)
x = int(options.x)
y = int(options.y)

# move laser to position
LM.Move(x,y,l)
