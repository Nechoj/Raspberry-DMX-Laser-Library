from optparse import OptionParser
from CVision import *
import time

#option parser
parser = OptionParser()
parser.add_option("-l", "--laser", dest="l", default = "1", help="number of laser")
parser.add_option("-x", "--xcoord", dest="x", default = "0", help="x-coordiante of laser")
parser.add_option("-y", "--ycoord", dest="y", default = "0", help="y-coordiante of laser")
parser.add_option("-w", "--width", dest="w", default = "7", help="width of laser")
parser.add_option("-z", "--zoom", dest="z", default = "120", help="zoom")
(options, args) = parser.parse_args()

l = int(options.l)
x = int(options.x)
y = int(options.y)
w = int(options.w)
z = int(options.z)

C = Calibration()

beamwidth = w
C.LM.SetBeamWidth(beamwidth)

Lx, Ly =  C.Convert_PositionToL(x, y)
print Lx, Ly
if Lx != None:
    C.LM.Move(Lx,Ly)

#C.CalibrateBrightness(beamwidth,control=True, color="green")
C.Cam.SetBrightness(49)
C.Cam.SetExposureCompensation(15)
print C.GetLaserPosition(beamwidth,control=True,threshold=251)

#C.LM.Stop()
#for i in xrange(0,30,1):
#    wait=6
#    dist_x, dist_y, row = C.DetectMissingBook()
#    if dist_x!=None and dist_y!=None:
#        print "cm-coordinates:", dist_x, dist_y, "shelf:", row
#        Lx,Ly = C.LM.MoveCM(dist_x, dist_y, row)
#        print "Laser channels:", Lx, Ly
#        wait=3
#    else:
#        print "..."

#    time.sleep(wait)
#    C.LM.Stop()


#C.LM.Stop()