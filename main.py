import time
import ntptime
import network
from pimoroni_i2c import PimoroniI2C
from breakout_msa301 import BreakoutMSA301
from pimoroni import Button
from machine import Pin
from d1_libary import emote, func, system
from machine import Timer

PINS_BREAKOUT_GARDEN = {"sda": 4, "scl": 5}
i2c = PimoroniI2C(**PINS_BREAKOUT_GARDEN)
msa = BreakoutMSA301(i2c)

#MSA301
part_id = msa.part_id()
print("Found MSA301. Part ID: 0x", '{:02x}'.format(part_id), sep="")

msa.enable_interrupts(BreakoutMSA301.FREEFALL | BreakoutMSA301.ORIENTATION)

#Import Functions and Emotes from D1_lib
emote = emote()
func = func()
system = system()

#Values
buttonpress = 0
idler_ran = 0

# connect the network       
system.wifi_connect()

# Connect to MQTT broker
system.mqtt_connect()

while True:

    func.current_time()
    minute = func.current_time()
    
    if str(msa.get_orientation()) != "1" : # if moved shocked face
        emote.shockedblink()
    
    while system.get_button1() == 1: 
        buttonpress += 1
        time.sleep(1)
        
    while system.get_button2() == 1:
        emote.shockedblink()
        system.button2_pressed()
        
    while buttonpress == 1: 
        func.showtime()
        if system.get_button1() == 1:
            buttonpress += 1
            time.sleep(1)
            
    while buttonpress == 2: 
        func.showtemp()
        if system.get_button1() == 1:
            buttonpress += 1
            time.sleep(1)
            
    while buttonpress == 3: 
        func.weather_test()
        if system.get_button1() == 1:
            buttonpress += 1
            time.sleep(1)
    
    if buttonpress == 4:
        buttonpress = 0
        idler_ran = 0
        func.reset_run_once()
            
    if idler_ran == 0:
        func.idle_time()
        idle = func.idle_time()
        idler_ran = 1
    
    while minute == idle: 
        emote.snooze1()
        time.sleep(1)
        emote.snooze2()
        time.sleep(1)
        if system.get_button1() == 1:
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

        
