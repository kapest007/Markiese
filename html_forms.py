
file = 'html_forms.py'
version = '00.00.001'
date = '04.05.2023'
author = 'Peter Stöck & Jean-Christophe Bos'

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

firstname = ''

####################################
# Wlan einrichten und verbinden:
####################################

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# wlan.ifconfig((dev_config['fixIP'], '255.255.255.0', '192.168.5.1', '192.168.5.1'))
wlan.connect(SSID, PW)

while not wlan.isconnected():
    time.sleep(1)
else:
    print(wlan.ifconfig()[0])

time.sleep(1)




# ----------------------------------------------------------------------------

@mws.MicroWebSrv.route('/test')
def _httpHandlerTestGet(httpClient, httpResponse) :
	content = """\
	<!DOCTYPE html>
	<html lang=en>
        <head>
        	<meta charset="UTF-8" />
            <title>TEST GET</title>
        </head>
        <body>
            <h1>TEST GET</h1>
            Client IP address = %s
            <br />
			<form action="/test" method="post" accept-charset="ISO-8859-1">
				First name: <input type="text" name="firstname"><br />
				Last name: <input type="text" name="lastname"><br />
				<input type="submit" value="Submit">
			</form>
        </body>
    </html>
	""" % httpClient.GetIPAddr()
	httpResponse.WriteResponseOk( headers		 = None,
								  contentType	 = "text/html",
								  contentCharset = "UTF-8",
								  content 		 = content )


@mws.MicroWebSrv.route('/test', 'POST')
def _httpHandlerTestPost(httpClient, httpResponse) :
	formData  = httpClient.ReadRequestPostedFormData()
	firstname = formData["firstname"]
	lastname  = formData["lastname"]
	content   = """\
	<!DOCTYPE html>
	<html lang=en>
		<head>
			<meta charset="UTF-8" />
            <title>TEST POST</title>
        </head>
        <body>
            <h1>TEST POST</h1>
            Firstname = %s<br />
            Lastname = %s<br />
        </body>
    </html>
	""" % ( mws.MicroWebSrv.HTMLEscape(firstname),
		    mws.MicroWebSrv.HTMLEscape(lastname) )
	httpResponse.WriteResponseOk( headers		 = None,
								  contentType	 = "text/html",
								  contentCharset = "UTF-8",
								  content 		 = content )


@mws.MicroWebSrv.route('/edit/<index>')             # <IP>/edit/123           ->   args['index']=123
@mws.MicroWebSrv.route('/edit/<index>/abc/<foo>')   # <IP>/edit/123/abc/bar   ->   args['index']=123  args['foo']='bar'
@mws.MicroWebSrv.route('/edit')                     # <IP>/edit               ->   args={}
def _httpHandlerEditWithArgs(httpClient, httpResponse, args={}) :
	content = """\
	<!DOCTYPE html>
	<html lang=en>
        <head>
        	<meta charset="UTF-8" />
            <title>TEST EDIT</title>
        </head>
        <body>
	"""
	content += "<h1>EDIT item with {} variable arguments</h1>"\
		.format(len(args))
	
	if 'index' in args :
		content += "<p>index = {}</p>".format(args['index'])
	
	if 'foo' in args :
		content += "<p>foo = {}</p>".format(args['foo'])
	
	content += """
        </body>
    </html>
	"""
	httpResponse.WriteResponseOk( headers		 = None,
								  contentType	 = "text/html",
								  contentCharset = "UTF-8",
								  content 		 = content )

# ----------------------------------------------------------------------------

# def _acceptWebSocketCallback(webSocket, httpClient) :
# 	print("WS ACCEPT")
# 	webSocket.RecvTextCallback   = _recvTextCallback
# 	webSocket.RecvBinaryCallback = _recvBinaryCallback
# 	webSocket.ClosedCallback 	 = _closedCallback
# 
# def _recvTextCallback(webSocket, msg) :
# 	print("WS RECV TEXT : %s" % msg)
# 	webSocket.SendText("Reply for %s" % msg)
# 
# def _recvBinaryCallback(webSocket, data) :
# 	print("WS RECV DATA : %s" % data)
# 
# def _closedCallback(webSocket) :
# 	print("WS CLOSED")
# 
# ----------------------------------------------------------------------------

####################################
# Grafische Oberfläche gestalten
####################################

label_name = M5TextBox(2, 0, file, lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label_version = M5TextBox(2, 20, 'Version ' + version, lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label_ipadress = M5TextBox(2, 40, 'IP ' + wlan.ifconfig()[0], lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label_data = M5TextBox(2, 60, firstname, lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
# label_feuchte = M5TextBox(130, 60, ' ' + wlan.ifconfig()[0], lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
# label_aussen_temperatur = M5TextBox(40, 90, "label0", lcd.FONT_DejaVu40, 0xFFFFFF, rotate=0)

lcd.setRotation(1)
setScreenColor(0x111111)
lcd.clear()
label_name.show()
label_version.show()
label_ipadress.show()


#routeHandlers = [
#	( "/test",	"GET",	_httpHandlerTestGet ),
#	( "/test",	"POST",	_httpHandlerTestPost )
#]

srv = mws.MicroWebSrv(webPath='www/')
# srv.MaxWebSocketRecvLen     = 256
# # srv.WebSocketThreaded		= False
# srv.AcceptWebSocketCallback = _acceptWebSocketCallback
srv.Start(threaded=True)

print('Server gestartet')

# ----------------------------------------------------------------------------
