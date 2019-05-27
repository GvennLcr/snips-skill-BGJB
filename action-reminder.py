#!/usr/bin/env python3
from hermes_python.hermes import Hermes
from datetime import datetime
from pytz import timezone
from collections import namedtuple
import json
import pdb
import requests

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

def intent_received(hermes, intent_message):
	reminder_msg = ""
	now = datetime.now(timezone('Europe/Paris'))

	try:
		intent_json = json.loads(intent_message)
		patientId = intent_json['slots'][0]['value']['value']

		headers = {'Content-Type': 'application/json'}
		apiResponse = requests.get("http://vouvouf.eu:8080/api/patients/{}".format(patientId), headers=headers)
		pdb.set_trace()

		if apiResponse.status_code == 200:
			patient = json.loads(apiResponse.text, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
			print(patient)
			reminder_msg = "Le patient s'appelle {0} {1}".format(patient.firstName, patient.lastName)
		else:
			raise ConnectionError #Mettre à jour l'API après une modif dans la BDD ?

	except ConnectionError:
		reminder_msg = "Désolé, je ne parviens pas à récupérer les informations demandées."
	except json.JSONDecodeError:
		reminder_msg = "Désolé, il y a un soucis, je ne parviens à interpréter les informations demandées."

	if reminder_msg == "":
		reminder_msg = "ça ne marche pas"

	print("DEBUG : reminder_msg = " + reminder_msg)
	hermes.publish_end_session(intent_message.session_id, reminder_msg)

with Hermes(MQTT_ADDR) as h:
	print("test")
	#intent_received(None, '{"input": "comment s\' appelle le patient numéro un","intent": {"intentName": "DiiagePFC:AskPatientInfos","confidenceScore": 1},"slots": [{"rawValue": "un","value": {"kind": "Number","value": 1},"range": {"start": 37,"end": 39},"entity": "snips/number","slotName": "PatientId"}]}')
	h.subscribe_intents(intent_received).start()

"""
class Patient:
    def __init__(self, id, firstName, lastName, birthdate, address, voucher, phone):
        self.Id = id
        self.FirstName = firstName
        self.LastName = lastName
        self.Birthdate = birthdate
        self.Address = address
        self.Voucher = voucher
        self.Phone = phone
"""