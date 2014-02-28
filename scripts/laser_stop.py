from DmxPro import DmxPro

dmx = DmxPro('/dev/ttyUSB0')
dmx.clearChannels()
dmx.send()
