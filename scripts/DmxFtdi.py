import ftdi, sys

DMX_DATA_LENGTH = 9 # depending on the number of channels needed for the DMX device; max. 512
START_CODE = chr(0) # start code of DMX protocol

class DmxFtdi:
        def __init__(self):
            try:
                self.ftdic = ftdi.ftdi_context()

                if ftdi.ftdi_init(self.ftdic) < 0:
                    print "ftdi_init failed"
                    sys.exit(0)

                ret = ftdi.ftdi_usb_open(self.ftdic, 0x0403, 0x6001) # The Enttec Open DMX device is identified with these IDs
                if (ret) < 0:
                    print "ftdi_usb_open failed"
                    print ret
                    print ftdi.ftdi_get_error_string(self.ftdic)
                    sys.exit(0)

                ret = ftdi.ftdi_set_baudrate(self.ftdic, 250000) # The 250K Baud is required by the DMX standard
                if (ret) < 0:
                    print "ftdi_set_baudrate failed"
                    print ret
                    print ftdi.ftdi_get_error_string(self.ftdic)
                    sys.exit(0)

                ret = ftdi.ftdi_set_line_property2(self.ftdic,8,2,0,1) # 8 data bits + 2 stop bits required by the DMX standard
                if (ret) < 0:
                    print "ftdi_set_line_property failed"
                    print ret
                    print ftdi.ftdi_get_error_string(self.ftdic)
                    sys.exit(0)
                
            except:
                print "Error: could not open and configure FTDI device"
                sys.exit(0)

            self.buffer=bytearray(DMX_DATA_LENGTH)

    def setChannel(self, chan, value):
            # chan: 1...DMX_DATA_LENGTH; value: 1...127
            self.buffer[chan-1] = chr(value) # note: 1st channel is self.buffer[0]

    def clearChannels(self):
            self.buffer = bytearray(DMX_DATA_LENGTH)

        def send(self):
            #toogle BREAK on line as required by the DMX standard
            ftdi.ftdi_set_line_property2(self.ftdic,8,2,0,0)
            ftdi.ftdi_set_line_property2(self.ftdic,8,2,0,1)
            ftdi.ftdi_set_line_property(self.ftdic,8,2,0) # without this additional command nothing is sent out. Bug in ftdi class?
            # convert buffer to string and add START_CODE
            payload = START_CODE + str(self.buffer)
            #print sdata.encode("hex")
            ftdi.ftdi_write_data(self.ftdic,payload,DMX_DATA_LENGTH+1)
