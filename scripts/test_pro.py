from DmxPro import DmxPro
import time

dmx = DmxPro('/dev/ttyUSB0')

dmx.setChannel(1,252) # DMX Betrieb
dmx.setChannel(2,0) # Pattern
dmx.setChannel(3,120) # Zoom
dmx.setChannel(4,0) # Rotation um y
dmx.setChannel(5,0) # Rotation um x
dmx.setChannel(6,0)  # Rotation um z
dmx.setChannel(7,0)  # x-Achse
dmx.setChannel(8,0)  # y-Achse
dmx.setChannel(9,32)  # Farbe: 16=rot, 32=gruen, 48=gelb, 127=wechselnd

dmx.send()



