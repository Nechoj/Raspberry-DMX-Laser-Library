from optparse import OptionParser
from Laser import LaserManagement

LM = LaserManagement()

#option parser
parser = OptionParser()
parser.add_option("-d", "--dist_x", dest="d", default = "0", help="distance of book to left border of shelves (in cm)")
parser.add_option("-b", "--dist_y", dest="b", default = "0", help="distance of book to bottom shelf (in cm). This parameter is ignored, if parameter -r is >0")
parser.add_option("-r", "--row", dest="r", default = "-1", help="number of shelf; top is 1")
(options, args) = parser.parse_args()

d = int(options.d)
b = int(options.b)
r = int(options.r)

# move laser to position
print LM.MoveCM(d,b,r)