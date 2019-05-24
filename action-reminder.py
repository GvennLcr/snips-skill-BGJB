#!/usr/bin/env python3
from hermes_python.hermes import Hermes
from datetime import datetime
from pytz import timezone
from collections import namedtuple
import http.client
import json
import Patient

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

def intent_received(hermes, intent_message):
	reminder_msg = ""
	now = datetime.now(timezone('Europe/Paris'))

	try:
		apiConnection = http.client.HTTPConnection('http://vouvouf.eu:8080/api/patients/1')
		apiResponse = apiConnection.getresponse()

		patient = json.loads(apiResponse.read(), object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))

		reminder_msg = "Le patient s'appelle {0} {1}".format(patient.FirstName, patient.LastName)
	except:
		reminder_msg = "ça ne marche pas"

	hermes.publish_end_session(intent_message.session_id, reminder_msg)

with Hermes(MQTT_ADDR) as h:
	h.subscribe_intents(intent_received).start()
