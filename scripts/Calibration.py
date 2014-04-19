from CVision import Calibration
import time
from optparse import OptionParser

#option parser
parser = OptionParser()
parser.add_option("-a", "--pa", dest="a", default = "0", help="general pupose parameter a")
parser.add_option("-b", "--pb", dest="b", default = "0", help="general pupose parameter b")
parser.add_option("-c", "--pc", dest="c", default = "0", help="general pupose parameter c")
parser.add_option("-d", "--pd", dest="d", default = "0", help="general pupose parameter d")
(options, args) = parser.parse_args()

a = int(options.a)
b = int(options.b)
c = int(options.c)
d = int(options.d)

C = Calibration()

#w = 1920
#h = 1080
#w = 2592
#h = 1944

#C.LM.Stop()
#print C.FindShelves(control=True)
#print C.FindBorders(control=True)
#print C.CalculateWarpMatrix(control=True)
#print C.FindChessboard(control=True)

Lx = c
Ly = d
C.LM.Move(Lx,Ly)
#print C.LM.MoveCM(Lx,Ly)

if b == 0:
    C.CalibrateBrightness(control=True,color="green",width=1280,height=720)
else:
    C.Cam.SetBrightness(b)
    C.Cam.SetExposureCompensation(a)
    
#print C.GetLaserPosition(control=True)

#print C.CreateLaserMatrix(control=True)
#print C.AssignLaserToShelves(control=True)

C.LM.Stop()
for i in xrange(0,30,1):
    wait=6
    dist_x, dist_y, row = C.DetectMissingBook()
    if dist_x!=None and dist_y!=None:
        print "cm-coordinates:", dist_x, dist_y, "shelf:", row
        Lx,Ly = C.LM.MoveCM(dist_x, dist_y, row)
        print "Laser channels:", Lx, Ly
        wait=3
    else:
        print "..."#

    time.sleep(wait)
    C.LM.Stop()


C.LM.Stop()
C.Cam.Close()