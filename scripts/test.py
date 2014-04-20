from CVision import Calibration
import time

C = Calibration()

beamwidth = 15
C.LM.SetBeamWidth(beamwidth)
C.LM.Move(70,80)
C.CalibrateBrightness(control=True, color="green")
C.GetLaserPosition(beamwidth,control=True,threshold=251)

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