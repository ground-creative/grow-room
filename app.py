#!/usr/bin/env python
#
# Grow system MQTT tuya cloud client
# Author: Ground Creative
# Version:1.1.0

import config.config as config
import time
import datetime
import coloredlogs
import sqlite3
import logging
import json
import paho.mqtt.client as mqtt
from queue import Queue
from threading import Thread
from modules.mqtt import MqttModule
from modules.tuya import TuyaModule
from modules.values import ValuesModule
from modules.devices import DevicesModule
from modules.cycle import WaterCycleModule
# Logging
coloredlogs.install(level = config.misc["debug_level"])
# Sqlite
connection = sqlite3.connect(config.sqlite["dbname"]  + ".db", check_same_thread = False)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()
#cursor.execute("DROP TABLE IF EXISTS dp")
#cursor.execute("DROP TABLE IF EXISTS devices")
#cursor.execute( "DROP TABLE IF EXISTS cycle" )
#connection.commit()
row = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dp'").fetchone()
if (row is None):
	logging.info("Setting up sqlite dp table")
	cursor.execute("CREATE TABLE dp (lights_state INTEGER,water_valve_state INTEGER, drain_pump_state INTEGER, feeding_pump_state INTEGER, mixing_pump_state INTEGER, fan_state INTEGER, extractor_state INTEGER, airco_state INTEGER, cur_water_level INTEGER, con_lcd INTEGER, air_sen_oled INTEGER, water_tester_oled INTEGER, main_con_night_mode INTEGER, air_sen_night_mode INTEGER, water_tester_night_mode INTEGER, doser_one_night_mode INTEGER, doser_two_night_mode INTEGER, doser_one_pump_one_name TEXT, doser_one_pump_two_name TEXT, doser_one_pump_three_name TEXT, doser_one_pump_four_name TEXT, doser_one_pump_five_name TEXT, doser_one_pump_six_name TEXT, doser_one_pump_one_dose INTEGER, doser_one_pump_two_dose INTEGER, doser_one_pump_three_dose INTEGER, doser_one_pump_four_dose INTEGER, doser_one_pump_five_dose INTEGER, doser_one_pump_six_dose INTEGER, cycle_min_ppm INTEGER, dose_sleep_time INTEGER, cycle_topup_value INTEGER, pause_cycle INTEGER)")
	cursor.execute("INSERT INTO dp VALUES (False, False, False, False, False, False, False, False, 0, True, True, True, False, False, False, False, False, 'D1 Pump 1', 'D1 Pump 2', 'D1 Pump 3', 'D1 Pump 4', 'D1 Pump 5', 'D1 Pump 6', 0, 0, 0, 0, 0, 0, 200, 30, 2, 0)") 
	connection.commit()
row = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='devices'").fetchone()
if (row is None):
	logging.info("Setting up sqlite devices table")
	cursor.execute("CREATE TABLE devices (id REAL,state REAL,last_seen INTEGER,last_alert INTEGER)" )
	cursor.execute("INSERT INTO devices VALUES ('" + config.misc[ "roomID" ] + "-main-controller','offline', NULL,NULL)")
	cursor.execute("INSERT INTO devices VALUES ('" + config.misc[ "roomID" ] + "-air-sensors','offline', NULL,NULL)")
	cursor.execute("INSERT INTO devices VALUES ('" + config.misc[ "roomID" ] + "-water-tester','offline', NULL,NULL)")
	cursor.execute("INSERT INTO devices VALUES ('" + config.misc[ "roomID" ] + "-doser-one','offline', NULL,NULL)")
	cursor.execute("INSERT INTO devices VALUES ('" + config.misc[ "roomID" ] + "-doser-two','offline', NULL,NULL)")
	connection.commit()
row = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cycle'" ).fetchone()	
if (row is None):
	logging.info("Setting up sqlite cycle table")
	cursor.execute("CREATE TABLE cycle (id INTEGER PRIMARY KEY AUTOINCREMENT,cycle INTEGER, cycle_type REAL,date_start INTEGER, date_stop INTEGER, refill_number INTEGER, refill_value INTEGER)")
	cursor.execute("INSERT INTO cycle VALUES (1,False,'water','','',0,2)") 	
	connection.commit()
# Set devices states
DevicesModule.set_current(connection)
# Set values states
ValuesModule.set_current(connection)
# Start mqtt local client
mqtt_client = mqtt.Client(config.misc["roomID"]) 
mqtt_client.on_connect = MqttModule.on_mqtt_connect
mqtt_client.on_message = MqttModule.on_mqtt_message
mqtt_client.message_callback_add(config.misc["roomID"] + "/air-sensors", MqttModule.on_air_sensors)
mqtt_client.message_callback_add(config.misc["roomID"] + "/water-tester", MqttModule.on_water_tester)
mqtt_client.message_callback_add("device-status/#", MqttModule.on_device_status)
mqtt_client.message_callback_add("m/" + config.misc["roomID"] + "/#", MqttModule.on_device_manual_action)
mqtt_client.username_pw_set(config.mqtt["user"], config.mqtt["password"])
mqtt_client.connect(config.mqtt["server"], config.mqtt["port"])
mqtt_client.loop_start()
# Start water cycle deamon
cycle_queue = Queue()
CycleModule = WaterCycleModule(mqtt_client, connection, cycle_queue)
Thread(target = CycleModule.run, args = (cycle_queue,)).start()
# Start tuya mqtt client
Tuya = TuyaModule(config.tuya["productid"], config.tuya["uuid"], config.tuya["authkey"], mqtt_client, CycleModule)
Tuya.client.connect() 
Tuya.client.loop_start()
# Send values to tuya mqtt server
while True:	
	CycleModule.send_queue("info", True)
	values = Tuya.values(ValuesModule.data())
	Tuya.client.push_dps(values)
	logging.info("Pushing loop dps data from loop: %s", values)
	mqtt_client.publish(config.misc["roomID"] + "/water-level" , json.dumps({"level": ValuesModule.data("cur_water_level")}))
	time.sleep(config.tuya["update_interval"])