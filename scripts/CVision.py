import io
import cv2
import time
import numpy as np
import picamera
from scipy import stats
from random import randrange
from Parameter import Parameter
from Laser import LaserManagement

class Camera:
    def __init__(self):
        """initialises picamera"""
        
        self.camera = picamera.PiCamera()
        self.camera.led = False
        self.img = np.empty([0,0]) # initialise with 0 size
        # default values for PiCamera
        self.best_brightness = 50
        self.best_exposure_compensation = 0
        
        # angular camera resolution in rad per pixel (near center of image)
        # this parameter has been calculated from the measured reference dx value (px per cm) and the distance to the camera
        # a new distance is then calculated with 1/(dx*tan(self.alpha))
        self.dalpha = 5.203831969919e-4 

    def SetBrightness(self, p_brightness):
        # function to override automatic calibration values
        self.best_brightness = p_brightness  

    def SetExposureCompensation(self, p_value):
        # function to override automatic calibration values
        self.best_exposure_compensation = p_value
        
    def QueryImage(self, width=1920, height=1080): 
        """takes a picture with the camera and stores it in self.img. The value self.best_brightness is used as camera.brightness"""

        self.camera.resolution = (width, height)
        self.camera.brightness = self.best_brightness
        self.camera.exposure_compensation = self.best_exposure_compensation
        
        stream = io.BytesIO()
        
        self.camera.led = True        
        self.camera.capture(stream, format='jpeg')
        self.camera.led = False
        
        # Construct a numpy array from the stream
        data = np.fromstring(stream.getvalue(), dtype=np.uint8)
        # "Decode" the image from the array, preserving colour
        self.img = cv2.imdecode(data, 1)  # flag 1: color image, flag 0: gray
        
        # free temporary containers
        del stream
        del data
        
    def WriteImage(self, filename):
        """writes the self.img to a file"""
        cv2.imwrite(filename,self.img)
        
    def Close(self):
        self.camera.close()    
        
    def __del__(self):
        self.camera.close()        
        
   
