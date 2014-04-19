import sys
import io
import math
import cv2
import numpy as np
import picamera
import time

class Cam:

    def __init__(self):
        self.camera = picamera.PiCamera()
        self.img = np.empty([0,0]) # initialise with 0 size
        self.best_thresval = 254
        self.best_thres = 20  
        self.best_brightness = 50
        self.width = 0
        self.height = 0
        self.ksize = 2  # for blurring images
        self.camera.ISO = 100
        
    def Close(self):
        self.camera.close()
        
    def QueryImage(self, width=2592, height=1944):
        self.width = width
        self.height = height
        self.min_length = int(self.width*0.01) # min width of laser beam
        
        self.camera.resolution = (width, height)
        self.camera.brightness = self.best_brightness
        
        stream = io.BytesIO()
        self.camera.capture(stream, format='jpeg')
        # Construct a numpy array from the stream
        data = np.fromstring(stream.getvalue(), dtype=np.uint8)
        # "Decode" the image from the array, preserving colour
        self.img = cv2.imdecode(data, 1)  # flag 1: color image, flag 0: gray
        # crop border
        #wborder = int(self.width/10)
        hborder = int(self.height*0.2)
        self.img = self.img[0:(self.height-hborder), 0:self.width]
        # free temporary containers
        del stream
        del data
        
    def WriteImage(self, filename):    
        if self.img.size > 0:
            cv2.imwrite(filename,self.img)
        else:
            print "no image to save"
            sys.exit(1)        
        
    def CallibrateBrightness(self, width=640, height=480, color="none"): # make sure green laser is turned on!         
         # first round: step 9
         for b in xrange(91,0,-10):
            self.best_brightness = b
            self.QueryImage(width,height)
            if color == "green":
                simg = cv2.split(self.img)
                #bimg = cv2.blur(simg[1], (self.ksize,self.ksize))
                hist = np.bincount(simg[1].ravel(),minlength=256) # optimise on green channel
                print hist[255]
                if hist[255] < self.width*self.height*0.0004: # 0.0004
                    break            
            else:
                #bimg = cv2.blur(self.img, (self.ksize,self.ksize))
                hist = np.bincount(self.img.ravel(),minlength=256) # optimise on all channels
                print hist[255]
                if hist[255] < self.width*self.height*0.001: # 0.0008
                    break 
         # second round: step 1         
         for bb in xrange(b+9,0,-1):
            self.best_brightness = bb
            self.QueryImage(width,height)
            if green == True:
                simg = cv2.split(self.img)
                #bimg = cv2.blur(simg[1], (self.ksize,self.ksize))
                hist = np.bincount(simg[1].ravel(),minlength=256) # optimise on green channel
                print hist[255]
                if hist[255] < self.width*self.height*0.0004:
                    break            
            else:
                #bimg = cv2.blur(self.img, (self.ksize,self.ksize))
                hist = np.bincount(self.img.ravel(),minlength=256) # optimise on all channels
                print hist[255]
                if hist[255] < self.width*self.height*0.001:
                    break    
         #self.best_brightness = self.best_brightness +1 # one step back
         print "best_brightness: ", self.best_brightness
            
    def CallibrateParameters(self, width=1920, height=1080):
        self.QueryImage(width,height)    
        simg = cv2.split(self.img) # simg[1] is the green channel
        # blurring of simg[1]
        #bimg = cv2.blur(simg[1], (self.ksize,self.ksize))
        # search for the best values of thresholds
        # criteria is smalles number of lines detected (ideally: 1 line which is the laser)
        
        min_size = 100; # number of lines detected        
        
        for thresval in xrange(254, 250, -1):
            ret, dst = cv2.threshold(simg[1], thresval, 255, cv2.THRESH_BINARY)
            print thresval
            #test whether there are already too many lines at thr = 100
            lines = cv2.HoughLinesP(dst, 1, math.pi/180, 100, None, self.min_length, int(self.min_length/3))
            if(lines != None):
                if(len(lines[0]) > 20):
                    break
            # now find optimum for thr
            for thr in xrange(5,100,5):
                lines = cv2.HoughLinesP(dst, 1, math.pi/180, thr, None, self.min_length, int(self.min_length/3))
                if(lines != None):
                    if len(lines[0]) == 0: # no need to increase thr further
                        break
                    if len(lines[0]) < min_size and len(lines[0]) > 0:
                        min_size = len(lines[0])
                        self.best_thresval = thresval
                        self.best_thres = thr

        print "min_size: ", min_size
        print "best_thresval: ", self.best_thresval
        print "best_thres: ", self.best_thres
        
        del simg, dst, lines #,bimg
    
    def GetLaserPosition2(self, control=False):        
        simg = cv2.split(self.img) # simg[1] is the green channel

        # blurring of simg[1]
        #bimg = cv2.blur(simg[1], (5,5))
        
        # now using the optimal valued best_thresval and best_thres
        ret, dst = cv2.threshold(simg[1], self.best_thresval, 255, cv2.THRESH_BINARY)
        cv2.imwrite("../images/threshold.jpg",dst)
        
        lines = cv2.HoughLinesP(dst, 1, math.pi/180, self.best_thres, None, self.min_length, self.min_length/3)
        if lines != None:
            #averaging the x and y position of all horizontal lines detected
            x = 0
            y = 0        
            for line in lines[0]:
                #check if horizontal line
                if abs(line[1]-line[3]) < self.height*0.014: # max. difference in y-coord allowed
                    x = x+abs(line[0]+line[2])/2
                    y = y+abs(line[1]+line[3])/2
                    if control == True: # draw lines into image
                        pt1 = (line[0],line[1])
                        pt2 = (line[2],line[3])
                        cv2.line(self.img, pt1, pt2, (0,0,255), 3)    
                                    
            if control == True:
                print lines[0]
                cv2.imwrite("../images/test_laser.jpg",self.img)
                
            x = x/len(lines[0])
            y = y/len(lines[0])
            return (x, y)
        else:
            return (0, 0)

    def GetLaserPosition(self, control=False):        
        simg = cv2.split(self.img) # simg[1] is the green channel
        # blurring of simg[1]
        #bimg = cv2.blur(simg[1], (5,5))
        
        # now using the optimal values for best_thresval
        ret, dst = cv2.threshold(simg[1], self.best_thresval, 255, cv2.THRESH_BINARY)
        if control == True:
            cv2.imwrite("../images/threshold.jpg",dst)
        # detect contours
        contours, hierarchy = cv2.findContours( dst, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #contours1 = [cv2.approxPolyDP(cnt, 3, True) for cnt in contours]
        
        if contours != None:
            rect = []
            for cnt in contours: # find bounding rectangles
                br = cv2.boundingRect(cnt)
                if control == True:
                    print br
                if br[2] > self.min_length and br[2] > 2*br[3]: # horizontal flat rectangle: width > 2*height
                    rect.append(br)
            if len(rect) > 0:
                if control == True:
                    print "-------------" , len(rect)          
                x = 0
                y = 0            
                for b in rect:
                    x = x + (b[0]+b[2]/2)
                    y = y + (b[1]+b[3]/2)
                    if control == True:
                        print b
                        cv2.rectangle(self.img,(b[0],b[1]),(b[0]+b[2],b[1]+b[3]),(0,0,255),2)
                        cv2.imwrite("../images/test_laser.jpg",self.img)
                    
                x = x/len(rect)
                y = y/len(rect)
                return (x,y)
            else:
                return (None, None)
        else:
            return (None, None)
            