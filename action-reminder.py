#!/usr/bin/env python3
from hermes_python.hermes import Hermes
from datetime import datetime
from pytz import timezone
from collections import namedtuple
import json
import requests
#import http.client
#import Patient

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

def intent_received(hermes, intent_message):
	reminder_msg = ""
	now = datetime.now(timezone('Europe/Paris'))

	try:
		headers = {'Content-Type': 'application/json'}
		
		#apiConnection = http.client.HTTPConnection('www.vouvouf.eu/api/patients/1', 8080)
		apiResponse = requests.get("http://vouvouf.eu:8080/api/patients/1", headers=headers)

		if apiResponse.status_code == 200:
			patient = json.loads(apiResponse.read(), object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
			reminder_msg = "Le patient s'appelle {0} {1}".format(patient.FirstName, patient.LastName)

	except ConnectionError:
		reminder_msg = "Désolé, je ne parviens pas à récupérer les informations demandées."
	#except http.client.HTTPException:
		#reminder_msg = "Désolé, je ne parviens pas à me connecter pour récupérer les informations demandées."
	except json.JSONDecodeError:
		reminder_msg = "Désolé, il y a un soucis, je ne parviens à interpréter les informations demandées."

	if reminder_msg == "":
		try:
			headers = {'Content-Type': 'application/json'}
			
			s = requests.Session()
			apiResponse = s.get("http://vouvouf.eu:8080/api/patients/1", headers=headers)

			if apiResponse.status_code == 200:
				patient = json.loads(apiResponse.read(), object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
				reminder_msg = "Le patient s'appelle {0} {1}".format(patient.FirstName, patient.LastName)

		except ConnectionError:
			reminder_msg = "Désolé, je ne parviens pas à récupérer les informations demandées."
		#except http.client.HTTPException:
			#reminder_msg = "Désolé, je ne parviens pas à me connecter pour récupérer les informations demandées."
		except json.JSONDecodeError:
			reminder_msg = "Désolé, il y a un soucis, je ne parviens à interpréter les informations demandées."

	if reminder_msg == "":
		reminder_msg = "ça ne marche pas"

	hermes.publish_end_session(intent_message.session_id, reminder_msg)

with Hermes(MQTT_ADDR) as h:
	h.subscribe_intents(intent_received).start()

class Patient:
    def __init__(self, id, firstName, lastName, birthdate, address, voucher, phone):
        self.Id = id
        self.FirstName = firstName
        self.LastName = lastName
        self.Birthdate = birthdate
        self.Address = address
        self.Voucher = voucher
        self.Phone = phone