# Home_Markiese
# Programm für die Sensorstation an der Markiese.
# Es misst die Aussentemperatur und Steuert die Markiese.

# Version 00.00.003
# Grundfunktion Temperaturmesseung ist OK
# Hübschere Ausgabe gestaltet.
# MicroWebSrv integrieren.

file = 'Home_Markiese_V_00_00_003.py'
version = '00.00.003'
date = '08.04.2023'
author = 'Peter Stöck'

'''
Befehle:
Mar_Ein   - Markiese einfahren
Mar_Aus  - Markiese ausfahren
Mar_Stop - Markiese Stop
Mar_Ver   - Softwareversion
Mar_Dbg  - Debug-Modue einstellen
Mar_Std   - Standard-Modus einstellen
Mar_Res  - System neu starten
'''

'''
Daten für das ATOM HUB AC/DC
Remote Control Switch Kit
Relais_1 = 22
Relais_2 = 19
RX          = 33
TX           = 23
SDA        = 25
SCL        = 21
'''

from m5stack import *
from m5ui import *
from uiflow import *
import machine
import time
import unit

import network
import MicroWebSrv.microWebSrv as mws
from wlansecrets import SSID, PW

env2_0 = unit.get(unit.ENV2, unit.PORTA)

command = None
its_weather_time = None
lfd_nr = None
command_received = None
wetter = None
lfd_nr_max = None
wetter_takt = None
makiese_aktiv = None
status = None
message = None
relais_1 = None
markiese_stop_zeit = None
relais_2 = None
relais_3 = None
aussen_temp = None

####################################
# Wlan einrichten und verbinden:
####################################

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

wlan.connect(SSID, PW)

while not wlan.isconnected():
    time.sleep(1)
else:
    lcd.setRotation(3)
    print(wlan.ifconfig()[0])

time.sleep(1)

# Grafische Oberfläche gestalten

label_name = M5TextBox(2, 0, file, lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label_version = M5TextBox(2, 40, 'Version ' + version, lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label_ipadress = M5TextBox(2, 60, 'IP ' + wlan.ifconfig()[0], lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label_aussen_temperatur = M5TextBox(40, 90, "label0", lcd.FONT_DejaVu40, 0xFFFFFF, rotate=0)

lcd.setRotation(3)
setScreenColor(0x111111)
lcd.clear()
label_name.show()
label_version.show()
label_ipadress.show()

while True:
    aussen_temp = env2_0.temperature
    label_aussen_temperatur.setText(str(aussen_temp))
    label_aussen_temperatur.show()
    time.sleep(1)

