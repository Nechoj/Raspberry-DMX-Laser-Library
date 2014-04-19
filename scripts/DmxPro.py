import serial, sys

SOM = chr(0x7E) # start of message
EOM = chr(0xE7) # end of message
LABEL_SEND = chr(6) # message type for sending data
START_CODE = chr(0) # start code of DMX protocol


class DmxPro:
    def __init__(self, serialPort, p_nr_channels):
        # serial port is a string, e.g. '/dev/ttyUSB0'
        # p_nr_channels is the number of DMX channels used; min 25, max 512 - depending on the number of channels needed for the DMX devices
        try:
            self.serial=serial.Serial(serialPort, baudrate=115200)
        except:
            print "Error: could not open Serial Port"
            sys.exit(1)
        
        self.nr_channels = p_nr_channels
        self.buffer=bytearray(self.nr_channels) # array for holding the data to be sent
        
        # message length most significant byte            
        self.MsgLen_MSB = chr((self.nr_channels+1) >> 8) # self.nr_channels+1 because the START_CODE is added to the buffer        
        # message length least significant byte
        self.MsgLen_LSB = chr((self.nr_channels+1) % 256) 
        
    
    def setChannels(self, p_offset, p_buffer):
        # p_offset: channel number to start with
        # p_buffer: data to be send as bytearray
        end = p_offset + len(p_buffer)
        if end > self.nr_channels:
            print "self.buffer exceeded"
            sys.exit(1)
        
        self.buffer[p_offset:end] = p_buffer


    def send(self):
        # convert byte array to string
        payload = str(self.buffer)
        # send out
        #print (SOM+LABEL_SEND+self.MsgLen_LSB+self.MsgLen_MSB+START_CODE+payload+EOM).encode("hex")
        self.serial.write(SOM+LABEL_SEND+self.MsgLen_LSB+self.MsgLen_MSB+START_CODE+payload+EOM)
