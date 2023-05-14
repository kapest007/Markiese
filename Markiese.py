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

# Versionen < 00.01. laufen auf M5Stick C Plus.
# Sie sind reine Testversionen mit Print-Ausgaben.
#
# V 00.00.007: TP/m0 wurde implementiert. Temeraturanzeige ist rot
# wenn die Markiese in Bewegung ist, sonst grün.
# Der timer_markiese wude eingeführt.
#
# V.00.00.006:
# Markiesen Funktionen überarbeitet.
#
# V.00.00.005:
# Funktionen für den Webserver implementiert:
# Wetterdaten werden auf Webseite ausgeben (IP/wetter).
# Gerät wird neugestartet (IP/restart).
#
# V.00.00.004:
# www eingerichtet und index.htm geschrieben.
#
# V.00.00.003:
# wird im Branch "websrv" bearbeitet.
# Es wird ein Webserver installiert.
# Funktioniert grundsätzlich.
# www und index.htm fehlen noch.
#
# V.00.00.002:
# Diese Version befasst sich nur mit den Umweltdaten.
# Diese werden ermittelt und angezeigt.
# Temperatur mit 1 Nachkommastelle,
# Druck und Feuchte ohne Nachkommastelle.


# Timer zur Positionsbestimmung muss eingefuehrt werden.
# Mit  utime.ticks_ms() realisieren.
# Testen wann ein Überlauf erfolgt und diesen verarbeiten.

file = 'Markiese.py'
version = '00.00.007'
date = '14.05.2023'
author = 'Peter Stöck'

'''
Befehle:
IP/   - Sys Meldung und Anleitung
IP/m0  - Markiese ganz einfahren
IP/m1 - Markiese ganz ausfahren
IP/m/0...100   - Markiese auf Position fahren
IP/m  - Markiese und Wetterseite abrufen
IP/set/x - Wert einstellen
IP/cal/<Messwert>/<Wert>  - Messwerte Kalibrieren
IP/man/<Mode> - Webseite zum Manipulieren des Systems aufrufen
IP/restart - Gerät neu starten
IP/wetter - Seite mit den Wetterdaten aufrufen
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

import json






######################################
# Relais Ansteuerung initialisieren
######################################

relais_1 = 22
relais_2 = 19
relais_3 = 25
pin0 = machine.Pin(relais_1, mode=machine.Pin.OUT, pull=0x00)
pin1 = machine.Pin(relais_2, mode=machine.Pin.OUT, pull=0x00)
pin2 = machine.Pin(relais_3, mode=machine.Pin.OUT, pull=0x00)

##############################
# Varialblen initialisieren
##############################

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

relais_delay = 30  # Verzögerung der Relaisachaltung in ms
motor = True       # True = Motor ist eingeschaltet.
markiese_fahrzeit = 30000  # Zeit zum Ein- / Ausfahren der Markiese
markiese_status = 0
positions_schritt = markiese_fahrzeit / 100
markiese_start_time = 0
markiese_stop_time = 0



##############################
# Einstellungen für Testboard
##############################

# Für Produktiven Einsatz Entkommentieren: 
# REL_ON = 1
# REL_OFF = 0

# Für Testbetrie1b mit Testboard auskommentieren:
REL_ON = 0
REL_OFF = 1



markiese_steht = 0x00FF00
markiese_bewegt = 0xFF0000
markiesen_farbe = markiese_steht

##########################################
# Geräte Definitionen laden.
##########################################
  
try:
    f = open('dev_config.json','r')
    dc = f.read()
    f.close()
    dev_config = json.loads(dc)
except:
#     write_log('dev_config.json konnte nicht geholt werden!')
#     abbruch = True
    print('Kann dev_config.json nicht öffnen.')
    
    
####################################
# Wlan einrichten und verbinden:
####################################

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

wlan.ifconfig((dev_config['fixIP'], '255.255.255.0', '192.168.5.1', '192.168.5.1'))
wlan.connect(SSID, PW)

while not wlan.isconnected():
    time.sleep(1)
else:
    print(wlan.ifconfig()[0])



time.sleep(1)






######################################
# Funktionen zum Steuern der Markiese
######################################

'''
Prinzip der Markiesensteuerung:
Wenn die Markiese in Bewegung gesetzt wird, wird der timer_markiese gestartet.
Wenn der Timer abgelaufen ist wird die Markiese gestoppt.
Die Laufzeit des Timers bestimmt wie weit die Markiese aus- oder eingefahren wird.


