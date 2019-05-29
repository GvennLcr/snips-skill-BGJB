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

def get_info(info_type, patient):
	switcher = {
		"Informations": 'Le patient ',
		"Garant": "Voucher",
		"Traitement": get_treatments_text(patient),
		"Maladie": "Le patient numéro {} souffre des maladies suivantes : {}".format(patient.id, get_illnesses_text(patient.suffer)),
		"Nom": "Name"
	}
	return switcher.get(info_type, "Invalid info")

def get_treatments_text(patient):
	print("get_treatments_text : patient.frequency = {}".format(patient.frequency))

	if len(patient.frequency) == 0:
		return "Le patient ne suit aucun traitement."

	res = "Le patient numéro {} suit les traitements suivants : ".format(patient.id),

	for frequency in patient.frequency:
		res += '{} de {}, '.format(frequency.treatment.dosage, frequency.treatment.name)
		if frequency.medicationPerDay != 0:
			res += '{} fois par jour'.format(frequency.medicationPerDay)
		elif frequency.medicationPerWeek != 0:
			res += '{} fois par semaine'.format(frequency.medicationPerWeek)
		else:
			res += 'dont je ne connais pas la fréquence de prise.'

		if frequency.toDate != None:
			res += 'Ce médicament est à prendre jusqu\'au {}. '.format(frequency.toDate)

	print(res)
	return res

def get_illnesses_text(suffers):
	res = ""
	for suffer in suffers:
		res += suffer.illness.name + ", "
	return res


def patient_info_handler(hermes, intent_message):
	try:
		patient_info = ""
		patientId = int(intent_message.slots.PatientId.first().value)
		print(patientId)
		print("intent_message.slots.InfoType.first() = {}".format(intent_message.slots.InfoType.first()))

		apiResponse = requests.get("http://vouvouf.eu:8080/api/patients/AllInfos/{}".format(patientId), headers=headers)
		print("DEBUG : http://vouvouf.eu:8080/api/patients/AllInfos/{} | Status code = {}".format(patientId, apiResponse.status_code))

		if apiResponse.status_code != 200:
			raise ConnectionError #Mettre à jour l'API après une modif dans la BDD ?

		patient = json.loads(apiResponse.text, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
		print(patient)
		#print("patient.suffer.first().illness.name = {}".format(patient.suffer.first().illness.name))
		print("intent_message.slots.InfoType.first().value = {}".format(intent_message.slots.InfoType.first().value))
		patient_info = get_info(intent_message.slots.InfoType.first().value, patient)
		#patient_info = "Le patient numéro {} s appelle {} {}".format(patientId, patient.firstName, patient.lastName)

	except ConnectionError:
		patient_info = "Désolé, je ne parviens pas à récupérer les informations demandées."
	except json.JSONDecodeError:
		patient_info = "Désolé, il y a un soucis, je ne parviens à interpréter les informations demandées."
	except Exception:
		patient_info = "Désolé, une erreur est survenue, pouvez-vous répéter ou reformuler votre phrase s'il vous plaît ?"
	finally:
		print("DEBUG : patient_info = " + patient_info)
		hermes.publish_end_session(intent_message.session_id, patient_info)


with Hermes(MQTT_ADDR) as h:
	print("test")
	h.subscribe_intent('DiiagePFC:AskPatientInfos', patient_info_handler).start()