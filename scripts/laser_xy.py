from optparse import OptionParser
from Laser import LaserManagement

LM = LaserManagement()

#option parser
parser = OptionParser()
parser.add_option("-l", "--laser", dest="l", default = "1", help="number of laser")
parser.add_option("-x", "--xcoord", dest="x", default = "0", help="x-coordiante of laser")
parser.add_option("-y", "--ycoord", dest="y", default = "0", help="y-coordiante of laser")
parser.add_option("-w", "--width", dest="w", default = "0", help="width of laser")
parser.add_option("-z", "--zoom", dest="z", default = "120", help="zoom")
(options, args) = parser.parse_args()

l = int(options.l)
x = int(options.x)
y = int(options.y)
w = int(options.w)
z = int(options.z)

if w!= 0: # w overrides z setting
    LM.SetBeamWidth(w)
else:
    LM.Lasers[l-1].SetZoom(z)

LM.Move(x,y,l)