class Calibration:

    def __init__(self, laser=1):
        """initialises components and reads system paramters from database"""
        
        self.Cam = Camera()
        self.LM = LaserManagement()
        self.P = Parameter() # interface to database table parameters
        
        # the following parameters are stored in the database and set in functions FindShelves and FindBorders
        # all parameters are normalised to a coordinate system height = width = 1.0
        
        # ab parameters of straight lines representing the shelves
        # usage: a = self.shelves_ab[i,1]*height, b = self.shelves_ab[i,2]*height/width where height and width are from actual image
        # y = a + x*b  
        self.shelves_ab = [] # [i,a,b] i = index of shelf, a = intercept, b = slope
        self.y_row = [] # y_row[i]: Ly channel numer of shelf i+1
        
        self.no_of_shelves = self.P.GetParameter("no_of_shelves")
        
        if self.no_of_shelves != None:
            for i in xrange(0, self.no_of_shelves, 1):
                a = self.P.GetParameter(''.join(["shelves_a_", str(i)]))
                b = self.P.GetParameter(''.join(["shelves_b_", str(i)]))
                if a != None and b!= None:
                    self.shelves_ab.append([i,a,b])
                
                p = self.P.GetParameter(''.join(["y_row_", str(i+1)]))
                if p != None:
                    self.y_row.append(p)
        
        self.shelves_ab = np.array(self.shelves_ab)
        self.y_row = np.array(self.y_row)
        
        # ab parameters of straight lines representing the borders of the shelves
        # usage: a = self.borders_ab[i,1]*width, b = self.borders_ab[i,2]*width/height where height and width are from actual image
        # i=0 : left border, i=1: right border
        # x = a + b*y  
        self.borders_ab = []
        pa = self.P.GetParameter("borders_a_left")
        pb = self.P.GetParameter("borders_b_left")
        if pa != None and pb != None:
            self.borders_ab.append([0,pa,pb])
        else:
            self.borders_ab.append([0,0.0,0.0])
        pa = self.P.GetParameter("borders_a_right")
        pb = self.P.GetParameter("borders_b_right")
        if pa != None and pb != None:
            self.borders_ab.append([1,pa,pb])
        else:
            self.borders_ab.append([1,1.0,0.0])  
        self.borders_ab = np.array(self.borders_ab)  
            
        # average height of books in pixels
        # usage: height of books = self.book_height*height
        p = self.P.GetParameter("book_height")  
        if p != None:
            self.book_height = p
        else:
            self.book_height = 0.065  
        
        # values for image cropping; 
        # usage: img = self.CropImg(img) -> see function CropImg() below
        p = self.P.GetParameter("cy_top")
        if p != None:
            self.cy_top = p
        else:
            self.cy_top = 0.0

        p = self.P.GetParameter("cy_height")
        if p != None:
            self.cy_height = p
        else:
            self.cy_height = 1.0
            
        p = self.P.GetParameter("cx_left")
        if p != None:
            self.cx_left = p
        else:
            self.cx_left = 0.0
            
        p = self.P.GetParameter("cx_width")
        if p != None:
            self.cx_width = p
        else:
            self.cx_width = 1.0
        
        # matrix for WarpPerspective
        self.matWarp = np.zeros((3,3), np.float32)
        for i in (0,1,2):
            for j in (0,1,2):
                name = ''.join(["mat_", str(i), str(j)])                
                p = self.P.GetParameter(name)
                if p == None:
                    if i==j:
                        self.matWarp[i,j] = 1.0
                else:
                    self.matWarp[i,j] = p   
                    
        # dx, dy for physical coordinates: 'pixels per cm' in warped image
        self.dx = self.P.GetParameter("dx")
        self.dy = self.P.GetParameter("dy")
        # distance between camera and shelves in cm
        p = self.P.GetParameter("distance")
        if p == None:
            self.distance = 400
        else:
            self.distance = p
        
        # matrix for mapping warped px,py to real world cm
        self.matCM = np.zeros((3,3), np.float32)
        for i in (0,1,2):
            for j in (0,1,2):      
                p = self.P.GetParameter(''.join(["matCM_", str(i), str(j)]))
                if p == None:
                    if i==j:
                        self.matCM[i,j] = 1.0
                else:
                    self.matCM[i,j] = p        
        
        # matrix for mapping real world cm coordinates to laser channels
        self.matCMtoL = np.zeros((3,3), np.float32)
        for i in (0,1,2):
            for j in (0,1,2):      
                p = self.P.GetParameter(''.join(["matCMtoL_", str(i), str(j)]))
                if p == None:
                    if i==j:
                        self.matCMtoL[i,j] = 1.0
                else:
                    self.matCMtoL[i,j] = p   
                    
    def __del__(self):
        self.Cam.Close()  
        
    def CalibrateBrightness(self, control=False, color="none", width=640, height=480):         
         """this function sets the brightness so that the laser beam is the brightest signal in the image.
         When calling this function, the laser beam must be on and pointing to some books"""
         
         if control == True:
            print "calibrating brightness and exposure compensation ..."
         max_255 = width*height*0.0001 # max number of bright pixels
         
         # first round: step 10
         for b in xrange(71,0,-10):
            self.Cam.SetBrightness(b)
            self.Cam.QueryImage(width,height)
            if color == "green": # make sure green laser is turned on! 
                simg = cv2.split(self.Cam.img)
                gimg = simg[1] # simg[1] is the green channel
                gimg = self.CropImg(gimg) # crop image
                hist = np.bincount(gimg.ravel(),minlength=256) # optimise on green channel
                if hist[255] < max_255:
                    break            
            else:
                gimg = self.CropImg(self.Cam.img) # crop image            
                hist = np.bincount(gimg.ravel(),minlength=256) # optimise on all channels
                if hist[255] < 2*max_255:
                    break 
                    
         # second round: step 1         
         for bb in xrange(b+9,b-1,-1):
            self.Cam.SetBrightness(bb)
            self.Cam.QueryImage(width,height)
            if color == "green": # make sure green laser is turned on! 
                simg = cv2.split(self.Cam.img)
                gimg = simg[1] # simg[1] is the green channel
                gimg = self.CropImg(gimg) # crop image
                hist = np.bincount(gimg.ravel(),minlength=256) # optimise on green channel
                if hist[255] < max_255:
                    break            
            else:
                gimg = self.CropImg(self.Cam.img) # crop image            
                hist = np.bincount(gimg.ravel(),minlength=256) # optimise on all channels
                if hist[255] < 2*max_255_pixels:
                    break    
         
         self.Cam.best_brightness = self.Cam.best_brightness + 1 # one step back
         if control == True:
            print "best_brightness: ", self.Cam.best_brightness
         
         # third round: find optimal camera.exposure_compensation
         # optimise on number of laser spot contours found
         for c in xrange(10,-25,-1):
            self.Cam.SetExposureCompensation(c)
            self.Cam.QueryImage(width,height)
            simg = cv2.split(self.Cam.img)
            gimg = simg[1] # simg[1] is the green channel
            gimg = self.WarpImg(gimg) # warp
            gimg = self.CropImg(gimg) # crop image
            gimg = cv2.blur(gimg, (3,3) ) # blur
            ret, dst = cv2.threshold(gimg, 251, 255, cv2.THRESH_BINARY) # only keep the brightest pixels        
            # detect contours
            contours, hierarchy = cv2.findContours( dst, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours != None and len(contours)<5:
                break
            
         if control == True:
            print "best_exposure_compensation: ", self.Cam.best_exposure_compensation 
        
    
    def CropImg(self, img):
        """ converts self.crop values to pixel coordinates and applies to img. Returns the cropped img."""
        # if gray image: img.shape = (height, width)
        # if color image: img.shape = (height, width, 3)
        if len(img.shape) == 2: # gray image
            return img[int(self.cy_top*img.shape[0]):int(self.cy_height*img.shape[0]), int(self.cx_left*img.shape[1]):int(self.cx_width*img.shape[1])]
        else: #color
            return img[int(self.cy_top*img.shape[0]):int(self.cy_height*img.shape[0]), int(self.cx_left*img.shape[1]):int(self.cx_width*img.shape[1]),:]        
        
    
    def GetCropValues(self, width=1920, height=1080):
        """ returns crop values in pixels, relative to given width and height"""
        return(int(self.cy_top*height), int(self.cy_height*height), int(self.cx_left*width), int(self.cx_width*width))

    
    def WarpImg(self,img):
        """perspective transformation using the matrix self.matWarp. Returns the warped img"""
        return cv2.warpPerspective(img, self.matWarp, (img.shape[1], img.shape[0]))
    
    
    def FindShelves(self, control=False, width=1920, height=1080):
        """finds contours of books, computes statistically the straight lines representing the shelves, 
        the average height of the books and the crop values for the image. Returns number of shelves found"""
        
        if control == True:
            print "searching for shelves ..."
        
        # require some min width and height of the rectangle around books -> filter out 'noise'
        min_width = width*0.002 
        min_height = width*0.02
        
        # take image, convert to gray and blur
        self.Cam.SetBrightness(50) # restore default value       
        self.Cam.QueryImage(width,height)         
        gray = cv2.cvtColor(self.Cam.img,cv2.COLOR_BGR2GRAY) # convert to gray image
        gray = cv2.blur(gray, (3,3) ); # blur        
        
        # find optimal threshold maximising the number of detected books
        number_of_books_found = 0
        best_thr = 0
        for thr in xrange(160,80,-5): # mostly, good values are in the range 100 ... 120
            ret, dst = cv2.threshold(gray, thr, 255, cv2.THRESH_BINARY) # apply threshold
            contours, hierarchy = cv2.findContours( dst, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # find contours
            if contours != None:
                # find bounding rectangles; type rectangle: [TL x-coord, TL y-coord, width, height]
                rect = []
                for cnt in contours: 
                    br = cv2.boundingRect(cnt)
                    if(br[2]>min_width and br[3]>min_height and br[3]>0.5*br[2] ): # filtering for potential books         
                        rect.append(br)
                if len(rect) >  number_of_books_found: # find maximum number of potential books
                     number_of_books_found = len(rect)
                     best_thr = thr
       
        if number_of_books_found == 0:
            if control == True:
                print "no potential books found"
            return 0
                        
        if control == True:
            print "best threshold: ", best_thr
        
        #now use best_thr to detect the potential books
        ret, dst = cv2.threshold(gray, best_thr, 255, cv2.THRESH_BINARY) # apply threshold
        contours, hierarchy = cv2.findContours( dst, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # find contours      
        rect = []
        for cnt in contours:
            br = cv2.boundingRect(cnt)
            if(br[2]>min_width and br[3]>min_height and br[3]>0.5*br[2] ): # filtering for potential books        
                rect.append(br)
                if control == True: # draw rectangle in black 
                    cv2.rectangle(self.Cam.img,(br[0],br[1]),(br[0]+br[2],br[1]+br[3]),(0,0,0),2)
          
        rect = np.array(rect) # convert to numpy array  
        
        # remove too high rectangles
        bh = np.average(rect[:,3]) # preliminary average book_height in pixels
        rect = rect[rect[:,3]< int(1.6*bh),:] # allowed max height: 1.6 * average
        
        # find clusters of books using a simple clustering algorithm (kind of a watershed algorithm on the histogram of bottom y-coordinates)
        # calculate histogram of bottom y-values of all potential books
        y = rect[:,1] + rect[:,3] # top y-coord + height = bottom y-coord
        
        # determine approximate average y-positions of shelves (step 1)
        y_bin_width = int(height/40)
        y_bins = np.arange(0,height,y_bin_width) # bins for histogram                
        y_hist = np.bincount(np.digitize(y,y_bins)) # histogram
        
        previous = False # used to find local maximums in y_hist -> shelves
        shelves_y = [] # array to hold approximate y-coordinates of shelves
        for i in xrange(0, len(y_hist), 1):
            if y_hist[i] >= 5: # at least 5 (potential) books make a shelf
                if  previous == False: # new local maximum = shelf
                    shelves_y.append(i*y_bin_width)
                elif y_hist[i] > y_hist[i-1]: # same shelf but higher value in histogram: replace previous value if value is higher
                    shelves_y[len(shelves_y)-1] = i*y_bin_width
                previous = True
            else: # we are between shelves
                previous = False
        
        self.no_of_shelves = len(shelves_y)
        if self.no_of_shelves == 0: # no potential shelves found
            return 0
            
        # fine-tune y-coord of shelves calculating an average position of the books on the shelves (step 2) 
        # calculate a new and finer histogram
        y_bin_width = int(height/100)
        y_bins = np.arange(0,height,y_bin_width) # bins for histogram                
        y_hist = np.bincount(np.digitize(y,y_bins)) # histogram   
        
        for n in xrange(0, self.no_of_shelves, 1):
            idx = int(shelves_y[n]/y_bin_width) # estimate index of local mixima in new histogram
            # calculate the average y-position of the books within a certain range around the shelf values
            no_books = 0
            new_y = 0
            lower = max(0, idx-5)
            upper = min(len(y_hist), idx+5)
            for i in xrange(lower, upper, 1):
                 new_y = new_y + y_hist[i]*i*y_bin_width
                 no_books = no_books + y_hist[i]
            shelves_y[n] = int(new_y/no_books) # store new value
        if control == True:
            print "approximate y-coords of shelves: ", shelves_y
                
        # now identify books by their y-coordinate (books are rectangles on the shelves)
        books = []  
        tol = int(height/60) # tolerance of y-coordinates around shelves
        for r in rect: # check all bottom y-coordinates of all rectangles, whether they are a book on a shelf
            for i in xrange(0, self.no_of_shelves, 1):
                if r[1]+r[3] > shelves_y[i] - tol and r[1]+r[3] < shelves_y[i] + tol: # r[1]+r[3] is y-coord of bottom of book
                    books.append([r[0],r[1],r[1],r[3],i]) # r is rectangle representing the book, i is index of shelf
        
        # linear regression for determining slope of shelves (step 3)
        books = np.array(books) # convert to numpy array
        sh_ab = [] # array to store the regression parameters temporarily
        for i in xrange(0, self.no_of_shelves, 1):
            books_i = books[books[:,4]==i,:] # filter out books on shelf with index i
            (b,a,r,tt,stderr)=stats.linregress(books_i[:,0],books_i[:,1]+books_i[:,3]) # numpy arrays are pretty cool :-)
            sh_ab.append([i,a,b,0]) # i: index of shelf, a: intercept, b: slope of straight line representing the shelf, last value: Laser channel number
                
        # identify books again by their y-coordinate in relation to the now skewed shelves
        del books # free memory
        books = []  
        tol = int(height/80) # tolerance of y-coordinates of shelves
        for i in xrange(0, len(sh_ab), 1):
            for r in rect: # check all y-coordinates of all rectangles, whether they are a book on the skewed shelf            
                y_shelf = int(sh_ab[i][1] + r[0]*sh_ab[i][2])
                if r[1]+r[3] > y_shelf - tol and r[1]+r[3] < y_shelf + tol: # r[1]+r[3] is y-coord of bottom
                    books.append([r[0],r[1],r[2],r[3],i]) # r is rectangle, i is index of shelf
                    if control == True: # draw white rectangles for books
                        cv2.rectangle(self.Cam.img,(r[0],r[1]),(r[0]+r[2],r[1]+r[3]),(255,255,255),2)         
        
        # new linear regression for determining slope of shelves (step 4)
        self.shelves_ab = [] # overwrite old values, if any
        books = np.array(books)
        for i in xrange(0, len(shelves_y), 1):
            books_i = books[books[:,4]==i,:]
            (b,a,r,tt,stderr)=stats.linregress(books_i[:,0],books_i[:,1]+books_i[:,3])
            # normalise a,b values to 0.0 ... 1.0 coordinate system
            # in new coord system then use y = a*height_2 + x*b*height_2/width_2
            a = a/height
            b = b*width/height
            self.shelves_ab.append([i,a,b])
            if control == True:
                #cv2.line(self.Cam.img,(0,int(a*height)), (width,int(a*height+width*b*height/width)),(0,0,255),2)
                cv2.line(self.Cam.img,(0,int(a*height)), (width,int(a*height+b*height)),(0,0,255),2)
        
        self.shelves_ab = np.array(self.shelves_ab)
        self.no_of_shelves = len(self.shelves_ab) # just in case we lost some shelves ...
        
        # store new values in database
        self.P.StoreParameter("no_of_shelves", str(self.no_of_shelves), "integer")
        
        for i in xrange(0,self.no_of_shelves,1):
            self.P.StoreParameter(''.join(["shelves_a_", str(i)]), str(self.shelves_ab[i,1]), "double")
            self.P.StoreParameter(''.join(["shelves_b_", str(i)]), str(self.shelves_ab[i,2]), "double")
                
        # determine average height of books store in database
        books = np.array(books)
        self.book_height = np.average(books[:,3])/float(height) # in coordinate system height = 0.0 ... 1.0
        if control == True:
            print "average height of books in pixels: ", int(self.book_height*float(height))
        self.P.StoreParameter("book_height", str(self.book_height), "double")
            
        # store preliminary crop values in 0.0 ... 1.0 coord system
        # exact crop values will be finally determined in function CalculateWarpMatrix
        self.cx_left = max(0.0, np.amin(books[:,0])/float(width) - 0.5*self.book_height) # take 50% book_height as reserve
        books_right = books[:,0]+books[:,2]
        self.cx_width = min(1.0, np.amax(books_right)/float(width) + 0.5*self.book_height)
        self.cy_top = max(0.0, min(self.shelves_ab[0,1]+self.shelves_ab[0,2]*self.cx_left, self.shelves_ab[0,1]+self.shelves_ab[0,2]*self.cx_width) - 1.3*self.book_height)
        nsh = len(self.shelves_ab)-1 # index for bottom shelf
        self.cy_height = min(1.0, max(self.shelves_ab[nsh,1]+self.shelves_ab[nsh,2]*self.cx_left, self.shelves_ab[nsh,1]+self.shelves_ab[nsh,2]*self.cx_width))

        if control == True:
            print "crop values y: ", self.cy_top, self.cy_height
            print "crop values x: ", self.cx_left, self.cx_width

        self.P.StoreParameter("cy_top", str(self.cy_top), "double")
        self.P.StoreParameter("cy_height", str(self.cy_height), "double")
        self.P.StoreParameter("cx_left", str(self.cx_left), "double")
        self.P.StoreParameter("cx_width", str(self.cx_width), "double")
            
        if control == True:
            cv2.imwrite("/home/pi/www/images/FindShelves.jpg",self.Cam.img)
        
        return self.no_of_shelves
        
    
    def FindBorders(self, control=False, width=1920, height=1080):
        """searches for vertical borders of shelves. Returns True if succesful, False otherwiese"""
                        
        # require some min height and max skewness of vertical lines
        min_length = 3.0*self.book_height*height
        maxLineGap = 0.1*self.book_height*height
        max_skew = 0.2*min_length
        # determine the best canny threshold: number of detected long vertical lines > lines_requested
        lines_requested = 3        
        
        if control == True:
            print "searching for at least ", lines_requested, "left border lines ..."
        
        canny_thres = 53 # start value
        round = 1 # first round will be with step = -5, then use step = -1
        step = -10
        for i in range(canny_thres): # max steps needed
            if control == True:
                print "testing canny_thres", canny_thres           
            borders_left = []
            self.Cam.QueryImage(width,height)         
            gray = cv2.cvtColor(self.Cam.img,cv2.COLOR_BGR2GRAY) # convert to gray image
            Crop = self.GetCropValues(width, height)
            gimg = gray[Crop[0]:Crop[1],int(Crop[2]-0.5*self.book_height*width):int(Crop[2]+self.book_height*width)] # crop image                                       
            canny_output = cv2.Canny(gimg,canny_thres,3*canny_thres,apertureSize = 3)
            lines = cv2.HoughLinesP(canny_output,1,np.pi/180,90,None,min_length,maxLineGap) # hough lines detection        
            
            if lines != None:
                for l in lines[0]: 
                    if( abs(l[2]-l[0]) < max_skew ): # filtering for potential vertical borders        
                        borders_left.append(l)
                if len(borders_left) >= lines_requested:
                    if round == 1:
                        canny_thres = canny_thres - step # go back and use finer steps
                        step = -1 # reduce step size
                        round = 2
                    else:
                        break # best canny_thres found
            
            if canny_thres > 1:
                canny_thres += step
            else:
                return False # something went wrong ...
        

        if len(borders_left) == 0:
            if control == True:
                print "no left border lines found"
            return False
            
        if control == True:
            for b in borders_left:
                cv2.line(gimg,(b[0],b[1]),(b[2],b[3]),255,2)
            cv2.imwrite("/home/pi/www/images/FindBorders_left.jpg",gimg)  
        
        if control == True:
            print "searching for at least ", lines_requested, "right border lines ..."

        canny_thres = 53 # start value
        round = 1 # first round will be with step = -5, then use step = -1
        step = -10
        for i in range(canny_thres): # max steps needed 
            if control == True:
                print "testing canny_thres", canny_thres         
            borders_right = []
            self.Cam.QueryImage(width,height)         
            gray = cv2.cvtColor(self.Cam.img,cv2.COLOR_BGR2GRAY) # convert to gray image
            Crop = self.GetCropValues(width, height)
            gimg = gray[Crop[0]:Crop[1],int(Crop[3]-self.book_height*width):int(Crop[3]+0.5*self.book_height*width)] # crop image                            
            canny_output = cv2.Canny(gimg,canny_thres,3*canny_thres,apertureSize = 3)
            lines = cv2.HoughLinesP(canny_output,1,np.pi/180,90,None,min_length,maxLineGap) # hough lines detection        
            
            if lines != None:
                for l in lines[0]: 
                    if( abs(l[2]-l[0]) < max_skew ): # filtering for potential vertical borders        
                        borders_right.append(l)
                if len(borders_right) >= lines_requested:
                    if round == 1:
                        canny_thres = canny_thres - step # go back and use finer steps
                        step = -1 # reduce step size
                        round = 2
                    else:
                        break # best canny_thres found
            
            if canny_thres > 1:
                canny_thres += step
            else:
                return False # something went wrong ...
        

        if len(borders_right) == 0:            
            if control == True:
                print "no right border lines found"
            return False
            
        if control == True:
            for b in borders_right:
                cv2.line(gimg,(b[0],b[1]),(b[2],b[3]),255,2)
            cv2.imwrite("/home/pi/www/images/FindBorders_right.jpg",gimg)  
        
        # calculate straight lines representing the borders of the shelves 
        intercept = [] # array to store intercepts of  border lines
        slope = [] # array to store slopes of  border lines
        for b in borders_left:
            # un-cropping coordinates
            b[0] = b[0] + Crop[2]-0.5*self.book_height*width # x1
            b[1] = b[1] + Crop[0] # y1
            b[2] = b[2] + Crop[2]-0.5*self.book_height*width # x2
            b[3] = b[3] + Crop[0] # y2
            s = float((b[0]-b[2]))/(b[1]-b[3]) # slope
            slope.append(s)
            intercept.append(float(b[0] - s*b[1]))
        # find maximum of intercept -> real edge of left border of shelve
        intercept = np.array(intercept)
        a = np.amax(intercept)
        b = slope[np.argmax(intercept)]
        # calculate coordinates relative to 0.0 ... 1.0 and store in data base
        self.borders_ab[0,1] = a/float(width)
        self.borders_ab[0,2] = b/float(width)*float(height)
        
        intercept = [] # array to store intercepts of  border lines
        slope = [] # array to store slopes of  border lines
        for b in borders_right:
            # un-cropping coordinates
            b[0] = b[0] + Crop[3]-self.book_height*width # x1
            b[1] = b[1] + Crop[0] # y1
            b[2] = b[2] + Crop[3]-self.book_height*width # x2
            b[3] = b[3] + Crop[0] # y2
            s = float((b[0]-b[2]))/(b[1]-b[3]) # slope
            slope.append(s)
            intercept.append(float(b[0] - s*b[1]))
        # find minimum of intercept -> real edge of right border of shelve
        intercept = np.array(intercept)
        a = np.amin(intercept)
        b = slope[np.argmin(intercept)]
        # calculate coordinates relative to 0.0 ... 1.0 and store in data base
        self.borders_ab[1,1] = a/float(width)
        self.borders_ab[1,2] = b/float(width)*float(height) 
        if control == True:
            print "borders_ab left:", self.borders_ab[0,:]
            print "borders_ab right:", self.borders_ab[1,:]
            cv2.line(self.Cam.img,(int(self.borders_ab[0,1]*width),0), (int(self.borders_ab[0,1]*width + height*self.borders_ab[0,2]*width/height),height),(0,0,255),2)
            cv2.line(self.Cam.img,(int(self.borders_ab[1,1]*width),0), (int(self.borders_ab[1,1]*width + height*self.borders_ab[1,2]*width/height),height),(0,0,255),2)
            cv2.imwrite("/home/pi/www/images/FindBorders.jpg",self.Cam.img)
            
        # store values in database
        self.P.StoreParameter("borders_a_left", str(self.borders_ab[0,1]), "double")
        self.P.StoreParameter("borders_b_left", str(self.borders_ab[0,2]), "double")
        self.P.StoreParameter("borders_a_right", str(self.borders_ab[1,1]), "double")
        self.P.StoreParameter("borders_b_right", str(self.borders_ab[1,2]), "double")
        
        return True
        
        
    def CalculateWarpMatrix(self, control=False, width=1920, height=1080):
        """calculates a matrix for warping the image (perspective transformation) on basis of the shelf and border lines.
        Returns True"""
        
        # define 4 source points       
        p_src = np.zeros((4,2), np.float32)
        
        # top left corner: intersect of top shelf line and left border
        # conversion of ab parameters to xy-coordinates
        sh_a = (self.shelves_ab[0,1]-self.book_height)*height
        sh_b = self.shelves_ab[0,2]*height/width
        bord_a = self.borders_ab[0,1]*width
        bord_b = self.borders_ab[0,2]*width/height        
        # x-coord top left corner
        p_src[0,0] = (sh_a+bord_a/bord_b)/(1.0/bord_b - sh_b)
        # y-coord top left corner
        p_src[0,1] = sh_a+sh_b*p_src[0,0]
        
        # top right corner: intersect of top shelf line and right border
        # conversion of ab parameters to xy-coordinates
        bord_a = self.borders_ab[1,1]*width
        bord_b = self.borders_ab[1,2]*width/height        
        # x-coord top right corner
        p_src[1,0] = (sh_a+bord_a/bord_b)/(1.0/bord_b - sh_b)
        # y-coord top right corner
        p_src[1,1] = sh_a+sh_b*p_src[1,0]        
        
        # bottom right corner: intersect of bottom shelf line and right border
        # conversion of ab parameters to xy-coordinates
        nsh = self.no_of_shelves-1
        sh_a = self.shelves_ab[nsh,1]*height
        sh_b = self.shelves_ab[nsh,2]*height/width       
        # x-coord bottom right corner
        p_src[2,0] = (sh_a+bord_a/bord_b)/(1.0/bord_b - sh_b)
        # y-coord bottom right corner
        p_src[2,1] = sh_a+sh_b*p_src[2,0]        
        
        # bottom left corner: intersect of bottom shelf line and left border
        # conversion of ab parameters to xy-coordinates
        bord_a = self.borders_ab[0,1]*width
        bord_b = self.borders_ab[0,2]*width/height        
        # x-coord top right corner
        p_src[3,0] = (sh_a+bord_a/bord_b)/(1.0/bord_b - sh_b)
        # y-coord top right corner
        p_src[3,1] = sh_a+sh_b*p_src[3,0]  

        
        # define 4 destination points       
        p_dst = np.zeros((4,2), np.float32)
        
        # top left corner: same as src
        # x-coord top left corner
        p_dst[0,0] = p_src[0,0]
        # y-coord top left corner
        p_dst[0,1] = p_src[0,1]
        
        # top right corner
        # x-coord top right corner: same is in src
        p_dst[1,0] = p_src[1,0]
        # y-coord top right corner: same is top left corner
        p_dst[1,1] = p_dst[0,1]
        
        # bottom right corner
        # x-coord bottom right corner: same top right dst
        p_dst[2,0] = p_dst[1,0]
        # y-coord bottom right corner: take from src bottom left
        p_dst[2,1] = p_src[3,1]  
        
        # bottom left corner
        # x-coord bottom left corner: same as top left dst
        p_dst[3,0] = p_dst[0,0]
        # y-coord bottom left corner: same as bottom right dst
        p_dst[3,1] = p_dst[2,1]         

        if control == True:
            print "p_src"
            print p_src
            print "p_dst"
            print p_dst
            self.Cam.QueryImage(width,height)
            cv2.line(self.Cam.img,(p_src[0,0],p_src[0,1]), (p_src[1,0],p_src[1,1]),(0,0,255),2)
            cv2.line(self.Cam.img,(p_src[1,0],p_src[1,1]), (p_src[2,0],p_src[2,1]),(0,0,255),2)
            cv2.line(self.Cam.img,(p_src[2,0],p_src[2,1]), (p_src[3,0],p_src[3,1]),(0,0,255),2)
            cv2.line(self.Cam.img,(p_src[3,0],p_src[3,1]), (p_src[0,0],p_src[0,1]),(0,0,255),2)
            cv2.line(self.Cam.img,(p_dst[0,0],p_dst[0,1]), (p_dst[1,0],p_dst[1,1]),(0,255,255),2)
            cv2.line(self.Cam.img,(p_dst[1,0],p_dst[1,1]), (p_dst[2,0],p_dst[2,1]),(0,255,255),2)
            cv2.line(self.Cam.img,(p_dst[2,0],p_dst[2,1]), (p_dst[3,0],p_dst[3,1]),(0,255,255),2)
            cv2.line(self.Cam.img,(p_dst[3,0],p_dst[3,1]), (p_dst[0,0],p_dst[0,1]),(0,255,255),2)
            cv2.imwrite("/home/pi/www/images/CalculateWarpMatrix.jpg",self.Cam.img)
            
        # calculation of matrix
        self.matWarp = cv2.getPerspectiveTransform(p_src, p_dst)
        if control == True:
            print "matWarp"
            print self.matWarp        
        
        # store values in database
        for i in (0,1,2):
            for j in (0,1,2):
                self.P.StoreParameter(''.join(["mat_", str(i), str(j)]), str(self.matWarp[i][j]), "double")
        
        # update crop values in 0.0 ... 1.0 coord system     
        # with these crop values, crop should be performed after warping
        self.cx_left = max(0.0, p_dst[0,0]/float(width))
        self.cx_width = min(1.0, p_dst[1,0]/float(width))
        self.cy_top = max(0.0, p_dst[0,1]/float(height))
        self.cy_height = min(1.0, p_dst[3,1]/float(height))

        if control == True:
            print "crop values y: ", self.cy_top, self.cy_height
            print "crop values x: ", self.cx_left, self.cx_width
            
        self.P.StoreParameter("cy_top", str(self.cy_top), "double")
        self.P.StoreParameter("cy_height", str(self.cy_height), "double")
        self.P.StoreParameter("cx_left", str(self.cx_left), "double")
        self.P.StoreParameter("cx_width", str(self.cx_width), "double")
        
        return True  
    
    
    def FindChessboard(self, control=False, width=1920, height=1080):
        """calculates values dx,dy and a matrix matCM for mapping warped px,py coordinates to real world coodinates (cm).
        Uses a chessbord with 7 horizontal and 5 vertical squares and a length of 5 cm per square.
        Note: dx, dy and the matrix are only valid in the warped image space (self.matWarp applied to pixel coordinates)
        Returns the calculated values."""
        
        self.Cam.SetBrightness(50) # restore default value       
        self.Cam.QueryImage(width,height)         
        gray = cv2.cvtColor(self.Cam.img,cv2.COLOR_BGR2GRAY) # convert to gray image
        gray = self.WarpImg(gray) # warp
        
        ret, corners = cv2.findChessboardCorners(gray,(6,4))
        
        x_coord = np.sort(corners[:,0,0])
        y_coord = np.sort(corners[:,0,1])
        self.dx = (np.average(x_coord[-4]) - np.average(x_coord[:3]))/25.0 # px per 1cm
        self.dy = (np.average(y_coord[-4]) - np.average(y_coord[:3]))/15.0 # py per 1cm

        # calcualte distance of shelves in cm
        self.distance = 1.0 / self.dx / np.tan(self.Cam.dalpha)
        
        if control == True:
            print "dx:", self.dx, "px pro cm"
            print "dy:", self.dy, "py pro cm"
            print "distance:", self.distance, "cm"
        
        # store values in database
        self.P.StoreParameter("dx", str(self.dx), "double")
        self.P.StoreParameter("dy", str(self.dy), "double")
        self.P.StoreParameter("distance", str(self.distance), "double")
        
        # matrix for mapping warped px,px coordinates to real world cm (x = distance from left border and y = distance from bottom shelf)
        self.matCM[0,0] = 1/self.dx
        self.matCM[0,2] = -self.cx_left*width/self.dx
        self.matCM[1,1] = -1/self.dy
        self.matCM[1,2] = self.cy_height*height/self.dy
        self.matCM[2,2] = 1.0
        # store values in database
        for i in (0,1,2):
            for j in (0,1,2):
                self.P.StoreParameter(''.join(["matCM_", str(i), str(j)]), str(self.matCM[i][j]), "double")
                
        return self.dx, self.dy


    def Convert_PtoCM(self, px, py, width=1920, height=1080):
        """for a given (px,py) point returns the distance to the left border of the shelves and to the bottom shelves in cm"""
        
        if px == None or py == None:
            return None, None
            
        points = np.array([[[px,py]]],np.float32)        
        points = cv2.perspectiveTransform(points, self.matWarp) # points are converted to warped image space
        points = cv2.perspectiveTransform(points, self.matCM) # points are converted to real world space
        points = points.ravel()

        return int(points[0]), int(points[1])
        
        
    def GetLaserPosition(self, beamwidth, control=False, threshold=251, width=1920, height=1080):               
        """ parameter beamwidth is laser width in cm.
            Returns the dist_x, dist_y coordinates of the laser position, or None"""
        
        min_length = int(0.6*beamwidth*self.dx) # 60% of laser beam in pixel
        if control == True:
            print "min_length: ", min_length
        
        Crop = self.GetCropValues(width, height)
        
        self.Cam.QueryImage(width,height)
        simg = cv2.split(self.Cam.img)
        gimg = simg[1] # simg[1] is the green channel
        gimg = self.WarpImg(gimg) # warp
        gimg = self.CropImg(gimg) # crop image
        gimg = cv2.blur(gimg, (3,3) ) # blur

        
        # assuming that function CalibrateBrightness has been called before, the laser should have intensity 253...255 on the green channel 
        ret, dst = cv2.threshold(gimg, threshold, 255, cv2.THRESH_BINARY) # only keep the brightest pixels        
        if control == True:
            cv2.imwrite("/home/pi/www/images/GetLaserThreshold.jpg",dst)
            cv2.imwrite("/home/pi/www/images/GetLaserGimg.jpg",gimg)
        
        # detect contours
        contours, hierarchy = cv2.findContours( dst, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #contours1 = [cv2.approxPolyDP(cnt, 3, True) for cnt in contours]
        
        if contours != None:
            rect = []
            for cnt in contours: # find bounding rectangles and check them
                br = cv2.boundingRect(cnt) # type rect: (topleft x, topleft y, width, height)
                if control == True:
                    print br
                if br[2] >= min_length and br[3] <= 0.6*br[2]: # check on conditions
                    rect.append(br)
            
            if len(rect) == 1: # laser found
                b = rect[0]
                if control == True:
                    print "laser rect:", b             
                    # convert coordinates to image space in order to draw rectangle into self.Cam.img
                    # un-crop
                    tlx = b[0]+Crop[2]
                    tly = b[1]+Crop[0]
                    brx = b[0]+Crop[2]+b[2]
                    bry = b[1]+Crop[0]+b[3]
                    # un-warp
                    imat = np.linalg.inv(self.matWarp)
                    points = np.array([[[tlx,tly],[brx,bry]]],np.float32) # see http://answers.opencv.org/question/252/cv2perspectivetransform-with-python/
                    points = cv2.perspectiveTransform(points, imat) # reverse warp transformation for laser rectangle
                    points = points.ravel()
                    tlx = points[0]
                    tly = points[1]
                    brx = points[2]
                    bry = points[3]
                    cv2.rectangle(self.Cam.img,(tlx,tly),(brx,bry),(0,0,255),2) 
                    cv2.imwrite("/home/pi/www/images/GetLaserPosition.jpg",self.Cam.img) 
                # center of rectangle:
                dist_x = (b[0] + b[2]/2)/self.dx
                dist_y = (Crop[1]-Crop[0] - (b[1] + b[3]/2))/self.dy
                return dist_x, dist_y
            elif len(rect) > 1:
                if control == True:
                    print "more than one laser position found:"
                    print rect  
                return (None, None)
            else: # len(rect)==0
                return (None, None)
        
        else:# contours == None
            return (None, None)


    def CreateLaserMatrix(self, control = False, width = 1920, height = 1080, laser=1):
        """Determines the matrix mapping real world x_dist, y_dist coordinates onto Lx,Ly-values for the laser positions.
        Returns True, if successful, otherwise False.""" 
        
        beamwidth = 10 # width of laser beam in cm
        self.LM.SetBeamWidth(beamwidth)
        
        max_left, max_right, max_top, max_bottom = self.LM.GetMaxChannels(laser)
        if max_left > max_right:
            max_left, max_right = max_right, max_left
        if max_top > max_bottom:
            max_top, max_bottom = max_bottom, max_top
            
        src = []
        dst = []
        # collect 10 random points
        while len(src) < 10:
            Lx = randrange(max_left, max_right, 1)
            Ly = randrange(max_top, max_bottom, 1)
            self.LM.Move(Lx,Ly)
            dist_x, dist_y = self.GetLaserPosition(beamwidth,False,251,width,height)
            if dist_y != None:
                src.append([dist_x,dist_y])
                dst.append([Lx,Ly])
                if control == True:
                    print "x:", dist_x, "y:", dist_y, "Lx:", Lx, "Ly:", Ly

        src = np.array([src],np.float32)
        dst = np.array([dst],np.float32)
        self.matCMtoL, mask = cv2.findHomography(src,dst,cv2.RANSAC,1.0)

        if control == True:
            print "matCMtoL"
            print self.matCMtoL       
               
        # store values in database
        for i in (0,1,2):
            for j in (0,1,2):
                self.P.StoreParameter(''.join(["matCMtoL_", str(i), str(j)]), str(self.matCMtoL[i][j]), "double")     
                
        return True
        
        
    def Convert_CMtoL(self, dist_x, dist_y, width=1920, height=1080, laser=1):
        """calculates the laser channels from real world coordinates (distance in cm from the left border of the shelves and from the bottom shelf).
        Checks against the possible laser channels. Returns the calculated values, or None"""
                
        max_left, max_right, max_top, max_bottom = self.LM.GetMaxChannels(laser)                
        
        points = np.array([[[dist_x,dist_y]]],np.float32)
        points = cv2.perspectiveTransform(points, self.matCMtoL)
        points = points.ravel()
        Lx = int(round(points[0]))
        Ly = int(round(points[1]))
        
        Lx_max = max(max_left, max_right)
        Lx_min = min(max_left, max_right)        
        Ly_max = max(max_top, max_bottom)
        Ly_min = min(max_top, max_bottom)
        
        if Lx <= Lx_max and Lx >= Lx_min and Ly <= Ly_max and Ly >= Ly_min:      
            return Lx, Ly
        else:
            return None, None
        
        
    def Convert_LtoCM(self, Lx, Ly, width=1920, height=1080):
        """calculates the distance in cm from the left border of the shelves and from the bottom shelf.
        Returns the calculated values, or None"""
                
        imat = np.linalg.inv(self.matCMtoL) # inverse self.matCMtoL
        points = np.array([[[Lx,Ly]]],np.float32)
        points = cv2.perspectiveTransform(points, imat)
        points = points.ravel()
            
        return int(points[0]), int(points[1])
    
    
    def AssignLaserToShelves(self, control = False, width=1920, height=1080, laser=1):
        """Calculates the Ly values for the shelves and stores in database. Returns True"""
        
        max_left, max_right, max_top, max_bottom = self.LM.GetMaxChannels(laser)
            
        x_mid = int((self.cx_left + (self.cx_width-self.cx_left)/2)*width) # x-coord of mid of shelves
        
        for i in xrange(0, self.no_of_shelves,1):
            y_shelf = int((self.shelves_ab[i,1] - 0.25*self.book_height)*height + self.shelves_ab[i,2]*height/width*x_mid)  # y-coord of shelf at x_mid (- 0.25 book_height)
            dist_x, dist_y = self.Convert_PtoCM(x_mid, y_shelf)
            Lx, Ly = self.Convert_CMtoL(dist_x, dist_y)
            if Ly != None:
                if control==True:
                    print i, int(x_mid), int(y_shelf), Lx, Ly
                self.P.StoreParameter(''.join(["y_row_", str(i+1)]), str(Ly), "integer")
            
        return True
    

    def Convert_PtoShelf(self, px, py, width=1920, height=1080):
        """for a given (px,py) point returns number of the shelf, this points sits on. Top shelf number is 1"""
        
        for i in xrange(0, self.no_of_shelves,1): # iterate from top to bottom
            y_shelf = int(self.shelves_ab[i,1]*height + self.shelves_ab[i,2]*height/width*px)  # y-coord of shelf at px
            if py < y_shelf:
                return i+1

        return None
        
        
    def DetectMissingBook(self, step, control=False, width=1920, height=1080):
        """detects position of missing (or added) books from comparing two subsequent images.
        Function needs to be called in sequence (step = 1 and step = 2).
        Returns the (dist_x, dist_y) real world coordinates, and the number of the shelf, or (None, None, None)"""
        
        if control == True:
            print "step", step
        
        if step == 2:
            # read previous picture and corresponding time-stamp
            gimg1 = cv2.imread("/home/pi/www/images/detect_book.jpg", 0)
            last_img_time = self.P.GetParameter("last_img_time")
        
        # take new picture
        self.Cam.QueryImage(width,height)
        gray = cv2.cvtColor(self.Cam.img,cv2.COLOR_BGR2GRAY) # convert to gray image
        gimg = self.WarpImg(gray) # warp
        gimg2 = self.CropImg(gimg) # crop image
        
        # store new picture as the next previous picture and store actual date-time in database
        cv2.imwrite("/home/pi/www/images/detect_book.jpg",gimg2)        
        self.P.StoreParameter("last_img_time", str(time.time()), "double")
        
        if step == 1: # nothing else to do
            return None, None, None
            
        # proceed if step > 1
        # do nothing, if old picture not present or not actual
        if gimg1 == None or last_img_time == None: 
            return None, None, None
            
        t_diff = time.time() - last_img_time
        if t_diff > 60: # no more than a minute difference; images should be taken in close sequence
            if control == True:
                print "time difference too big:", t_diff
            return None, None, None
            
        gimg = cv2.absdiff(gimg1, gimg2)
        ret, threshold_output = cv2.threshold(gimg, 30, 255, cv2.THRESH_BINARY)
        #threshold_output = cv2.adaptiveThreshold(gimg, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        if control == True:
            cv2.imwrite("/home/pi/www/images/MissingBook_threshold.jpg",threshold_output) 
            
        # detect contours
        contours, hierarchy = cv2.findContours( threshold_output, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #contours1 = [cv2.approxPolyDP(cnt, 3, True) for cnt in contours]
        
        min_height = int(0.3*self.book_height*height) # min height of missing book  
        max_height = int(2*self.book_height*height) # max height of missing book 
        min_width = int(0.05*self.book_height*height)      
        Crop = self.GetCropValues(width, height) # needed for un-cropping the coordinates   
        
        if contours != None:
            for cnt in contours: # find bounding rectangles and check them
                br = cv2.boundingRect(cnt) # type rect: (topleft x, topleft y, width, height)
                if br[3] > min_height and br[3] < max_height and br[2] < br[3] and br[2] > min_width: # check on conditions
                    tlx = br[0]+Crop[2]
                    tly = br[1]+Crop[0]
                    brx = br[0]+Crop[2]+br[2]
                    bry = br[1]+Crop[0]+br[3]
                    imat = np.linalg.inv(self.matWarp)
                    points = np.array([[[tlx,tly],[brx,bry]]],np.float32) # see http://answers.opencv.org/question/252/cv2perspectivetransform-with-python/
                    points = cv2.perspectiveTransform(points, imat) # reverse warp transformation for book rectangle
                    points = points.ravel()
                    tlx = int(points[0])
                    tly = int(points[1])
                    brx = int(points[2])
                    bry = int(points[3])
                    if control == True:
                        print "rect:", br            
                        cv2.rectangle(self.Cam.img,(tlx,tly),(brx,bry),(255,255,255),2) 
                        cv2.imwrite("/home/pi/www/images/MissingBook.jpg",self.Cam.img)
                        cv2.rectangle(gimg2,(br[0],br[1]),(br[0]+br[2],br[1]+br[3]),255,2)
                        cv2.imwrite("/home/pi/www/images/MissingBookGimg.jpg",gimg2)  
                    dist_x, dist_y = self.Convert_PtoCM(int((tlx+brx)/2),int((bry+tly)/2))  # center of book
                    row = self.Convert_PtoShelf(int((tlx+brx)/2), int((bry+tly)/2))
                    return dist_x, dist_y, row
        return None,None,None
        

        
        