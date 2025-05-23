import time
import ntptime
import network
import d1_libary
from pimoroni_i2c import PimoroniI2C
from breakout_msa301 import BreakoutMSA301
from pimoroni import Button
from machine import Pin
from d1_libary import emote, func, system, menu_page
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
idler_ran = 0

# connect the network       
system.wifi_connect()

# Connect to MQTT broker
system.mqtt_connect()

while True:
    
    while d1_libary.menu_page == 0: 
        func.current_time()
        minute = func.current_time()
    
        if str(msa.get_orientation()) != "1" : # if moved shocked face
            emote.shockedblink()
        
        while system.get_button1() == 1: 
            system.button_press1()
        while system.get_button2() == 1:
            system.button_press2()
        while system.get_button3() == 1:
            system.button_press3()
        while system.get_button4() == 1:
            system.button_press4()
        while system.get_button5() == 1:
            system.button_press5()
        while system.get_button6() == 1:
            system.button_press6()
            
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

        
    while d1_libary.menu_page == 1: 
        func.showtime()
        while system.get_button1() == 1:
            system.button_press1()
        while system.get_button2() == 1:
            system.button_press2()
        while system.get_button3() == 1:
            system.button_press3()
        while system.get_button4() == 1:
            system.button_press4()
        while system.get_button5() == 1:
            system.button_press5()
        while system.get_button6() == 1:
            system.button_press6()
            
    while d1_libary.menu_page == 2: 
        func.reset_run_once()
        func.showtemp()
        while system.get_button1() == 1:
            system.button_press1()
        while system.get_button2() == 1:
            system.button_press2()
        while system.get_button3() == 1:
            system.button_press3()
        while system.get_button4() == 1:
            system.button_press4()
        while system.get_button5() == 1:
            system.button_press5()
        while system.get_button6() == 1:
            system.button_press6()
            
    while d1_libary.menu_page == 3: 
        func.weather()
        while system.get_button1() == 1:
            system.button_press1()
        while system.get_button2() == 1:
            system.button_press2()
        while system.get_button3() == 1:
            system.button_press3()
        while system.get_button4() == 1:
            system.button_press4()
        while system.get_button5() == 1:
            system.button_press5()
        while system.get_button6() == 1:
            system.button_press6()

    while d1_libary.menu_page == 4: 
        func.reset_run_once()
        func.network_dash()
        while system.get_button1() == 1:
            system.button_press1()
        while system.get_button2() == 1:
            system.button_press2()
        while system.get_button3() == 1:
            system.button_press3()
        while system.get_button4() == 1:
            system.button_press4()
        while system.get_button5() == 1:
            system.button_press5()
        while system.get_button6() == 1:
            system.button_press6()
    
    if d1_libary.menu_page == 5:
        d1_libary.menu_page = 0
        idler_ran = 0
        func.reset_run_once()

    if d1_libary.menu_page == -1:
        d1_libary.menu_page = 4
        func.reset_run_once()
import time
import ntptime
import network
import d1_libary
from pimoroni_i2c import PimoroniI2C
from breakout_msa301 import BreakoutMSA301
from pimoroni import Button
from machine import Pin
from d1_libary import emote, func, system, menu_page
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
idler_ran = 0

# connect the network       
system.wifi_connect()

# Connect to MQTT broker
system.mqtt_connect()

while True:
    
    while d1_libary.menu_page == 0: 
        func.current_time_minutes()
        minute = func.current_time_minutes()
    
        if str(msa.get_orientation()) != "1" : # if moved shocked face
            emote.shockedblink()
        
        while system.get_button1() == 1: 
            system.button_press1()
        while system.get_button2() == 1:
            system.button_press2()
        while system.get_button3() == 1:
            system.button_press3()
        while system.get_button4() == 1:
            system.button_press4()
        while system.get_button5() == 1:
            system.button_press5()
        while system.get_button6() == 1:
            system.button_press6()
            
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

        
    while d1_libary.menu_page == 1: 
        func.showtime()
        while system.get_button1() == 1:
            system.button_press1()
        while system.get_button2() == 1:
            system.button_press2()
        while system.get_button3() == 1:
            system.button_press3()
        while system.get_button4() == 1:
            system.button_press4()
        while system.get_button5() == 1:
            system.button_press5()
        while system.get_button6() == 1:
            system.button_press6()
            
    while d1_libary.menu_page == 2: 
        func.reset_run_once()
        func.showtemp()
        while system.get_button1() == 1:
            system.button_press1()
        while system.get_button2() == 1:
            system.button_press2()
        while system.get_button3() == 1:
            system.button_press3()
        while system.get_button4() == 1:
            system.button_press4()
        while system.get_button5() == 1:
            system.button_press5()
        while system.get_button6() == 1:
            system.button_press6()
            
    while d1_libary.menu_page == 3: 
        func.weather()
        while system.get_button1() == 1:
            system.button_press1()
        while system.get_button2() == 1:
            system.button_press2()
        while system.get_button3() == 1:
            system.button_press3()
        while system.get_button4() == 1:
            system.button_press4()
        while system.get_button5() == 1:
            system.button_press5()
        while system.get_button6() == 1:
            system.button_press6()

    while d1_libary.menu_page == 4: 
        func.current_time_full()
        ctime = func.current_time_full()
        sleeptime = "23:00"
        waketime = "9:00"
        
        
        while ctime == sleeptime: 
            func.routiner_sleep()
        
        while system.get_button1() == 1:
            system.button_press1()
        while system.get_button2() == 1:
            system.button_press2()
        while system.get_button3() == 1:
            system.button_press3()
        while system.get_button4() == 1:
            system.button_press4()
        while system.get_button5() == 1:
            system.button_press5()
        while system.get_button6() == 1:
            system.button_press6()
    
    if d1_libary.menu_page == 5:
        d1_libary.menu_page = 0
        idler_ran = 0
        func.reset_run_once()

    if d1_libary.menu_page == -1:
        d1_libary.menu_page = 4
        func.reset_run_once()
