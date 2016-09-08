import time
from MovingAvg import MovingAvg
from PdConnection import PdConnection      
import Adafruit_MPR121.MPR121 as MPR121

def init(cap):
    # Soft reset of device.
    cap._i2c_retry(cap._device.write8, MPR121.MPR121_SOFTRESET, 0x63)
    time.sleep(0.001) # This 1ms delay here probably isn't necessary but can't hurt.
    # Set electrode configuration to default values.
    cap._i2c_retry(cap._device.write8, MPR121.MPR121_ECR, 0x00)
    # Check CDT, SFI, ESI configuration is at default values.
    c = cap._i2c_retry(cap._device.readU8, MPR121.MPR121_CONFIG2)
    if c != 0x24:
        return False
    # Set threshold for touch and release to default values.
    cap.set_thresholds(1,1)
    # Configure baseline filtering control registers.

    # Set other configuration registers.
    cap._i2c_retry(cap._device.write8, MPR121.MPR121_DEBOUNCE, 3)
    cap._i2c_retry(cap._device.write8, MPR121.MPR121_CONFIG1, 0x3F) # default, 16uA charge current
    cap._i2c_retry(cap._device.write8, MPR121.MPR121_CONFIG2, 0x20) # 0.5uS encoding, 1ms period
    # Enable all electrodes.
    cap._i2c_retry(cap._device.write8, MPR121.MPR121_ECR, 0x8F) # start with first 5 bits of baseline tracking
    
    # Setup the autoconfig
    cap1._i2c_retry(cap1._device.write8, MPR121.MPR121_AUTOCONFIG0, 0b10101110)
    cap1._i2c_retry(cap1._device.write8, MPR121.MPR121_AUTOCONFIG1, 0)

# Create MPR121 instance
cap1 = MPR121.MPR121()

# Initialize communication with MPR121
cap1.begin( 0x5a )
init(cap1)

# Create connection to PD and open a log file
pd = PdConnection('localhost', 3000)
logFile = open('singing_plants.log', 'a')

pins = [0,2,4,5]
ccount = 0
avg = 0
buffer = [0, 0, 0, 0]
pState = 0
bs = 5
mavg = [MovingAvg(bs), MovingAvg(bs), MovingAvg(bs), MovingAvg(bs)]

cap1.touched()

# Start loop
while True:

    # Get current state
    tcd = cap1.touched()
    
    # Send zeros once if released
    if pState > 0 and tcd == 0:
        
        for i in range(4):
            mavg[i].reset()
            try:
                pd.sendValue('pin' + str(i), 0)
            except Exception as e:
                logFile.write('\n' + str(e))
    
    # Send values if touching
    elif tcd > 0:

        # Calculate difference for all pins
        diff1 = [cap1.baseline_data(i) - cap1.filtered_data(i) for i in pins]

        # Print the differences
        print 'Diff:\t', '\t'.join(map(str, diff1))
        
        # Raw values
        '''            
        for i in range(4):
            try:
                pd.sendValue('pin' + str(i), diff1[i])
            except Exception as e:
                print str(e)
                logFile.write('\n' + str(e))
        '''   

        # Average every 10 readings
        '''
        if ccount == 10:
            ccount = 0
            for i in range(4):
                try:
                    pd.sendValue('pin' + str(i), buffer[i]/10)
                    buffer[i] = 0
                except Exception as e:
                    print str(e)
                    logFile.write('\n' + str(e))
        else:
	    for i in range(4):
                buffer[i] += diff1[i]
	
        ccount += 1
        '''
    
        # Moving average
        for i in range(4):
            mavg[i].add(diff1[i])
            avg = mavg[i].get()
            # print 'Avg' + str(i), ':\t', avg
            try:
                pd.sendValue('pin' + str(i), avg if cap1.is_touched(pins[i]) else 0)
            except Exception as e:
                print str(e)
                logFile.write('\n' + str(e))

    # Reset every minute
    if ccount >= 600:
        ccount = 0
        init(cap1)
        print 'Reinitializing the sensor'
    
    # Save previous state
    pState = tcd

    # Short pause before repeating loop
    time.sleep(0.1)

    # Increase cycle counter
    ccount += 1
