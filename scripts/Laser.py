import numpy as np
from DmxPro import DmxPro
from Parameter import Parameter

class Laser_Stairville__150_RGY: # for each laser model define such a class
    def __init__(self, DMX_address=1): # most DMX devices allow for configuring the start address within the 512 DMX channels
       
        # parameter offset = DMX channel offset that can be configured at the device
        self.offset = DMX_address-1 # self.offset is start index in buffer (0 = 1st byte)
        self.no_of_channels = 9 # number of DMX channels used by this device
        
        self.max_left = 94 # x-channel value for leftmost position
        self.max_right = 34 # x-channel value for rightmost position
        self.max_top = 34 # y-channel value for topmost position
        self.max_bottom = 96 # y-channel value for topbottom position
        
        # distance of laser to shelves in cm
        self.distance = 525.0
        
        
        P = Parameter() # interface to database table parameters
        
        # parameters y_row_i: Laser y-channels corresponding to shelves;
        # these parameters are automatically set in function CVision::Cam:AssignLaserToShelves(), or set in the database laser - table parameters - manually
        self.y_row = [] # y_row[i]: Ly channel numer of shelf i+1
        for i in range(10): # max 10 shelves should be enough in any case ...
            p = P.GetParameter(''.join(["y_row_", str(i+1)]))
            if p != None:
                self.y_row.append(p)
        self.y_row = np.array(self.y_row)
        
        # matrix to convert real world cm coordinates into laser channel values
        # this matrix is calculated in function CVision::Cam:CreateLaserMatrix()
        self.matCMtoL = np.zeros((3,3), np.float32)
        for i in (0,1,2):
            for j in (0,1,2):      
                p = P.GetParameter(''.join(["matCMtoL_", str(i), str(j)]))
                if p != None:
                    self.matCMtoL[i,j] = p
        
        # initialising the buffer for the DMX channel values
        self.buffer=bytearray(self.no_of_channels) # array for holding the data to be sent; buffer[0] is channel 1
        # self.buffer[n] = channel n+1 !!
        self.buffer[1] = chr(152) # channel 2: pattern; 152 = horizontal line
        self.buffer[2] = chr(120) # channel 3: zoom; set default value to approx 15 cm beam width
        self.buffer[3] = chr(0)   # channel 4: rotation y: 0=off
        self.buffer[4] = chr(0)   # channel 5: rotation x: 0=off
        self.buffer[5] = chr(0)   # channel 6: rotation z: 0=off
        self.buffer[8] = chr(32)  # channel 9: color: 16=red, 32=green, 48=yellow (both), 127=changing
        
    def SetMoveXY(self, x, y):
        self.buffer[0] = chr(252) # channel 1: 252 = DMX mode and laser on
        self.buffer[6] = chr(x)   # channel 7: move to x position
        self.buffer[7] = chr(y)   # channel 8: move to y position
        
    def SetStop(self):
        self.buffer[0] = chr(0)   # channel 1: 0 = laser off
        
    def SetZoom(self,zoom):
        self.buffer[2] = chr(zoom) # channel 3: zoom;
        
    def SetBeamWidth(self, width):
        # width is the required beam width in cm
        # Assumes that parameter self.distance has been set correctly
        alpha = 2*np.arctan(float(width)/2.0/self.distance)
        # the following mathematical function for the zoom needs to be derived in an experiment with this laser
        zoom = int(16262*alpha**3 - 230.2*alpha**2 - 464.96*alpha + 129.02) 
        if zoom > 122:
            zoom = 122
        if zoom < 0:
            zoom = 0
        self.SetZoom(zoom)


class LaserManagement: # this class provides functions to deal with the connected lasers     
    def __init__(self): 
        try:
            self.dmx = DmxPro('/dev/ttyUSB0', 25) # interface to DMX Pro driver
        except:
            print "Error in LaserManagement::__init__: "
            sys.exit(1)
        self.Lasers = []
        L1 = Laser_Stairville__150_RGY(DMX_address=1) # for each connected laser, instantiate such a class (use different DMX addresses!) and append to Lasers[]
        self.Lasers.append(L1)
        self.no_of_lasers = len(self.Lasers) # number of connected lasers
        
    
    def SetBeamWidth(self, width, laser=1):
        """ sets the beamwidth in cm for a specified laser"""
        L = self.Lasers[laser-1]
        L.SetBeamWidth(width)
    
    def Move(self, x, y, laser=1):
        """moves a laser to laser channel coordinates x,y"""
        # parameter laser specifies, which laser to use
        L = self.Lasers[laser-1]
        L.SetMoveXY(x,y)
        self.dmx.setChannels(L.offset, L.buffer)
        self.dmx.send()
            
    def MoveCM(self, dist_x, dist_y, row = -1, laser=1):
        """moves laser to pyisical point (dist_x, dist_y) where dist_x is the distance in cm of the point to the left border of the shelves,
        dist_y is the distance in cm to the bottom shelf. If parameter row is > 0, this is the number of the shelf and dist_y is ignored."""
        
        L = self.Lasers[laser-1]
        Lx, Ly, Lz = np.dot(L.matCMtoL, [dist_x, dist_y, 1.0])
        Lx = int(round(Lx/Lz))
        Ly = int(round(Ly/Lz))
        
        Lx_max = max(L.max_left, L.max_right)
        Lx_min = min(L.max_left, L.max_right)
        Ly_max = max(L.max_top, L.max_bottom)
        Ly_min = min(L.max_top, L.max_bottom)
        
        if Lx > Lx_max or Lx < Lx_min:
            return None, None # Lx out of allowed range
        
        if row == -1:
            if Ly > Ly_max or Ly < Ly_min:
                return None, None # Ly out of allowed range
        elif row > 0 and row <= len(L.y_row):
            Ly = L.y_row[row-1]
        else:
            return None, None # row out of allowed range
        
        self.Move(Lx,Ly,laser)
        return Lx, Ly
            
    def Stop(self):
        """turns of all lasers"""        
        
        for L in self.Lasers:
            L.SetStop()
            self.dmx.setChannels(L.offset, L.buffer)
        
        self.dmx.send()               
            
    def GetMaxChannels(self, laser=1):
        """returns max_left, max_right, max_top, max_bottom"""
        
        L = self.Lasers[laser-1]
        return L.max_left, L.max_right, L.max_top, L.max_bottom
        