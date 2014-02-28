import ftdi, sys

DMX_DATA_LENGTH = 9

class DmxFtdi:
        def __init__(self):
            try:
                self.ftdic = ftdi.ftdi_context()

                if ftdi.ftdi_init(self.ftdic) < 0:
                    print "ftdi_init failed"
                    sys.exit(0)

                ret = ftdi.ftdi_usb_open(self.ftdic, 0x0403, 0x6001)
                if (ret) < 0:
                    print "ftdi_usb_open failed"
                    print ret
                    print ftdi.ftdi_get_error_string(self.ftdic)
                    sys.exit(0)

                ret = ftdi.ftdi_set_baudrate(self.ftdic, 250000)
                if (ret) < 0:
                    print "ftdi_set_baudrate failed"
                    print ret
                    print ftdi.ftdi_get_error_string(self.ftdic)
                    sys.exit(0)

                ret = ftdi.ftdi_set_line_property2(self.ftdic,8,2,0,1)
                if (ret) < 0:
                    print "ftdi_set_line_property failed"
                    print ret
                    print ftdi.ftdi_get_error_string(self.ftdic)
                    sys.exit(0)
                
            except:
                print "Error: could not open and configure FTDI device"
                sys.exit(0)

            self.buffer=bytearray(DMX_DATA_LENGTH+1)   # including  leading '0' startcode

    def setChannel(self, chan, value):
            # chan: 1...DMX_DATA_LENGTH; value: 1...127
            self.buffer[chan] = chr(value) # note: 1st channel is self.buffer[1], startcode is self.buffer[0]

    def clearChannels(self):
            self.buffer = bytearray(DMX_DATA_LENGTH+1)

        def send(self):
            #toogle BREAK on line
            ftdi.ftdi_set_line_property2(self.ftdic,8,2,0,0)
            ftdi.ftdi_set_line_property2(self.ftdic,8,2,0,1)
            ftdi.ftdi_set_line_property(self.ftdic,8,2,0) # without this additional command nothing happens. Bug in ftdi class?
            # convert buffer to string
            sdata = str(self.buffer)
            #print sdata.encode("hex")
            ftdi.ftdi_write_data(self.ftdic,sdata,DMX_DATA_LENGTH+1)
