#!/usr/bin/env python

import config.config as config
import logging
import json
import time
from datetime import datetime
from datetime import timedelta
from modules.values import ValuesModule
from modules.devices import DevicesModule

class WaterCycleModule:
	def __init__(self, mqttClient, connection, cycleQueue):
		self._mqtt = mqttClient
		self._connection = connection
		self._queue = cycleQueue
		cursor = self._connection.cursor()
		self._values = {}
		self.update_values(True)
		if (self._values["cycle_job"] == True and ValuesModule.data("pause_cycle") == True):
			self.send_queue("pause")
		else:
			self.send_queue("boot")
	def run(self, args):
		cycle = False
		water_level = 0
		cycle_type = "water"
		working = False
		start_com = False
		pause = ValuesModule.data("pause_cycle")
		#feeding = False
		feeding_wait_time = 0
		wait_feeding_interval = 300
		while True:
			try:
				data = json.loads(args.get())
				logging.info("thread data %s" , data)
				if (data["com"] == "start"):
					start_com = True
				if (data["com"] == "pause"):
					print('Pausing water cycle job')
					pause = True	
					if (working == True):
						self._mqtt.publish(config.misc[ "roomID" ] + "/drain-pump"  , "0")
						self._mqtt.publish(config.misc[ "roomID" ] + "/water-valve"  , "0")
						ValuesModule.set("water_valve_state", False)
						ValuesModule.set("drain_pump_state", False)
				if (data["com"] == "resume"):
					print('Resuming water cycle job')
					pause = False
				if (data["cycle"] == 0):
					pause = False
				if (data["cycle"] == 1 and pause == False):
					print('Cycle job is active')
					cycle = True
					water_level = data["water_level"]
					cycle_type = data["cycle_type"]
					if (DevicesModule.data("display_network_state") == "offline"):
						print('Cycle job skipping, main controller is offline...')
						#working = False
						continue
					if (ValuesModule.data("feeding_pump_state") == True):
						if (working == False):	# the pump started before the cycle
							if (feeding_wait_time == 0):
								print('Cycle job started waiting')
							else:
								print('Cycle job is waiting for feeding pump to finish...')
							feeding_wait_time = time.time()
							#feeding = True
							continue
						else:	# the cycle started before the pump
							ValuesModule.set("feeding_pump_state", False)
							self._mqtt.publish(config.misc[ "roomID" ] + "/feeding-pump", "0")
					elif (feeding_wait_time > 0):
						print('Cycle job is waiting...')
						waiting_time_left = time.time() - feeding_wait_time
						if ( waiting_time_left >= wait_feeding_interval):
							print('Cycle job finshed waiting')
							feeding_wait_time = 0;
						else:
							print('Cycle job is waiting for water drain, waiting time: ' + str( wait_feeding_interval - waiting_time_left ) + ' seconds')
							continue
					if (ValuesModule.data("feeding_pump_state") == True and working == True):
						ValuesModule.set("feeding_pump_state", False)
						self._mqtt.publish(config.misc[ "roomID" ] + "/feeding-pump"  , "0")
					if (water_level < 50 and working == False):
						if (ValuesModule.data("cycle_topup_value")  <= int(data["topup"]) and water_level > 0):
							print('Cycle job empty and refill, starting to drain water')
							self._mqtt.publish(config.misc[ "roomID" ] + "/drain-pump"  , "1")
							self._mqtt.publish(config.misc[ "roomID" ] + "/water-valve"  , "0")
							self._mqtt.publish(config.misc[ "roomID" ] + "/feeding-pump"  , "0")
							ValuesModule.set("water_valve_state", False)
							ValuesModule.set("feeding_pump_state", False)
							ValuesModule.set("drain_pump_state", True)
							working = True
						elif (ValuesModule.data("cycle_topup_value")  > int(data["topup"])):
							if (start_com == True):
								print('Cycle job refill ' + str(int(data["topup"])))
							else:
								print('Cycle job refill ' + str(int(data["topup"]) + 1))
							self._mqtt.publish(config.misc[ "roomID" ] + "/drain-pump" , "0")
							self._mqtt.publish(config.misc[ "roomID" ] + "/feeding-pump" , "0")
							self._mqtt.publish(config.misc[ "roomID" ] + "/water-valve" , "1")
							ValuesModule.set("water_valve_state", True)
							ValuesModule.set("feeding_pump_state", False)
							ValuesModule.set("drain_pump_state", False)
							working = True
					elif (water_level >= 75 and working == True):
						print("Cycle job water reached 75%...")
						ValuesModule.set("water_valve_state", False)
						self._mqtt.publish( config.misc[ "roomID" ] + "/water-valve" , "0" )
						if (DevicesModule.data("water_tester_network_state") == "offline"):
							print('Cycle job skipping, cannot check ppm. Water tester is offline...')
							#working = True
							#continue
						else:
							if (start_com == True):
								self._values[ "cycle_topup" ] = 0
								if(data["ppm"] <= ValuesModule.data("cycle_min_ppm")):
									start_com = False
							else:
								self._values[ "cycle_topup" ] = 0 if ValuesModule.data("cycle_topup_value")  <= int(data["topup"]) else int(data["topup"]) + 1
							if (self._values[ "cycle_topup" ] == 0 and data["ppm"] > ValuesModule.data("cycle_min_ppm")):
								print("Cycle job ppm too high, draining water tank again...")
								self._mqtt.publish(config.misc[ "roomID" ] + "/drain-pump" , "1")
								ValuesModule.set("drain_pump_state", True)
								#working = True
								#continue
							elif (cycle_type != "water" and DevicesModule.data("doser_one_network_state") == "offline"):
								print('Cycle job skipping, doser one is offline...')
								#working = True
								#continue
							else:
								if (cycle_type != "water" and cycle_type != "schedule"):
									self._mqtt.publish(config.misc[ "roomID" ] + "/mixing-pump" , "1")
									if (ValuesModule.data("doser_one_pump_one_dose") > 0):
										dose = self.calculate_dose(ValuesModule.data("doser_one_pump_one_dose"))
										self._mqtt.publish( config.misc[ "roomID" ] + "/doser-one/p-one" , dose)
										time.sleep(ValuesModule.data("dose_sleep_time"))
									if (ValuesModule.data("doser_one_pump_two_dose") > 0):
										dose = self.calculate_dose(ValuesModule.data("doser_one_pump_two_dose"))
										self._mqtt.publish( config.misc[ "roomID" ] + "/doser-one/p-two" , dose)
										time.sleep(ValuesModule.data("dose_sleep_time"))
									if (ValuesModule.data("doser_one_pump_three_dose") > 0):
										dose = self.calculate_dose(ValuesModule.data("doser_one_pump_three_dose"))
										self._mqtt.publish( config.misc[ "roomID" ] + "/doser-one/p-three" , dose)
										time.sleep(ValuesModule.data("dose_sleep_time"))
									if (ValuesModule.data("doser_one_pump_four_dose") > 0):
										dose = self.calculate_dose(ValuesModule.data("doser_one_pump_four_dose"))
										self._mqtt.publish( config.misc[ "roomID" ] + "/doser-one/p-four" , dose)
										time.sleep(ValuesModule.data("dose_sleep_time"))
									if (ValuesModule.data("doser_one_pump_five_dose") > 0):
										dose = self.calculate_dose(ValuesModule.data("doser_one_pump_five_dose"))
										self._mqtt.publish( config.misc[ "roomID" ] + "/doser-one/p-five" , dose)
										time.sleep(ValuesModule.data("dose_sleep_time"))
									if (ValuesModule.data("doser_one_pump_six_dose") > 0):
										dose = self.calculate_dose(ValuesModule.data("doser_one_pump_six_dose"))
										self._mqtt.publish( config.misc[ "roomID" ] + "/doser-one/p-six" , dose)
										time.sleep(ValuesModule.data("dose_sleep_time"))
								print("Cycle job finished. PPM ok, saving to db")
								working = False
								self._connection.cursor( ).execute("UPDATE cycle SET refill_number = " + str(self._values[ "cycle_topup" ]) + " WHERE id = (SELECT MAX(id) FROM cycle)")
								self._connection.commit( )
					elif ( water_level < 25 and working == True):
						print('Cycle job empty and refill, starting to refill the tank')
						self._mqtt.publish(config.misc[ "roomID" ] + "/drain-pump" , "0")
						self._mqtt.publish(config.misc[ "roomID" ] + "/water-valve" , "1")
						self._mqtt.publish(config.misc[ "roomID" ] + "/feeding-pump" , "0")
						ValuesModule.set("water_valve_state", True)
						ValuesModule.set("feeding_pump_state", False)
						ValuesModule.set("drain_pump_state", False)
				elif (data["cycle"] == 0 and cycle == True):
					cycle = False
					working = False
					print("Killing cycle job...")
					self._mqtt.publish(config.misc[ "roomID" ] + "/water-valve" , "0")
					self._mqtt.publish(config.misc[ "roomID" ] + "/drain-pump" , "0")
					ValuesModule.set("water_valve_state", False)
					ValuesModule.set("drain_pump_state", False)
				if (water_level == 100):
					self._mqtt.publish(config.misc[ "roomID" ] + "/water-valve" , "0")
					ValuesModule.set("water_valve_state", False)
					working = False
			except Exception as e:
				logging.exception( e )
	def update_values(self,all = None):
		if (all is not None):
			row = self._connection.cursor().execute("SELECT * FROM cycle ORDER by id DESC LIMIT 1").fetchone()
			#self._values = {}
			self._values["cycle_job"] = bool(row["cycle"])
			self._values["cycle_type"] = row[ "cycle_type"]
			if(row["date_start"]):
				self._values["date_start"] = row["date_start"]
			else:
				self._values["date_start"] = str(datetime.now())
			self._values["cycle_topup"] = 0 if self._values["cycle_job"] == False else row["refill_number"]
		logging.info("Updating cycle values")
		date_format = "%Y-%m-%d %H:%M:%S.%f"
		convert_date = datetime.strptime(self._values["date_start"], date_format)
		self._values["cycle_start_date"] = convert_date.strftime('%d') +' ' + convert_date.strftime("%b")  if self._values["cycle_job"] == True else ""
		adate = convert_date #datetime.strptime( row[ "date_start" ] , date_format )
		bdate = datetime.strptime(str(datetime.now()), date_format)
		deltadate = bdate - adate
		self._values["cycle_days"] = 0 if self._values["cycle_job"] == False else deltadate.days + 1
		self._values["cycle_week"] =  0 if self._values["cycle_job"] == False else (deltadate.days + 1) // 7 + 1
		ValuesModule.set("cycle_type", self._values["cycle_type"], False)
		ValuesModule.set("cycle_job", self._values["cycle_job"], False)
		ValuesModule.set("cycle_topup", self._values["cycle_topup"], False)
		ValuesModule.set("cycle_start_date", self._values["cycle_start_date"], False)
		ValuesModule.set("cycle_days", self._values["cycle_days"], False)
		ValuesModule.set("cycle_week", self._values["cycle_week"], False)
	def data(self, key = None):
		if (key is None):
			return self._values
		return self._values[key]		
	def turn_on(self):
		logging.info( "Switching on cycle job.." )
		date = datetime.now( )
		self._connection.cursor().execute("INSERT INTO cycle VALUES ((SELECT MAX(id) FROM cycle)+1,1,'" + self._values["cycle_type"] + "','" + str(date) + "','',0," + str(ValuesModule.data("cycle_topup_value")) + ")") 
		self._connection.commit( )
		self.update_values(True)
		self.send_queue("start")
	def turn_off(self):
		logging.info("Switching off cycle job..")
		date = datetime.now()
		self._connection.cursor().execute("UPDATE cycle SET cycle = 0, date_stop = '" + str(date) + "' WHERE id = (SELECT MAX(id) FROM cycle)")
		self._connection.commit()
		self.update_values(True)
		ValuesModule.set("pause_cycle", False)
		self.send_queue("stop")
	def change_type(self,type):
		logging.info("Changing cycle type to " + type)
		self._values["cycle_type"] = type
		self._connection.cursor().execute("UPDATE cycle SET cycle_type = '" + self._values["cycle_type"] + "' WHERE id = (SELECT MAX(id) FROM cycle)")
		self._connection.commit()
		self.update_values();
	def pause(self):
		logging.info("Pausing cycle")
		ValuesModule.set("pause_cycle", True)
		self.send_queue("pause")
	def resume(self):
		logging.info("Resuming cycle")
		ValuesModule.set("pause_cycle", False)
		self.send_queue("resume")
	def calculate_dose(self, fullDose):
		if (self._values["cycle_type"] == "half"):
			dose = fullDose//2
		elif (self._values["cycle_type"] == "quarter"):
			dose = fullDose//4
		else:
			dose = fullDose
		if (self._values[ "cycle_topup" ]  > 0):
			dose = dose//2
		return dose
	def send_queue(self, command, update = None):
		cyle_queue = '{"cycle": ' + str(int(self._values["cycle_job"])) + ',"water_level": ' + str(ValuesModule.data("cur_water_level")) + ',"cycle_type": "' + self._values["cycle_type"] + '","topup": "' + str(self._values["cycle_topup"]) + '","ppm": ' + str(ValuesModule.data("ppm")) + ',"com": "' + command + '"}'
		logging.info("Sending cycle queue %s" , cyle_queue)
		if (update == True and self._values["cycle_job"] == True):
			self.update_values();
		self._queue.put(cyle_queue)