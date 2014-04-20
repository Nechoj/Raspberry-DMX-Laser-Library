from CVision import Calibration
import time
from optparse import OptionParser

# important: laser_daemon must nit running when using this script!
# sudo service laser_daemon.sh stop

#option parser
parser = OptionParser()
parser.add_option("-s", "--step", dest="s", default = "0", help="calibration step")
parser.add_option("-b", "--brightness", dest="b", default = "50", help="brightness")
parser.add_option("-e", "--exposure", dest="e", default = "0", help="exposure compensation")
parser.add_option("-c", "--canny", dest="c", default = "10", help="canny threshold")

(options, args) = parser.parse_args()

s = int(options.s)
b = int(options.b)
e = int(options.e)
c = int(options.c)

C = Calibration()

C.LM.Stop()
if s==1:
    print C.FindShelves(control=True)
if s==2:    
    print C.FindBorders(control=True, canny_thres = c)
if s==3:
    print C.CalculateWarpMatrix(control=True)
if s==4:
    print C.FindChessboard(control=True)
if s==5:
    if b==0:
        C.LM.Move(60,72)
        C.CalibrateBrightness(control=True,color="green",width=1280,height=720)
        C.LM.Stop()
    else:
        C.Cam.SetBrightness(b)
        C.Cam.SetExposureCompensation(e)
    print C.CreateLaserMatrix(control=True)
if s==6:    
    print C.AssignLaserToShelves(control=True)


C.LM.Stop()
C.Cam.Close()