'''

@timerSch.event('timer_markiese')
def ttimer_markiese():
  # global params
  markiese_stop()

# Markiese anhalten
def markiese_stop():
    global pin0, pin1, pin2, REL_OFF, relais_delay, markiesen_farbe, markiese_steht
    pin2.value(REL_OFF)
    utime.sleep_ms(relais_delay)
    pin0.value(REL_OFF)
    pin1.value(REL_OFF)
    markiesen_farbe = markiese_steht

# Markiese ausfahren - 
def markiese_ausfahren():
    global pin0, pin1, pin2, REL_ON, relais_delay, markiesen_farbe, markiese_bewegt
    pin0.value(REL_ON)
    utime.sleep_ms(relais_delay)
    pin2.value(REL_ON)
    markiesen_farbe = markiese_bewegt
  
  
# Markiese einfahren - 
def markiese_einfahren():
    global pin0, pin1, pin2, REL_ON, relais_delay, markiesen_farbe, markiese_bewegt
    pin1.value(REL_ON)
    utime.sleep_ms(relais_delay)
    pin2.value(REL_ON)
    markiesen_farbe = markiese_bewegt
    

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

################################
# ENVII Modul anmelden
################################

env2_0 = unit.get(unit.ENV2, unit.PORTA)




####################################
# Grafische Oberfläche gestalten
####################################

label_name = M5TextBox(2, 0, file, lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label_version = M5TextBox(2, 20, 'Version ' + version, lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label_ipadress = M5TextBox(2, 40, 'IP ' + wlan.ifconfig()[0], lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label_druck = M5TextBox(2, 60, ' ' + wlan.ifconfig()[0], lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label_feuchte = M5TextBox(130, 60, ' ' + wlan.ifconfig()[0], lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label_aussen_temperatur = M5TextBox(40, 90, "label0", lcd.FONT_DejaVu40, markiesen_farbe, rotate=0)

lcd.setRotation(3)
setScreenColor(0x111111)
lcd.clear()
label_name.show()
label_version.show()
label_ipadress.show()

#####################################
# Webserver einrichten und starten
#####################################

#################################
# Text der Index-Seite erstellen
#################################
index_text =  '''
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>Markiese</title>
    </head>
    <body>
        <h1>Markiese Info</h1>        
        <h3>Softwareversion: {}
            </br>
            IP-Adresse: {}</h3>
        </br>
        <h2>Benutzung:</h2>
            IP/   - Sys Meldung und Anleitung</br>
            IP/m0  - Markiese ganz einfahren</br>
            IP/m1 - Markiese ganz ausfahren</br>
            IP/m/0...100   - Markiese auf Position fahren</br>
            IP/m  - Markiese und Wetterseite abrufen</br>
            IP/set/x - Wert einstellen</br>
            IP/cal/<Messwert>/<Wert>  - Messwerte Kalibrieren</br>
            IP/man/<Mode> - Webseite zum Manipulieren des Systems aufrufen</br>
            IP/restart - Gerät neu starten</br>
            IP/wetter - Seite mit den Wetterdaten abrufen
    </body>
</html>

'''.format(version, wlan.ifconfig()[0])

# Index-Seite erstellen
try:
    f = open('./www/index.htm', 'w')
    f.write(index_text)
    f.close()
except:
    print('Kann index.htm nicht speichern.')

del(index_text)
gc.collect()



#--------------------------------------------------------------------
@mws.MicroWebSrv.route('/m0')
def _httpHandler_markiese_einfahren(httpClient, httpResponse):
    global label2, label3 # ist erforderlich
    markiese_einfahren()
    timerSch.run('timer_markiese', markiese_fahrzeit, 0x01)
    httpResponse.WriteResponseOk( headers = None,
                                  contentType = "text/html",
                                  contentCharset = "UTF-8",
                                  content = "Markiese wird eingefahren")    
    

#--------------------------------------------------------------------
@mws.MicroWebSrv.route('/wetter')
def _httpHandlerTestGet(httpClient, httpResponse):
    global label2, label3 # ist erforderlich
    content = """\
    <!DOCTYPE html>
    <html lang=de>
        <head>
            <meta charset="UTF-8" />
            <title>Test-Testseite</title>
        </head>
        <body>
            <h1>Wetterdaten vom Balkon</h1>
            <h2>Temperatur: {}</h2>
            <h2>Luftdruck: {}</h2>
            <h2>Luftfeuchte: {}</h2>
        </body>
    </html>
    """ .format(aussen_temp, aussen_druck, aussen_feuchte)
    httpResponse.WriteResponseOk( headers = None,
                                  contentType = "text/html",
                                  contentCharset = "UTF-8",
                                  content = content)

#--------------------------------------------------------------------
@mws.MicroWebSrv.route('/restart')
def _httpHandlerTestGet(httpClient, httpResponse):
    global label2, label3 # ist erforderlich
    content = """\
    <!DOCTYPE html>
    <html lang=de>
        <head>
            <meta charset="UTF-8" />
            <title>Restart</title>
        </head>
        <body>
            <h1>Gerät wird neu gestartet</h1>
        </body>
    </html>
    """
    httpResponse.WriteResponseOk( headers = None,
                                  contentType = "text/html",
                                  contentCharset = "UTF-8",
                                  content = content)
    time.sleep(1)
    machine.reset()
    
#--------------------------------------------------------------------    

srv = mws.MicroWebSrv()
srv.Start(threaded=True)

########################################################
# Ausgabeschleife nur zum Testen auf M5Stick C Plus
########################################################

while True:
    aussen_temp = env2_0.temperature
    aussen_druck = env2_0.pressure
    aussen_feuchte = env2_0.humidity
    label_aussen_temperatur.setText("%.1f"%float((aussen_temp)))
    label_druck.setText("%.0f"%float((aussen_druck)))
    label_feuchte.setText("%.0f"%float((aussen_feuchte)))
    label_aussen_temperatur.setColor(markiesen_farbe)
    label_aussen_temperatur.show()
    label_druck.show()
    label_feuchte.show()
    time.sleep(1)


