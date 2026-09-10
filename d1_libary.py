import time
import ntptime
import urequests
import network
import uping
import machine
import socket
import struct
from umqttsimple import MQTTClient
from secret import *
from pimoroni_i2c import PimoroniI2C
from picographics import PicoGraphics, DISPLAY_LCD_240X240, PEN_P8
from breakout_bme280 import BreakoutBME280
from breakout_msa301 import BreakoutMSA301
from breakout_rtc import BreakoutRTC
from machine import Pin

PINS_BREAKOUT_GARDEN = {"sda": 4, "scl": 5}
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

i2c = PimoroniI2C(**PINS_BREAKOUT_GARDEN)
bme = BreakoutBME280(i2c)
msa = BreakoutMSA301(i2c)
rtc = BreakoutRTC(i2c)
rtcpico = machine.RTC()
NTP_DELTA = 2208988800 - 3600
time_host = "pool.ntp.org"
display = PicoGraphics(display=DISPLAY_LCD_240X240, pen_type=PEN_P8)
display.set_backlight(1.0)
display.set_font("bitmap8")
WIDTH, HEIGHT = display.get_bounds()

RED   = display.create_pen(255, 000, 000)   
GREEN = display.create_pen(000, 255, 000)
BLUE  = display.create_pen(000, 000, 255)
WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
RAIN  = display.create_pen(56, 194, 231)
CLOUD = display.create_pen(157, 165, 167)
SUN = display.create_pen(252, 186, 3)

#Button 1
buttonPIN = 11
button1 = Pin(buttonPIN, Pin.IN, Pin.PULL_UP)

#Button 2
buttonPIN = 10
button2 = Pin(buttonPIN, Pin.IN, Pin.PULL_UP)

#Button 3
buttonPIN = 12
button3 = Pin(buttonPIN, Pin.IN, Pin.PULL_UP)

#Button 4
buttonPIN = 13
button4 = Pin(buttonPIN, Pin.IN, Pin.PULL_UP)

#Button 5
buttonPIN = 14
button5 = Pin(buttonPIN, Pin.IN, Pin.PULL_UP)

#Button 6
buttonPIN = 15
button6 = Pin(buttonPIN, Pin.IN, Pin.PULL_UP)

run_once = 0

### Menu Page ###
menu_page = 0

rtc.enable_periodic_update_interrupt(True)

### System ###

class system:

    ### WiFi ###
    def wifi_connect(self):
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
            
    ### MQTT ###   
    def mqtt_connect(self):
        """ Connect to the MQTT broker and subscribe to the topic"""
        global client_id, mqtt_broker
        
        print(client_id, mqtt_broker)
        client = MQTTClient(client_id, mqtt_broker, user=mqttusername, password=mqttpassword, keepalive=5000)
        client.connect()
        print('Connected to %s MQTT Broker'%(mqtt_broker))
        
        return client

    def restart_reconnect(self):
        global client
        print('Failed to connect to MQTT broker, Reconnecting...')
        sleep(10)
        client = mqtt_connect()
    
    ### Get button values ###
    def get_button1(self):
        return not button1.value()
    def get_button2(self):
        return not button2.value()
    def get_button3(self):
        return not button3.value()
    def get_button4(self):
        return not button4.value()
    def get_button5(self):
        return not button5.value()
    def get_button6(self):
        return not button6.value()
    
    ### Button Functions ###
    def button_press1(self):
        global menu_page
        menu_page += 1
        time.sleep(1)
    
    def button_press2(self):
        global menu_page
        menu_page -= 1
        time.sleep(1)
    
    def button_press3(self):
        client = system.mqtt_connect(self)
        client.publish(switch1, topic_msg)
        client.publish(switch2, topic_msg)
        print("sent",topic_msg,"to",switch1,"&",switch2)
        time.sleep(2)
    
    def button_press4(self):
        client = system.mqtt_connect(self)
        client.publish(switch3, topic_msg)
        print("sent",topic_msg,"to",switch3)
        time.sleep(2)
    
    def button_press5(self):
        client = system.mqtt_connect(self)
        client.publish(switch4, topic_msg)
        print("sent",topic_msg,"to",switch4)
        time.sleep(2)
    
    def button_press6(self):
        func.set_time(self)


##### Functions ####

