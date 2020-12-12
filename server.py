from bottle import *
import bottle
import RPi.GPIO as GPIO

LAMP = {
    "GPIO": {
        "BUTTON": 4,
        "RELAY": 3,
        "LED": 17
    },
    "STATE": False
}

DEVICE = {
    "LAMP": LAMP
}

def button_pressed(channel):
    for DEV in DEVICE:
        if DEVICE[DEV]["GPIO"]["BUTTON"] == channel:
            toggle_relay(DEV)

def toggle_relay(key):
	if DEVICE[key]["STATE"]:
		GPIO.output(DEVICE[key]["GPIO"]["LED"], GPIO.LOW)
		GPIO.output(DEVICE[key]["GPIO"]["RELAY"], GPIO.HIGH)
	else:
		GPIO.output(DEVICE[key]["GPIO"]["LED"], GPIO.HIGH)
		GPIO.output(DEVICE[key]["GPIO"]["RELAY"], GPIO.LOW)
	DEVICE[key]["STATE"] = not DEVICE[key]["STATE"]

@bottle.hook('after_request')
def enable_cors_after_request_hook():
    bottle.response.headers['Access-Control-Allow-Origin'] = '*'
    bottle.response.headers['Access-Control-Allow-Methods'] = \
        'GET, POST, PUT, OPTIONS'
    bottle.response.headers['Access-Control-Allow-Headers'] = \
        'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

@get('/')
def serve_json():
    return {
        "msg": "Error: use /togglerelay or /getrelay", 
        "error": 1
        }

@get('/togglerelay')
def serve_json():
    dev = request.query['relay'].decode()
    if dev in DEVICE:
        toggle_relay(dev)
        return {
            "msg": "Relay " + request.query['relay'] + " will turn " + ( "on" if DEVICE[dev]["STATE"] else "off" ), 
            "error": 0
            }
    else:
        return {
            "msg": "Relay not found!",
            "error:": 1
        }

@get('/getrelay')
def serve_json():
    dev = request.query['relay'].decode()
    if dev in DEVICE:
        return {
            "msg": "Relay is " + ( "on" if DEVICE[dev]["STATE"] else "off" ),
            "state": DEVICE[dev]["STATE"],
            "error": 0
            }
    else:
        return {
            "msg": "Relay not found!",
            "error:": 1
        }

if __name__ == "__main__":
	GPIO.setmode(GPIO.BCM)
	for dev in DEVICE.values():
		GPIO.setup(dev["GPIO"]["LED"], GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup(dev["GPIO"]["RELAY"], GPIO.OUT, initial=GPIO.HIGH)
		GPIO.setup(dev["GPIO"]["BUTTON"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.add_event_detect(dev["GPIO"]["BUTTON"], GPIO.FALLING, callback=button_pressed, bouncetime=500)
	
	run(host='0.0.0.0', port=8080)
	GPIO.cleanup()
