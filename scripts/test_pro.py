from DmxPro import DmxPro

dmx = DmxPro('/dev/ttyUSB0')

dmx.setChannel(1,252) # DMX mode
dmx.setChannel(2,152) # pattern
dmx.setChannel(3,120) # zoom
dmx.setChannel(4,0) # rotation y
dmx.setChannel(5,0) # rotation x
dmx.setChannel(6,0)  # rotation z
dmx.setChannel(7,0)  # move to x position
dmx.setChannel(8,0)  # move to y position
dmx.setChannel(9,32)  # color: 16=red, 32=green, 48=yellow (both), 127=changing

dmx.send()



