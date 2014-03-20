from DmxPro import DmxPro

class Laser_Stairville__150_RGY: # for each laser model define such a class

     def __init__(self, offset=0): # most DMX devices allow for configuring an offset within the 512 DMX channels
        self.dmx = DmxPro('/dev/ttyUSB0')
        
        self.offset = offset
        
        self.max_left = 94 # x-channel value for leftmost position
        self.max_right = 34 # x-channel value for rightmost position
        
        self.max_top = 34 # y-channel value for topmost position
        self.max_bottom = 96 # y-channel value for topbottom position
        
        self.dmx.setChannel(self.offset+2,152) # pattern; 152 = horizontal line
        self.dmx.setChannel(self.offset+3,120) # zoom; set to have a width of the laser beam of approx. 20 cm on the book-shelf
        self.dmx.setChannel(self.offset+4,0) # rotation y: 0=off
        self.dmx.setChannel(self.offset+5,0) # rotation x: 0=off
        self.dmx.setChannel(self.offset+6,0)  # rotation z: 0=off
        self.dmx.setChannel(self.offset+9,32)  # color: 16=red, 32=green, 48=yellow (both), 127=changing
        
     def Move(self, x, y):
        self.dmx.setChannel(self.offset+1,252) # DMX mode and laser on
        self.dmx.setChannel(self.offset+7,x)  # move to x position
        self.dmx.setChannel(self.offset+8,y)  # move to y position
        self.dmx.send()
        
     def Stop(self):
        self.dmx.setChannel(self.offset+1,0) # laser off
        self.dmx.send()