class func:

    def set_time(self):
        NTP_QUERY = bytearray(48)
        NTP_QUERY[0] = 0x1B
        addr = socket.getaddrinfo(time_host, 123)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.settimeout(1)
            res = s.sendto(NTP_QUERY, addr)
            msg = s.recv(48)
        finally:
            s.close()
        val = struct.unpack("!I", msg[40:44])[0]
        t = val - NTP_DELTA    
        tm = time.gmtime(t)
        
        #machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3] - 1, tm[4], tm[5], 0))
        machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], 0))
        
        # this sets up the battery switching mode on your breakout
        rtc.setup()

        print(f"Getting time from Pico RTC/Thonny: {rtcpico.datetime()}")
        year, month, day, weekday, hour, minute, second, microsecond = rtcpico.datetime()

        print("Setting the breakout RTC!")
        rtc.set_time(second, minute, hour, weekday, day, month, year)

        print(f"New breakout time: {rtc.string_date()} {rtc.string_time()}")
    
    def showtemp(self):
        temperature, pressure, humidity = bme.read()
        temp = int(temperature)
        humi = int(humidity)
        
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.text(str(temp)+"°C", 75, 70, scale=6)
        display.text(str(humi)+"%", 80, 130, scale=6)
        
        ### Temp Icon ###
        display.circle(55, 100, 10)
        display.rectangle(50, 70, 10, 30)
        display.set_pen(RED)
        display.circle(55, 100, 7)
        display.rectangle(52, 80, 6, 20)
        
        ### Humidity Icon ###
        display.set_pen(RAIN)
        display.line(55, 130, 40, 150, 5)
        display.line(65, 140, 55, 153, 5)
        display.line(50, 160, 40, 174, 5)
        display.line(70, 155, 56, 175, 5)
        
        display.update()
        time.sleep(0.01)
        
    def showtime(self):
        rtc_date = rtc.string_date()
        rtc_time = rtc.string_time()
        hour = rtc_time[:-3]
        
        if rtc.read_periodic_update_interrupt_flag():
            rtc.clear_periodic_update_interrupt_flag()

            if rtc.update_time():
                display.set_pen(BLACK)
                display.clear()
                display.set_pen(WHITE)
                display.text((hour), 60, 80, scale=6)
                display.text((rtc_date), 25, 150, scale=4)
                display.update()
                time.sleep(0.01)
        
    def idle_time(self):
        time.sleep(1)
        get_time = rtc.string_time()#get time
        minute = get_time[3:5] #format hour
        minute = int(minute)
        idletime = minute + 5
        
        if rtc.read_periodic_update_interrupt_flag():
            rtc.clear_periodic_update_interrupt_flag()

            if rtc.update_time():
                return idletime

    def current_time_minutes(self):
        get_time = rtc.string_time()#get time
        minute = get_time[3:5] #format hour
        minute = int(minute)
        
        if rtc.read_periodic_update_interrupt_flag():
            rtc.clear_periodic_update_interrupt_flag()

            if rtc.update_time():
                return minute
    
    def current_time_full(self):
        rtc_date = rtc.string_date()
        rtc_time = rtc.string_time()
        hour = rtc_time[:-3]
        
        if rtc.read_periodic_update_interrupt_flag():
            rtc.clear_periodic_update_interrupt_flag()

            if rtc.update_time():
                return hour
            
    def weather(self):
        
        global run_once
        global temp_out
        global humidity_out
        global weather
        global cloud
        global rain1h
        global snow1h
        
        def get_weather():
            '''
            Get weather data from openweathermap.org
                city: City name, state code and country code divided by comma, Please, refer to ISO 3166 for the state codes or country codes. https://www.iso.org/obp/ui/#search
                api_key: Your unique API key (you can always find it on your openweather account page under the "API key" tab https://home.openweathermap.org/api_keys
                unit: Units of measurement. standard, metric and imperial units are available. If you do not use the units parameter, standard units will be applied by default. More: https://openweathermap.org/current#data
                lang: You can use this parameter to get the output in your language. More: https://openweathermap.org/current#multi
            '''
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={openweather_api_key}&units={units}&lang={lang}"
            print(url)
            res = urequests.post(url)
            return res.json()
        
        if run_once == 0:
            weather_data = get_weather()
            weather = weather_data["weather"][0]["main"]
            temp_raw = weather_data["main"]["temp"]
            temp_out = int(temp_raw)
            humidity_out = weather_data["main"]["humidity"]
            if "clouds" in weather_data:
                cloud = weather_data["clouds"]["all"]
                if "rain" in weather_data:
                    rain_raw = weather_data["rain"]["1h"]
                    rain1h = int(rain_raw)
                if "snow" in weather_data:
                    snow_raw = weather_data["snow"]["1h"]
                    snow1h = int(snow_raw)
            run_once = 1
        
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.text(str(temp_out)+"°C", 160, 70, scale=4)
        display.text(str(humidity_out)+"%", 165, 140, scale=4)

        ### Clouds ###
        if weather == "Clouds":
            display.set_pen(CLOUD)
            display.circle(30, 89, 15) #left
            display.circle(50, 80, 18) #middle
            display.circle(70, 92, 12) #right
            display.rectangle(30, 90, 40, 15)
            display.set_pen(WHITE)
            display.text(str(cloud)+"%", 20, 140, scale=4)
            
        ### Rain ###
        if weather == "Rain":
            display.set_pen(CLOUD)
            display.circle(30, 89, 15) #left
            display.circle(50, 80, 18) #middle
            display.circle(70, 92, 12) #right
            display.rectangle(30, 90, 40, 15)
            display.set_pen(RAIN)
            display.line(35, 105, 30, 115, 5)
            display.line(50, 105, 45, 115, 5)
            #display.line(70, 155, 56, 175, 5)
            display.line(65, 105, 60, 115, 5)
            display.text(str(rain1h)+"mm", 20, 140, scale=4)
            
        ### Clear ###
        if weather == "Clear":
            display.set_pen(SUN)
            display.circle(50, 89, 30)
            
        ### Snow ###
        if weather == "Snow":
            display.set_pen(Cloud)
            display.circle(30, 89, 15) #left
            display.circle(50, 80, 18) #middle
            display.circle(70, 92, 12) #right
            display.rectangle(30, 90, 40, 15)
            display.set_pen(WHITE)
            display.circle(35, 111, 5) #snow
            display.circle(50, 125, 5) #snow
            display.circle(65, 114, 5) #snow
            display.text(str(snow1h)+"mm", 20, 140, scale=4)
        
        ### Temp Icon ###
        display.set_pen(WHITE)
        display.circle(140, 95, 10)
        display.rectangle(135, 65, 10, 30)
        display.set_pen(RED)
        display.circle(140, 95, 7)
        display.rectangle(137, 75, 6, 20)
        
        ### Humidity Icon ###
        display.set_pen(RAIN)
        display.line(140, 130, 125, 150, 5)
        display.line(150, 140, 140, 153, 5)
        display.line(135, 160, 125, 174, 5)
        display.line(155, 155, 141, 175, 5)
        
        display.update()
        time.sleep(0.01)
    
    def network_dash(self):
        ping1 = uping.ping('192.168.0.1', quiet=True)
        ping2 = uping.ping('192.168.0.11', quiet=True)
        ping3 = uping.ping('192.168.0.13', quiet=True)
        
        ping_time1 = str(ping1[2])
        ping_time2 = str(ping2[2])
        ping_time3 = str(ping3[2])
        
        display.set_pen(BLACK)
        display.clear()

        ### Ping 1 ###
        display.set_pen(WHITE)
        display.text("RMO", 30, 40, scale=5)
        display.set_pen(GREEN)
        display.text((ping_time1+"ms"), 35, 80, scale=4)
            
        ### Ping 2 ###
        display.set_pen(WHITE)
        display.text("BMO", 140, 40, scale=5)
        display.set_pen(GREEN)
        display.text((ping_time2+"ms"), 145, 80, scale=4)
        
        ### Ping 3 ###
        display.set_pen(WHITE)
        display.text("HMO", 30, 140, scale=5)
        display.set_pen(GREEN)
        display.text((ping_time3+"ms"), 35, 180, scale=4)
        
        ### Ping 1 Down ###
        if ping1[1] == 0:
            
            display.set_pen(BLACK)
            display.clear()
            
            ### Ping 1 ###
            display.set_pen(WHITE)
            display.text("RMO", 30, 40, scale=5)
            display.set_pen(RED)
            display.text("DOWN", 30, 80, scale=4)
                
            ### Ping 2 ###
            display.set_pen(WHITE)
            display.text("BMO", 140, 40, scale=5)
            display.set_pen(GREEN)
            display.text((ping_time2+"ms"), 145, 80, scale=4)
            
            ### Ping 3 ###
            display.set_pen(WHITE)
            display.text("HMO", 30, 140, scale=5)
            display.set_pen(GREEN)
            display.text((ping_time3+"ms"), 35, 180, scale=4)
            
            display.update()
            time.sleep(0.01)
        
        ### Ping 2 Down ###
        if ping2[1] == 0:
            
            display.set_pen(BLACK)
            display.clear()
            
            ### Ping 1 ###
            display.set_pen(WHITE)
            display.text("RMO", 30, 40, scale=5)
            display.set_pen(GREEN)
            display.text((ping_time1+"ms"), 35, 80, scale=4)
                
            ### Ping 2 ###
            display.set_pen(WHITE)
            display.text("BMO", 140, 40, scale=5)
            display.set_pen(RED)
            display.text(("DOWN"), 140, 80, scale=4)
            
            ### Ping 3 ###
            display.set_pen(WHITE)
            display.text("HMO", 30, 140, scale=5)
            display.set_pen(GREEN)
            display.text((ping_time3+"ms"), 35, 180, scale=4)
            
            display.update()
            time.sleep(0.01)
        
        ### Ping 3 Down ###
        if ping3[1] == 0:
            
            display.set_pen(BLACK)
            display.clear()
            
            ### Ping 1 ###
            display.set_pen(WHITE)
            display.text("RMO", 30, 40, scale=5)
            display.set_pen(GREEN)
            display.text((ping_time1+"ms"), 35, 80, scale=4)
                
            ### Ping 2 ###
            display.set_pen(WHITE)
            display.text("BMO", 140, 40, scale=5)
            display.set_pen(GREEN)
            display.text((ping_time2+"ms"), 145, 80, scale=4)
            
            ### Ping 3 ###
            display.set_pen(WHITE)
            display.text("HMO", 30, 140, scale=5)
            display.set_pen(RED)
            display.text("DOWN", 30, 180, scale=4)
            
            display.update()
            time.sleep(0.01)

        ### Ping 1 and 2 Down ###
        if ping1[1] == 0 and ping2[1] == 0:
                        
            display.set_pen(BLACK)
            display.clear()
            
            ### Ping 1 ###
            display.set_pen(WHITE)
            display.text("RMO", 30, 40, scale=5)
            display.set_pen(RED)
            display.text(("DOWN"), 30, 80, scale=4)
                
            ### Ping 2 ###
            display.set_pen(WHITE)
            display.text("BMO", 140, 40, scale=5)
            display.set_pen(RED)
            display.text(("DOWN"), 140, 80, scale=4)
            
            ### Ping 3 ###
            display.set_pen(WHITE)
            display.text("HMO", 30, 140, scale=5)
            display.set_pen(GREEN)
            display.text((ping_time3+"ms"), 35, 180, scale=4)
            
            display.update()
            time.sleep(0.01)

        ### Ping 1 and 3 Down ###
        if ping1[1] == 0 and ping3[1] == 0:
                        
            display.set_pen(BLACK)
            display.clear()
            
            ### Ping 1 ###
            display.set_pen(WHITE)
            display.text("RMO", 30, 40, scale=5)
            display.set_pen(RED)
            display.text(("DOWN"), 30, 80, scale=4)
                
            ### Ping 2 ###
            display.set_pen(WHITE)
            display.text("BMO", 140, 40, scale=5)
            display.set_pen(GREEN)
            display.text((ping_time2+"ms"), 145, 80, scale=4)
            
            ### Ping 3 ###
            display.set_pen(WHITE)
            display.text("HMO", 30, 140, scale=5)
            display.set_pen(RED)
            display.text(("DOWN"), 30, 180, scale=4)
            
            display.update()
            time.sleep(0.01)

        ### Ping 2 and 3 Down ###
        if ping2[1] == 0 and ping3[1] == 0:
                        
            display.set_pen(BLACK)
            display.clear()
            
            ### Ping 1 ###
            display.set_pen(WHITE)
            display.text("RMO", 30, 40, scale=5)
            display.set_pen(GREEN)
            display.text((ping_time1+"ms"), 35, 80, scale=4)
                
            ### Ping 2 ###
            display.set_pen(WHITE)
            display.text("BMO", 140, 40, scale=5)
            display.set_pen(RED)
            display.text(("DOWN"), 140, 80, scale=4)
            
            ### Ping 3 ###
            display.set_pen(WHITE)
            display.text("HMO", 30, 140, scale=5)
            display.set_pen(RED)
            display.text(("DOWN"), 30, 180, scale=4)
            
            display.update()
            time.sleep(0.01)

        ### Ping 1, 2 and 3 Down ###
        if ping1[1] == 0 and ping2[1] == 0 and ping3[1] == 0 :
                                
            display.set_pen(BLACK)
            display.clear()
            
            ### Ping 1 ###
            display.set_pen(WHITE)
            display.text("RMO", 30, 40, scale=5)
            display.set_pen(RED)
            display.text(("DOWN"), 30, 80, scale=4)
                
            ### Ping 2 ###
            display.set_pen(WHITE)
            display.text("BMO", 140, 40, scale=5)
            display.set_pen(RED)
            display.text(("DOWN"), 140, 80, scale=4)
            
            ### Ping 3 ###
            display.set_pen(WHITE)
            display.text("HMO", 30, 140, scale=5)
            display.set_pen(RED)
            display.text(("DOWN"), 30, 180, scale=4)
            
            display.update()
            time.sleep(0.01)

        display.update()
        time.sleep(0.01)

    def reset_run_once(self):
        global run_once
        run_once = 0
    
    def routiner_sleep(self):
        print("Sleep")
        
    def routiner_wake(self):
        print("Wake")
     
