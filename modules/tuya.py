#!/usr/bin/env python

from tuyalinksdk.client import TuyaClient
from tuyalinksdk.console_qrcode import qrcode_generate
from modules.values import ValuesModule
from modules.devices import DevicesModule
import config.config as config
import logging
import json
import time

class TuyaModule:
	def __init__( self, productid, uuid, authkey, mqttClient, CycleModule ):
		self.client = TuyaClient( productid, uuid, authkey )
		self.client.on_connected = self.on_connected
		self.client.on_qrcode = self.on_qrcode
		self.client.on_reset = self.on_reset
		self.client.on_dps = self.on_dps
		self._mqtt = mqttClient
		self._cycle = CycleModule
		self._change_water_level_started = False
		self._new_water_level = 0
	def on_connected(self):
		print('Connected to tuya mqtt server!')
	def on_qrcode(self, url):
		qrcode_generate(url)
	def on_reset(self, data):
		print('Reset:', data)
	def on_dps(self, dps):
		print('DataPoints received: ', dps)
		key = next(iter(dps))
		# Change water level		
		if (config.dps[ "new_water_level" ] in dps):
			if (dps[ config.dps[ "new_water_level" ] ] > ValuesModule.data("cur_water_level")):
				self._change_water_level_started = True
				self._new_water_level = dps[ config.dps[ "new_water_level" ] ]
				ValuesModule.set( "water_valve_state", True )
				ValuesModule.set( "drain_pump_state", False )
				self._mqtt.publish( config.misc["roomID"] + "/water-valve"  , 1)
				self._mqtt.publish( config.misc["roomID"] + "/drain-pump"  , 0)
			elif (dps[config.dps["new_water_level"]] < ValuesModule.data("cur_water_level")):
				self._change_water_level_started = True
				self._new_water_level = dps[config.dps["new_water_level"]]
				ValuesModule.set("water_valve_state", False)
				ValuesModule.set("drain_pump_state", True)
				self._mqtt.publish(config.misc["roomID"] + "/water-valve", 0)
				self._mqtt.publish(config.misc["roomID"] + "/drain-pump" , 1)
		# Current water level
		elif (key == config.dps["cur_water_level"]):
			logging.info("Setting current water level to " + str(dps[key]))
			ValuesModule.set("cur_water_level", dps[key])
			self._mqtt.publish(config.misc["roomID"] + "/water-level" , json.dumps({"level": dps[key] }))
			if (self._change_water_level_started == True and self._new_water_level == dps[key] ):
				ValuesModule.set("water_valve_state", False)
				ValuesModule.set("drain_pump_state", False)
				self._mqtt.publish(config.misc["roomID"] + "/water-valve", 0)
				self._mqtt.publish(config.misc["roomID"] + "/drain-pump", 0)
				self._change_water_level_started = False
		# Main controller lcd backlight
		elif (key == config.dps["con_lcd"]):
			self._mqtt.publish(config.misc["roomID"] + "/main-controller-display-backlight", int(dps[key]))
			ValuesModule.set("con_lcd", dps[ key ])
		# Air sensors oled backlight
		elif (key == config.dps["air_sen_oled"]):
			self._mqtt.publish(config.misc["roomID"] + "/air-sensors-display-backlight", int(dps[key]))
			ValuesModule.set("air_sen_oled", dps[key])		
		# Cycle on/off
		elif (key == config.dps["cycle_job"]):
			if (dps[key] == True):
				self._cycle.turn_on()
			elif (dps[key] == False):
				self._cycle.turn_off()
		# Change Cycle Type
		elif (config.dps["cycle_type"] in dps):
			self._cycle.change_type(dps[config.dps["cycle_type"]])
		# Pause Cycle		
		elif (key == config.dps["pause_cycle"]):
			if (dps[key] == True):
				self._cycle.pause()
			# Resume Paused Cycle	
			elif (dps[key] == False):
				self._cycle.resume()
		# Restart	
		elif (key == config.dps["restart"]):
			self._mqtt.publish(config.misc["roomID"] + "/air-sensors-restart", int(dps[key]))	
			self._mqtt.publish(config.misc["roomID"] + "/main-controller-restart", int(dps[key]))			
		# Relays states
		elif (isinstance(dps[key], (bool))):
			for function in config.dps:
				if (config.dps[function] == key):
					logging.info("setting " + function.replace("_", " ") + " to " + str(dps[key]))
					ValuesModule.set( function, dps[ key ] )
					subtopic = function.replace("_state", "").replace("_", "-")
					self._mqtt.publish( config.misc["roomID"] + "/" + subtopic  , int(dps[key]))
					if (function == "drain_pump_state" and dps[key] == False):
						self._change_water_level_started = False
					if (function == "water_valve_state" and dps[key] == False):
						self._change_water_level_started = False
		values = self.values(ValuesModule.data())
		logging.info("Pushing action dps data from loop: %s", values)	
		self.client.push_dps(values)
		#time.sleep( 2 )
	def values(self, data):
		devices = DevicesModule.data()
		dps = {}
		#values
		dps[config.dps["lights_state"]] = data["lights_state"]
		dps[config.dps["extractor_state"]] = data["extractor_state"]
		dps[config.dps["water_valve_state"]] = data["water_valve_state"]
		dps[config.dps["mixing_pump_state"]] = data["mixing_pump_state"]
		dps[config.dps["fan_state"]] = data["fan_state"]
		dps[config.dps["feeding_pump_state"]] = data["feeding_pump_state"]
		dps[config.dps["drain_pump_state"]] = data["drain_pump_state"]
		dps[config.dps["airco_state"]] = data["airco_state"]
		dps[config.dps["cur_water_level"]] = data["cur_water_level"]
		dps[config.dps["new_water_level"]] = data["cur_water_level"]
		dps[config.dps["in_temp"]] = data["in_temp"]
		dps[config.dps["out_temp"]] = data["out_temp"]
		dps[config.dps["in_hum"]] = data["in_hum"]
		dps[config.dps["in_co2"]] = data["in_co2"]
		dps[config.dps["water_temp"]] = data["water_temp"]
		dps[config.dps["ph"]] = data["ph"]
		dps[config.dps["ppm"]] = data["ppm"]
		dps[config.dps["ec"]] = data["ec"]
		dps[config.dps["con_lcd"]] = data["con_lcd"]
		dps[config.dps["air_sen_oled"]] = data["air_sen_oled"]
		dps[config.dps["cycle_type"]] = data["cycle_type"]
		dps[config.dps["pause_cycle"]] = data["pause_cycle"]
		dps[config.dps["cycle_job"]] = data["cycle_job"]
		dps[config.dps["cycle_start_date"]] = data["cycle_start_date"]
		dps[config.dps["cycle_days"]] = data["cycle_days"]
		dps[config.dps["cycle_week"]] = data["cycle_week"]
		dps[config.dps["cycle_topup"]] = data["cycle_topup"]
		# devices network states
		dps[config.dps["display_network_state"]] = devices["display_network_state"]
		dps[config.dps["airsensors_network_state"]] = devices["airsensors_network_state"]
		dps[config.dps["doser_one_network_state"]] = devices["doser_one_network_state"]
		return dps