import time
import ntptime
import urequests
from secret import openweather_api_key, city, lang, units
from pimoroni_i2c import PimoroniI2C
from picographics import PicoGraphics, DISPLAY_LCD_240X240, PEN_P8
from breakout_bme280 import BreakoutBME280
from breakout_msa301 import BreakoutMSA301

PINS_BREAKOUT_GARDEN = {"sda": 4, "scl": 5}

i2c = PimoroniI2C(**PINS_BREAKOUT_GARDEN)
bme = BreakoutBME280(i2c)
msa = BreakoutMSA301(i2c)
display = PicoGraphics(display=DISPLAY_LCD_240X240, pen_type=PEN_P8)
display.set_backlight(1.0)
display.set_font("bitmap8")
WIDTH, HEIGHT = display.get_bounds()

RED   = display.create_pen(255, 000, 000)    #Define some colors to use (R,G,B)
GREEN = display.create_pen(000, 255, 000)
BLUE  = display.create_pen(000, 000, 255)
WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
RAIN  = display.create_pen(56, 194, 231)
Cloud = display.create_pen(157, 165, 167)

run_once = 0

##### Functions ####

class func:
    
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
        timestamp=time.localtime() #get time
        hour="%02d:%02d"%(timestamp[3:5]) #format hour
        date="%04d-%02d-%02d"%(timestamp[0:3]) # format date
        year=(date[0:4]) #split year into own object
        month=(date[5:7]) #split month into own object
        day=(date[8:10]) #split date into own object
            
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.text((hour), 60, 80, scale=6)
        display.text((day + "-" + month +"-"+ year), 30, 150, scale=4) # assemble date in normal format
        display.update()
        time.sleep(0.01)
        
    def idle_time(self):
        get_time = time.localtime() #get time
        minute = "%02d"%(get_time[4:5])
        idletime = int(minute)
        idletime = idletime + 1 #5
        return idletime

    def current_time(self):
        get_time = time.localtime() #get time
        minute = "%02d"%(get_time[4:5]) #format hour
        minute = int(minute)
        return minute
            
    def weather_test(self):
        
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
            elif "rain" in weather_data:
                rain1h = weather_data["rain"]["1h"]
            elif "snow" in weather_data:
                snow1h = weather_data["snow"]["1h"]
            run_once = 1
        
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        display.text(str(temp_out)+"°C", 160, 70, scale=4)
        display.text(str(humidity_out)+"%", 165, 140, scale=4)

        ### Clouds ###
        if weather == "Clouds":
            display.set_pen(Cloud)
            display.circle(30, 89, 15) #left
            display.circle(50, 80, 18) #middle
            display.circle(70, 92, 12) #right
            display.rectangle(30, 90, 40, 15)
            display.set_pen(WHITE)
            display.text(str(cloud)+"%", 20, 140, scale=4)
            
        ### Rain ###
        if weather == "Rain":
            display.set_pen(Cloud)
            display.circle(30, 89, 15) #left
            display.circle(50, 80, 18) #middle
            display.circle(70, 92, 12) #right
            display.rectangle(30, 90, 40, 15)
            display.set_pen(RAIN)
            display.line(35, 105, 30, 115, 5)
            display.line(50, 105, 45, 115, 5)
            #display.line(70, 155, 56, 175, 5)
            display.line(65, 105, 60, 115, 5)
            
        #Clear
        #Snow

        
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
        
    def reset_run_once(self):
        global run_once
        run_once = 0
     
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