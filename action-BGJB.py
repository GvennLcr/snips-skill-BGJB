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
now = datetime.now(timezone('Europe/Paris'))
headers = {'Content-Type': 'application/json'}
is_exception_raised = False
#pdb.set_trace()


def patient_info_handler(hermes, intent_message):
	try:
		patient_info = ""
		print(intent_message)
		if intent_message.slots.count() == 0:
			raise ValueError('No slot value found')

		patientId = int(intent_message.slots.PatientId.first().value)
		print(patientId)

		apiResponse = requests.get("http://vouvouf.eu:8080/api/patients/{}".format(patientId), headers=headers)
		print("DEBUG : http://vouvouf.eu:8080/api/patients/{} | Status code = {}".format(patientId, apiResponse.status_code))

		if apiResponse.status_code == 200:
			patient = json.loads(apiResponse.text, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
			print(patient)
			patient_info = "Le patient numéro {} s appelle {} {}".format(patientId, patient.firstName, patient.lastName)
		else:
			raise ConnectionError #Mettre à jour l'API après une modif dans la BDD ?

	except ConnectionError:
		patient_info = "Désolé, je ne parviens pas à récupérer les informations demandées."
	except json.JSONDecodeError:
		patient_info = "Désolé, il y a un soucis, je ne parviens à interpréter les informations demandées."
	except ValueError:
		patient_info = "Excusez-moi, je n'ai pas compris de quel patient vous parlez, pouvez-vous répéter son numéro ?"
		hermes.publish_continue_session(intent_message.session_id, patient_info, ["PillsReminder"], slot_to_fill=json.dumps("PatientId"))
	else:
		hermes.publish_end_session(intent_message.session_id, patient_info)
	finally:
		print("DEBUG : patient_info = " + patient_info)


with Hermes(MQTT_ADDR) as h:
	print("test")
	h.subscribe_intents('DiiagePFC:AskPatientInfos', patient_info_handler).start()