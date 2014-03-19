from optparse import OptionParser
from Laser import Laser_Stairville__150_RGY

L = Laser_Stairville__150_RGY(0)

#option parser
parser = OptionParser()
parser.add_option("-x", "--xcoord", dest="x", default = "0", help="x-coordiante of laser")
parser.add_option("-y", "--ycoord", dest="y", default = "0", help="y-coordiante of laser")
(options, args) = parser.parse_args()

x = int(options.x)
y = int(options.y)

# move laser to position
L.Move(x,y)
