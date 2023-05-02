

# MODUL_NAME = 'markiese_steuerung.py'
# MODUL_VERSION = '0.0.1'

# Timer zur Positionsbestimmung muss eingefuehrt werden.
# Mit  utime.ticks_ms() realisieren.
# Testen wann ein Überlauf erfolgt und diesen verarbeiten.




import machine
import utime




# Relais Ansteuerung initialisieren
relais_1 = 22
relais_2 = 19
relais_3 = 25
pin0 = machine.Pin(relais_1, mode=machine.Pin.OUT, pull=0x00)
pin1 = machine.Pin(relais_2, mode=machine.Pin.OUT, pull=0x00)
pin2 = machine.Pin(relais_3, mode=machine.Pin.OUT, pull=0x00)

# Prüfen ob Testumgebung oder Produktivumgebung
try:
    from markiese_main_test import DEBUG, SIM_MODE
#    print("Produktivumgebung")
except:
    from markiese_main import DEBUG, SIM_MODE
#    print("Testumgebung")

# Für debug 9 -> Hardwaresimulation
from markiese_main import DEBUG
if DEBUG & SIM_MODE > 0:
    REL_ON = 0
    REL_OFF = 1
else:
    REL_ON = 1
    REL_OFF = 0

relais_delay = 30  # Verzögerung der Relaisachaltung in ms
motor = True       # True = Motor ist eingeschaltet.
markiese_fahrzeit = 30000  # Zeit zum Ein- / Ausfahren der Markiese
markiese_status = 0
positions_schritt = markiese_fahrzeit / 100
markiese_start_time = 0
markiese_stop_time = 0



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

