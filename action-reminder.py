#!/usr/bin/env python2
from hermes_python.hermes import Hermes
#from datetime import datetime
#from pytz import timezone

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

def intent_received(hermes, intent_message):
	reminder_msg = ""
	#now = datetime.now(timezone('Europe/Paris'))

	try:
		raise ValueError('invalid user response')
	except:
		reminder_msg = "Bouffe moi le cul."

	hermes.publish_end_session(intent_message.session_id, reminder_msg)

with Hermes(MQTT_ADDR) as h:
	h.subscribe_intents(intent_received).start()
