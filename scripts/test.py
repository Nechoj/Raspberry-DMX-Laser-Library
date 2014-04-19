from CVision import Cam
import time

C = Cam()
time.sleep(15)
C.QueryImage()
C.WriteImage("../images/test_ocr.jpg")