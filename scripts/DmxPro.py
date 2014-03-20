import serial, sys

SOM = chr(0x7E) # start of message
EOM = chr(0xE7) # end of message
DMX_DATA_LENGTH = 25 # min 25, max 512 - depending on the number of channels needed for the DMX devices
LABEL_SEND = chr(6) # message type for sending data
START_CODE = chr(0) # start code of DMX protocol


class DmxPro:
    def __init__(self, serialPort):
            try:
                self.serial=serial.Serial(serialPort, baudrate=115200)
            except:
                print "Error: could not open Serial Port"
                sys.exit(1)
        
            self.buffer=bytearray(DMX_DATA_LENGTH) # array for holding the data to be sent
        
            # message length most significant byte            
            self.MsgLen_MSB = chr((DMX_DATA_LENGTH+1) >> 8) # DMX_DATA_LENGTH+1 because the START_CODE is added to the buffer        
            # message length least significant byte
            self.MsgLen_LSB = chr((DMX_DATA_LENGTH+1) % 256) 
        
    def setChannel(self, chan, value):
            # chan: 1...DMX_DATA_LENGTH; value: 0...255
            if chan <= DMX_DATA_LENGTH:
                self.buffer[chan-1] = chr(value) # note: 1st channel is self.buffer[0]
            else:
                print "channel number not allowed"
                sys.exit(1)

    def send(self):
            # convert byte array to string
            payload = str(self.buffer)
            # send out
            #print (SOM+LABEL_SEND+self.MsgLen_LSB+self.MsgLen_MSB+START_CODE+payload+EOM).encode("hex")
            self.serial.write(SOM+LABEL_SEND+self.MsgLen_LSB+self.MsgLen_MSB+START_CODE+payload+EOM)
