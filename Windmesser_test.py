from m5stack import *
from m5ui import *
from uiflow import *
import time
import unit


setScreenColor(0x111111)
env3_0 = unit.get(unit.ENV3, unit.PORTA)
adc_0 = unit.get(unit.ADC, unit.PORTA)




wind_max = 0
wind_min = 100




while True:
    wind = adc_0.voltage *25
    if wind > wind_max:
        wind_max = wind
    elif wind < wind_min:
        wind_min = wind
    lcd.clear()
    lcd.print("%.1f m/s"%float((wind)), 5, 5, 0xffffff)
    lcd.print("%.1f m/s"%float((wind_max)), 5, 25, 0xffffff)
    lcd.print("%.1f m/s"%float((wind_min)), 5, 45, 0xffffff)
    wait_ms(1000)