##### Emotions #####

class emote:

    def happy(self):
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 50, 30, 40) #eye
        display.rectangle(180, 50, 30, 40) #eye
        display.line(90, 100, 150, 100, 10) #mouth
        display.line(150, 100, 160, 91, 9) #smile
        display.line(90, 100, 80, 91, 9) #smile
        display.update()
        
    def neutral(self):
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 50, 30, 40) #eye
        display.rectangle(180, 50, 30, 40) #eye
        display.line(90, 100, 150, 100, 10) #mouth
        display.update()

    def shocked(self):
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 50, 30, 40) #eye
        display.rectangle(180, 50, 30, 40) #eye
        display.circle(120, 100, 15) #mouth
        display.update()
        
    def neutralblink(self):
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 50, 30, 40) #eye
        display.rectangle(180, 50, 30, 40) #eye
        display.line(90, 100, 150, 100, 10) #mouth
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 60, 30, 30) #eye
        display.rectangle(180, 60, 30, 30) #eye
        display.line(90, 100, 150, 100, 10) #mouth
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 70, 30, 20) #eye
        display.rectangle(180, 70, 30, 20) #eye
        display.line(90, 100, 150, 100, 10) #mouth
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 80, 30, 10) #eye
        display.rectangle(180, 80, 30, 10) #eye
        display.line(90, 100, 150, 100, 10) #mouth
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 85, 30, 5) #eye
        display.rectangle(180, 85, 30, 5) #eye
        display.line(90, 100, 150, 100, 10) #mouth
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 80, 30, 10) #eye
        display.rectangle(180, 80, 30, 10) #eye
        display.line(90, 100, 150, 100, 10) #mouth
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 70, 30, 20) #eye
        display.rectangle(180, 70, 30, 20) #eye
        display.line(90, 100, 150, 100, 10) #mouth
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 60, 30, 30) #eye
        display.rectangle(180, 60, 30, 30) #eye
        display.line(90, 100, 150, 100, 10) #mouth
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 50, 30, 40) #eye
        display.rectangle(180, 50, 30, 40) #eye
        display.line(90, 100, 150, 100, 10) #mouth
        display.update()
        time.sleep(2)

    def shockedblink(self):
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 50, 30, 40) #eye
        display.rectangle(180, 50, 30, 40) #eye
        display.circle(120, 100, 15) #mouth
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 60, 30, 30) #eye
        display.rectangle(180, 60, 30, 30) #eye
        display.circle(120, 100, 15) #mouth
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 70, 30, 20) #eye
        display.rectangle(180, 70, 30, 20) #eye
        display.circle(120, 100, 15) #mouth
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 80, 30, 10) #eye
        display.rectangle(180, 80, 30, 10) #eye
        display.circle(120, 100, 15) #mouth
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 85, 30, 5) #eye
        display.rectangle(180, 85, 30, 5) #eye
        display.circle(120, 100, 15) #mouth
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 80, 30, 10) #eye
        display.rectangle(180, 80, 30, 10) #eye
        display.circle(120, 100, 15) #mouth
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 70, 30, 20) #eye
        display.rectangle(180, 70, 30, 20) #eye
        display.circle(120, 100, 15) #mouth
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 60, 30, 30) #eye
        display.rectangle(180, 60, 30, 30) #eye
        display.circle(120, 100, 15) #mouth
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 50, 30, 40) #eye
        display.rectangle(180, 50, 30, 40) #eye
        display.circle(120, 100, 15) #mouth
        display.update()
        time.sleep(2)
        
    def awakeblink(self):
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 85, 30, 5) #eye
        display.rectangle(180, 85, 30, 5) #eye
        display.circle(120, 100, 15) #mouth
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 80, 30, 10) #eye
        display.rectangle(180, 80, 30, 10) #eye
        display.circle(120, 100, 15) #mouth
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 70, 30, 20) #eye
        display.rectangle(180, 70, 30, 20) #eye
        display.circle(120, 100, 15) #mouth
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 60, 30, 30) #eye
        display.rectangle(180, 60, 30, 30) #eye
        display.circle(120, 100, 15) #mouth
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 50, 30, 40) #eye
        display.rectangle(180, 50, 30, 40) #eye
        display.circle(120, 100, 15) #mouth
        display.update()
        time.sleep(2)
        
        
    def happyblink(self):
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 50, 30, 40) #eye
        display.rectangle(180, 50, 30, 40) #eye
        display.line(90, 100, 150, 100, 10) #mouth
        display.line(150, 100, 160, 91, 9) #smile
        display.line(90, 100, 80, 91, 9) #smile
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 60, 30, 30) #eye
        display.rectangle(180, 60, 30, 30) #eye
        display.line(90, 100, 150, 100, 10) #mouth
        display.line(150, 100, 160, 91, 9) #smile
        display.line(90, 100, 80, 91, 9) #smile
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 70, 30, 20) #eye
        display.rectangle(180, 70, 30, 20) #eye
        display.line(90, 100, 150, 100, 10) #mouth
        display.line(150, 100, 160, 91, 9) #smile
        display.line(90, 100, 80, 91, 9) #smile
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 80, 30, 10) #eye
        display.rectangle(180, 80, 30, 10) #eye
        display.line(90, 100, 150, 100, 10) #mouth
        display.line(150, 100, 160, 91, 9) #smile
        display.line(90, 100, 80, 91, 9) #smile
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 85, 30, 5) #eye
        display.rectangle(180, 85, 30, 5) #eye
        display.line(90, 100, 150, 100, 10) #mouth
        display.line(150, 100, 160, 91, 9) #smile
        display.line(90, 100, 80, 91, 9) #smile
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 80, 30, 10) #eye
        display.rectangle(180, 80, 30, 10) #eye
        display.line(90, 100, 150, 100, 10) #mouth
        display.line(150, 100, 160, 91, 9) #smile
        display.line(90, 100, 80, 91, 9) #smile
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 70, 30, 20) #eye
        display.rectangle(180, 70, 30, 20) #eye
        display.line(90, 100, 150, 100, 10) #mouth
        display.line(150, 100, 160, 91, 9) #smile
        display.line(90, 100, 80, 91, 9) #smile
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 60, 30, 30) #eye
        display.rectangle(180, 60, 30, 30) #eye
        display.line(90, 100, 150, 100, 10) #mouth
        display.line(150, 100, 160, 91, 9) #smile
        display.line(90, 100, 80, 91, 9) #smile
        display.update()
        time.sleep(0.01)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 50, 30, 40) #eye
        display.rectangle(180, 50, 30, 40) #eye
        display.line(90, 100, 150, 100, 10) #mouth
        display.line(150, 100, 160, 91, 9) #smile
        display.line(90, 100, 80, 91, 9) #smile
        display.update()
        time.sleep(2)
        
    def snooze1(self):
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 85, 30, 5) #eye
        display.rectangle(180, 85, 30, 5) #eye
        display.circle(120, 100, 15) #mouth
        display.text("Z", 140, 40, scale=3)
        display.text("Z", 170, 20, scale=3)
        display.update()

    def snooze2(self):
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.rectangle(30, 85, 30, 5) #eye
        display.rectangle(180, 85, 30, 5) #eye
        display.circle(120, 100, 10) #mouth
        display.text("Z", 140, 40, scale=4)
        display.text("Z", 170, 20, scale=4)
        display.update()
        
    def debug(self):
        self.neutral()
        self.neutralblink()
        self.happy()
        self.happyblink()
        self.shocked()
        self.shockedblink()

