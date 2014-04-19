from CVision import Calibration
from optparse import OptionParser

#option parser
parser = OptionParser()
parser.add_option("-s", "--step", dest="s", default = "0", help="step for registering new books")
(options, args) = parser.parse_args()

step = int(options.s)
C = Calibration()
C.LM.Stop()

if step == 1:    
    dist_x, dist_y, row = C.DetectMissingBook(1)
elif step == 2:
    dist_x, dist_y, row = C.DetectMissingBook(2)
    if dist_x!=None and dist_y!=None:
        print dist_x, dist_y, row
        C.LM.MoveCM(dist_x, dist_y, row)
        C.P.StoreParameter("dist_x",str(dist_x),"integer")
        C.P.StoreParameter("dist_y",str(dist_y),"integer")
        C.P.StoreParameter("row",str(row),"integer")
    else:
        print "no book found"
else:  
    exit(0)
    