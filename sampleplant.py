import time
from MovingAvg import MovingAvg
import Adafruit_MPR121.MPR121 as MPR121
import time
import pygame
import sys

last_reset = time.time()

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

    last_reset = time.time()

# Create MPR121 instance
cap1 = MPR121.MPR121()

# Initialize communication with MPR121
cap1.begin( 0x5a )
init(cap1)

#logFile = open('singing_plants.log', 'a')

pins = [0,2,4,5]
ccount = 0
avg = 0
buffer = [0, 0, 0, 0]
pState = 0
bs = 5
mavg = [MovingAvg(bs), MovingAvg(bs), MovingAvg(bs), MovingAvg(bs)]

cap1.touched()

pygame.mixer.pre_init(44100, -16, 12, 512)
pygame.init()

SOUND_MAPPING = {
  3: ['samples/loop_amen.wav',0.7,True],
  1: ['samples/ambi_drone.wav',1,True],
  2: ['samples/bass_voxy_c.wav',0.5,True],
  0: ['samples/ppap.wav',0.5,True]
}

sounds = [0,0,0,0]
is_loop = [False,False,False,False]

for key,data in SOUND_MAPPING.iteritems():
        soundfile, volume, loop = data
        sounds[key] =  pygame.mixer.Sound(soundfile)
        sounds[key].set_volume(volume);
        is_loop[key] = loop

sounds_playing = [False,False,False,False]
print is_loop



def playSound(sound_id):
    if is_loop[sound_id]:
        if not sounds_playing[sound_id]:
            sounds[sound_id].play(loops = -1)
            sounds_playing[i] = True
    else:
        sounds[sound_id].play()
        sounds_playing[i] = True

def stopSound(sound_id):
    sounds[i].stop()
    sounds_playing[i] = False
    
# Start loop
while True:

    # Get current state
    tcd = cap1.touched()
    
    # Send zeros once if released
    if pState > 0 and tcd == 0:
        
        for i in range(4):
            mavg[i].reset()
            #stop sounds
            stopSound(i)
            # try:
            #     # play sound

            #     #pd.sendValue('pin' + str(i), 0)
            # except Exception as e:
            #     logFile.write('\n' + str(e))
    
    # Send values if touching
    elif tcd > 0:

        # Calculate difference for all pins
        diff1 = [cap1.baseline_data(i) - cap1.filtered_data(i) for i in pins]

        # Print the differences
        print 'Diff:\t', '\t'.join(map(str, diff1))
        
    
        # Moving average
        for i in range(4):
            mavg[i].add(diff1[i])
            avg = mavg[i].get()
            # print 'Avg' + str(i), ':\t', avg
            try:
                #pd.sendValue('pin' + str(i), avg if cap1.is_touched(pins[i]) else 0)
                if cap1.is_touched(pins[i]):
                    playSound(i)
                else:
                    stopSound(i)

            except Exception as e:
                print str(e)
                logFile.write('\n' + str(e))

    # Reset every minute
    if time.time() - last_reset > 60:
        init(cap1)
        print 'Reinitializing the sensor'
        last_reset = time.time()
    
    # Save previous state
    pState = tcd

    # Short pause before repeating loop
    time.sleep(0.1)

    # Increase cycle counter
    #ccount += 1
