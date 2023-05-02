# Markiese.py
#
# Dient zur Steuerung der Markiese und
# erfasst die Umweltdaten auf dem Balkon.
#

# Versionen:
#
# Versionen >= 00.01. laufen auf M5ATOM Lite.
# Sie haben einen Webserver über den mit Ihm
# kommuniziert werden kann.
#
#
#
# Versionen < 00.01. laufen auf M5Stick C Plus.
# Sie sind reine Testversionen mit Print-Ausgaben.
#
# V.00.00.02:
# Diese Version befasst sich nur mit den Umweltdaten.
# Diese werden ermittelt und angezeigt.
# Temperatur mit 1 Nachkommastelle,
# Druck und Feuchte ohne Nachkommastelle.


# Timer zur Positionsbestimmung muss eingefuehrt werden.
# Mit  utime.ticks_ms() realisieren.
# Testen wann ein Überlauf erfolgt und diesen verarbeiten.

file = 'Markiese.py'
version = '00.00.002'
date = '02.05.2023'
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
import utime

import network
import MicroWebSrv.microWebSrv as mws
from wlansecrets import SSID, PW







# Relais Ansteuerung initialisieren
relais_1 = 22
relais_2 = 19
relais_3 = 25
pin0 = machine.Pin(relais_1, mode=machine.Pin.OUT, pull=0x00)
pin1 = machine.Pin(relais_2, mode=machine.Pin.OUT, pull=0x00)
pin2 = machine.Pin(relais_3, mode=machine.Pin.OUT, pull=0x00)

# Varialblen initialisieren

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
markiese_stop_zeit = None
aussen_temp = None




# Varialblen initialisieren

relais_delay = 30  # Verzögerung der Relaisachaltung in ms
motor = True       # True = Motor ist eingeschaltet.
markiese_fahrzeit = 30000  # Zeit zum Ein- / Ausfahren der Markiese
markiese_status = 0
positions_schritt = markiese_fahrzeit / 100
markiese_start_time = 0
markiese_stop_time = 0

# Für Produktiven Einsatz Entkommentieren: 
# REL_ON = 1
# REL_OFF = 0

# Für Testbetrieb mit Testboard auskommentieren:
REL_ON = 0
REL_OFF = 1



# Markiese anhalten - gibt Verfahrzeit in ticks_ms und Motorflag = 0 zurück
def markiese_stop(start, motor):
    global pin0, pin1, pin2, REL_OFF, RELAIS_VERZ
    pin2.value(REL_OFF)
    utime.sleep_ms(RELAIS_VERZ)
    pin0.value(REL_OFF)
    pin1.value(REL_OFF)
    stop = utime.ticks_ms()
    return utime.ticks_diff(start, stop) * motor, 0  

# Markiese ausfahren - gibt Startzeit in ticks_ms und Motorflag = 1 zurück
def markiese_ausfahren():
    global pin0, pin1, pin2, REL_ON, RELAIS_VERZ
    pin0.value(REL_ON)
    utime.sleep_ms(RELAIS_VERZ)
    pin2.value(REL_ON)
    return utime.ticks_ms(), 1
  
  
# Markiese einfahren - gibt Startzeit in ticks_ms und Motorflag = -1 zurück
def markiese_einfahren():
    global pin0, pin1, pin2, REL_ON, RELAIS_VERZ
    pin1.value(REL_ON)
    utime.sleep_ms(RELAIS_VERZ)
    pin2.value(REL_ON)
    return utime.ticks_ms(), -1

# Markiese auf Position fahren
# - Eingabe in % markiese_status
# - Ausgabe in % markiese_status
def markiese_position(ziel, aktuell):
    weg = ziel - aktuell
    if weg < 1:
        richtung = 0
    else:
        richtung = 1
    dauer = abs(weg) * positions_schritt
    if richtung == 0:
        start_time, motor = markiese_einfahren()
    else:
        start_time, motor = markiese_ausfahren()
    utime.sleep_ms(dauer)
    weg_zeit, motor = markiese_stop(start_time, motor)
    return ziel

# Markiesen Aus- und Einfahrzeiten ermitteln
def markiese_kalibrieren():
    pass


# ENVII Modul anmelden

env2_0 = unit.get(unit.ENV2, unit.PORTA)

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
label_version = M5TextBox(2, 20, 'Version ' + version, lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label_ipadress = M5TextBox(2, 40, 'IP ' + wlan.ifconfig()[0], lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label_druck = M5TextBox(2, 60, ' ' + wlan.ifconfig()[0], lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label_feuchte = M5TextBox(130, 60, ' ' + wlan.ifconfig()[0], lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label_aussen_temperatur = M5TextBox(40, 90, "label0", lcd.FONT_DejaVu40, 0xFFFFFF, rotate=0)

lcd.setRotation(3)
setScreenColor(0x111111)
lcd.clear()
label_name.show()
label_version.show()
label_ipadress.show()



while True:
    aussen_temp = env2_0.temperature
    aussen_druck = env2_0.pressure
    aussen_feuchte = env2_0.humidity
    label_aussen_temperatur.setText("%.1f"%float((aussen_temp)))
    label_druck.setText("%.0f"%float((aussen_druck)))
    label_feuchte.setText("%.0f"%float((aussen_feuchte)))
    label_aussen_temperatur.show()
    label_druck.show()
    label_feuchte.show()
    time.sleep(1)


