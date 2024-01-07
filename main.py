import time
import ntptime
import urequests
import network
from secret import ssid, password
from pimoroni_i2c import PimoroniI2C
from breakout_msa301 import BreakoutMSA301
from pimoroni import Button
from machine import Pin
from d1_libary import emote, func
from machine import Timer

PINS_BREAKOUT_GARDEN = {"sda": 4, "scl": 5}
i2c = PimoroniI2C(**PINS_BREAKOUT_GARDEN)
msa = BreakoutMSA301(i2c)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

#MSA301
part_id = msa.part_id()
print("Found MSA301. Part ID: 0x", '{:02x}'.format(part_id), sep="")

msa.enable_interrupts(BreakoutMSA301.FREEFALL | BreakoutMSA301.ORIENTATION)

#Import Functions and Emotes from D1_lib
emote = emote()
func = func()

#Values
buttonpress = 0
idler_ran = 0

#Button 1
buttonPIN = 0
button1 = Pin(buttonPIN, Pin.IN, Pin.PULL_UP)

#Get button values
def get_button1():
    return not button1.value()

# connect the network       
wait = 10
while wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    wait -= 1
    print('waiting for connection...')
    time.sleep(1)
 
# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('wifi connection failed')
else:
    print('connected')
    ip=wlan.ifconfig()[0]
    print('IP: ', ip)

while True:

    func.current_time()
    minute = func.current_time()
    
    if str(msa.get_orientation()) != "1" : # if moved shocked face
        emote.shockedblink()
    
    if buttonpress == 4:
        buttonpress = 0
        idler_ran = 0
        func.reset_run_once()
    
    while get_button1() == 1: 
        buttonpress += 1
        time.sleep(1)
        
    while buttonpress == 1: 
        func.showtime()
        if get_button1() == 1:
            buttonpress += 1
            time.sleep(1)
            
    while buttonpress == 2: 
        func.showtemp()
        if get_button1() == 1:
            buttonpress += 1
            time.sleep(1)
            
    while buttonpress == 3: 
        func.weather_test()
        if get_button1() == 1:
            buttonpress += 1
            time.sleep(1)
            
    if idler_ran == 0:
        func.idle_time()
        idle = func.idle_time()
        idler_ran = 1
    
    while minute == idle:
        emote.snooze1()
        time.sleep(1)
        emote.snooze2()
        time.sleep(1)
        if get_button1() == 1:
            idle = 100 # reset idle
            idler_ran=0 # reset idle
            emote.awakeblink()
            time.sleep(1)
        if str(msa.get_orientation()) != "1" : # if moved shocked face
            idle = 100 # reset idle
            idler_ran=0 # reset idle
            emote.awakeblink()
            time.sleep(1)
    
    if minute != idle:
         emote.neutral()

        
