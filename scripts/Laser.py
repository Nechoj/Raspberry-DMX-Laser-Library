import numpy as np
from DmxPro import DmxPro
from Parameter import Parameter

class Laser_Stairville__150_RGY: # for each laser model define such a class
    def __init__(self, offset=0): # most DMX devices allow for configuring an offset within the 512 DMX channels
        
        self.offset = offset # DMX channel offset that can be configured at the device
        
        self.max_left = 94 # x-channel value for leftmost position
        self.max_right = 34 # x-channel value for rightmost position
        self.max_top = 34 # y-channel value for topmost position
        self.max_bottom = 96 # y-channel value for topbottom position
        
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
                    
        self.no_of_channels = 9 # number of DMX channels used by this device
        self.buffer=bytearray(self.no_of_channels) # array for holding the data to be sent; buffer[0] is channel 1
        
        # self.buffer[n] = channel n+1 !!
        self.buffer[1] = chr(152) # channel 2: pattern; 152 = horizontal line
        self.buffer[2] = chr(120) # channel 3: zoom; set to have a width of the laser beam of approx. 20 cm on the book-shelf
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
        
        
class LaserManagement: # this class provides functions to deal with the connected lasers     
    def __init__(self):        
        self.dmx = DmxPro('/dev/ttyUSB0', 25) # interface to DMX Pro driver
        self.Lasers = []
        L1 = Laser_Stairville__150_RGY(offset=0) # for each connected laser, instantiate such a class (use different offsets!) and append to Lasers[]
        self.Lasers.append(L1)
        self.no_of_lasers = len(self.Lasers) # number of connected lasers
        
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
        