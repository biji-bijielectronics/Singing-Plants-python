import OSC
import time
send_address = 'localhost' , 4557
c = OSC.OSCClient()
c.connect(send_address)


def sendMessage(address, value):
	msg = OSC.OSCMessage()
	msg.setAddress(address)
	msg.append("SONIC_PI_PIPE")
	msg.append(value)
	c.send(msg)

print 'here'
time.sleep(1)
print 'sound 1'
sendMessage("/run-code", "play 60")
time.sleep(1)
print 'sound 2'

sendMessage("/run-code", "play 65")
time.sleep(1)