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
reminder_msg = ""
is_exception_raised = False
#pdb.set_trace()

"""def execute_action_from_intentName(intentName):
    switcher = {
        "DiiagePFC:AskPatientInfos": patient_info,
        "DiiagePFC:PillsReminder": patient_info,
    }
    # Get the function from switcher dictionary
    func = switcher.get(intentName, lambda: "Invalid intentName")
    # Execute the function
    func()"""


def patient_info_handler(hermes, intent_message):
	try:
		if intent_message.slots.count() == 0:
			raise ValueError('No slot value found')
		
		patientId = int(intent_message.slots.PatientId.first().value)
		print(patientId)

		apiResponse = requests.get("http://vouvouf.eu:8080/api/patients/{}".format(patientId), headers=headers)
		print("DEBUG : http://vouvouf.eu:8080/api/patients/{} | Status code = {}".format(patientId, apiResponse.status_code))

		if apiResponse.status_code == 200:
			patient = json.loads(apiResponse.text, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
			print(patient)
			reminder_msg = "Le patient numéro {} s appelle {} {}".format(patientId, patient.firstName, patient.lastName)
		else:
			raise ConnectionError #Mettre à jour l'API après une modif dans la BDD ?

	except ConnectionError:
		reminder_msg = "Désolé, je ne parviens pas à récupérer les informations demandées."
	except json.JSONDecodeError:
		reminder_msg = "Désolé, il y a un soucis, je ne parviens à interpréter les informations demandées."
	except ValueError:
		reminder_msg = "Excusez-moi, je n'ai pas compris de quel patient vous parlez, pouvez-vous répéter son numéro ?"
		hermes.publish_continue_session(intent_message.session_id, reminder_msg, ["PillsReminder"], slot_to_fill=json.dumps("PatientId"))
	else:
		hermes.publish_end_session(intent_message.session_id, reminder_msg)
	finally:
		print("DEBUG : reminder_msg = " + reminder_msg)


"""def pills_reminder_handler(hermes, intent_message):
	if reminder_msg == "":
		reminder_msg = "Désolé, un erreur est survenue, pouvez-vous répéter ou reformuler votre phrase s'il vous plaît ?" """


with Hermes(MQTT_ADDR) as h:
	print("test")
	#intent_received(None, '{"input": "comment s\' appelle le patient numéro un","intent": {"intentName": "DiiagePFC:AskPatientInfos","confidenceScore": 1},"slots": [{"rawValue": "un","value": {"kind": "Number","value": 1},"range": {"start": 37,"end": 39},"entity": "snips/number","slotName": "PatientId"}]}')
	h\
		.subscribe_intents("AskPatientInfos", patient_info_handler)\
		#.subscribe_intents("PillsReminder", pills_reminder_handler)\
		.start()
