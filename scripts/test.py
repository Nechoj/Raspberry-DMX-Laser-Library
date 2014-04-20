from CVision import Calibration
import time

C = Calibration()

#C.LM.Stop()
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