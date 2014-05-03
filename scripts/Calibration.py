from CVision import Calibration
import time
from optparse import OptionParser
import subprocess

# important: laser_daemon must not running when using this script!
#subprocess.call("sudo service laser_daemon.sh stop", shell=True)

#option parser
parser = OptionParser()
parser.add_option("-s", "--step", dest="s", default = "0", help="calibration step")
parser.add_option("-b", "--brightness", dest="b", default = "0", help="brightness")
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
    print C.FindBorders(control=True)
if s==3:
    print C.CalculateWarpMatrix(control=True)
if s==4:
    print C.FindChessboard(control=True)
if s==5:
    bwidth = 7
    if b==0:
        C.LM.SetBeamWidth(bwidth)
        C.LM.Move(70,72)
        C.CalibrateBrightness(bwidth,control=True,color="green",width=1280,height=720)
        C.LM.Stop()
    else:
        C.Cam.SetBrightness(b)
        C.Cam.SetExposureCompensation(e)
    print C.CreateLaserMatrix(beamwidth=bwidth,control=True)


C.LM.Stop()
C.Cam.Close()