#!/usr/bin/env python

import config.config as config
import logging
import json
from modules.devices import DevicesModule
from modules.values import ValuesModule

class MqttModule:
	def on_mqtt_connect( mosq, userdata, flags, rc ):
		logging.info( "MQTT local server connected, subscribing to topics for room '" + config.misc[ "roomID" ] + "'" )
		mosq.subscribe(  config.misc[ "roomID" ] + "/#" )
		mosq.subscribe( "device-status/" + config.misc[ "roomID" ] + "-main-controller" )
		mosq.subscribe( "device-status/" + config.misc[ "roomID" ] + "-air-sensors" )
		mosq.subscribe( "m/" + config.misc[ "roomID" ] + "/#" )
	def  on_mqtt_message( mosq, userdata, msg ):
		logging.info( "MQTT Uncaught Message Received: " + str( msg.topic ) + " -> "  + str( msg.payload.decode( "utf-8" ) ) )
	def  on_device_status( mosq, userdata, msg ):
		state = msg.payload.decode( "utf-8" )
		logging.info( "MQTT Device Status: "  + msg.topic + " -> " + str( state ) )
		if ( "device-status/" + config.misc[ "roomID" ] + "-main-controller" == msg.topic ):
			DevicesModule.set( "display_network_state", state, config.misc[ "roomID" ] + "-display" )
		if ( "device-status/" + config.misc[ "roomID" ] + "-air-sensors" == msg.topic ):
			DevicesModule.set( "airsensors_network_state", state, config.misc[ "roomID" ] + "-air-sensors" )	
	def on_device_manual_action( mosq, userdata, msg ):
		value = msg.payload.decode( "utf-8" )
		logging.info( "MQTT Device Manual Action: "  + msg.topic + " -> " + str( value ) )
		if ( "m/" + config.misc[ "roomID" ] + "/mp-btn" == msg.topic ):
			ValuesModule.set( "mixing_pump_state", ( False if value == "0" else True ) )
		if ( "m/" + config.misc[ "roomID" ] + "/sv-btn" == msg.topic ):
			ValuesModule.set( "water_valve_state", ( False if value == "0" else True ) )
		if ( "m/" + config.misc[ "roomID" ] + "/dp-btn" == msg.topic ):
			ValuesModule.set( "drain_pump_state", ( False if value == "0" else True ) )
		if ( "m/" + config.misc[ "roomID" ] + "/ex-btn" == msg.topic ):
			ValuesModule.set( "extractor_state", ( False if value == "0" else True ) )
		if ( "m/" + config.misc[ "roomID" ] + "/fp-btn" == msg.topic ):
			ValuesModule.set( "feeding_pump_state", ( False if value == "0" else True ) )
		if ( "m/" + config.misc[ "roomID" ] + "/li-btn" == msg.topic ):
			ValuesModule.set( "lights_state", ( False if value == "0" else True ) )
		if ( "m/" + config.misc[ "roomID" ] + "/fa-btn" == msg.topic ):
			ValuesModule.set( "fan_state", ( False if value == "0" else True ) )
		if ( "m/" + config.misc[ "roomID" ] + "/ai-btn" == msg.topic ):
			ValuesModule.set( "airco_state", ( False if value == "0" else True ) )
		if ( "m/" + config.misc[ "roomID" ] + "/backlight-btn" == msg.topic ):
			ValuesModule.set( "con_lcd", ( False if value == "0" else True ) )
	def on_air_sensors( mosq, userdata, msg ):
		value = msg.payload.decode( "utf-8" )
		logging.info( "MQTT Device Air Values: "  + msg.topic + " -> " + str( value ) )
		try:
			data = json.loads( value )
			ValuesModule.set( "in_temp", int( str( data[ "i"] ).replace('.', '') ), False )
			ValuesModule.set( "out_temp", int( str( data[ "o"] ).replace('.', '') ), False )	
			ValuesModule.set( "in_hum", int( str( data[ "h"] ).replace('.', '') ), False )
			ValuesModule.set( "in_co2", int( str( data[ "c"] ).replace('.', '') ), False )
		except Exception as e:
			logging.exception( e )
	def on_water_tester( mosq, userdata, msg ):
		value = msg.payload.decode( "utf-8" )
		logging.info( "MQTT Device Water Values: "  + msg.topic + " -> " + str( value ) )
		try:
			data = json.loads( value )
			ValuesModule.set( "water_temp", int( str( data[ "water_temp"] ).replace('.', '') ), False )
			ValuesModule.set( "ph", int( str( data[ "ph"] ).replace('.', '') ), False )	
			ValuesModule.set( "ppm", int( str( data[ "ppm"] ).replace('.', '') ), False )
			ValuesModule.set( "ec", int( str( data[ "ec"] ).replace('.', '') ), False )
		except Exception as e:
			logging.exception( e )