#!/usr/bin/env python

import config.config as config
import logging
from modules.devices import DevicesModule
from modules.values import ValuesModule

class MqttModule:

	def on_mqtt_connect( mosq, userdata, flags, rc ):
		logging.info( "MQTT local server connected, subscribing to topics for room '" + config.misc[ "roomID" ] + "'" )
		mosq.subscribe(  config.misc[ "roomID" ] + "/#" )
		mosq.subscribe( "device-status/" + config.misc[ "roomID" ] + "-display" )
		mosq.subscribe( "device-manual-action/" + config.misc[ "roomID" ] + "/#" )

	def  on_mqtt_message( mosq, userdata, msg ):
		logging.info( "MQTT Uncaught Message Received: " + str( msg.topic ) + " -> "  + str( msg.payload.decode( "utf-8" ) ) )
		
	def  on_device_status( mosq, userdata, msg ):
		state = msg.payload.decode( "utf-8" )
		logging.info( "MQTT Device Status: "  + msg.topic + " -> " + str( state ) )
		if ( "device-status/" + config.misc[ "roomID" ] + "-display" == msg.topic ):
			DevicesModule.set( "display_network_state", state, config.misc[ "roomID" ] + "-display" )
			
	def on_device_manual_action( mosq, userdata, msg ):
		value = msg.payload.decode( "utf-8" )
		logging.info( "MQTT Device Manual Action: "  + msg.topic + " -> " + str( value ) )
		if ( "device-manual-action/" + config.misc[ "roomID" ] + "/mixing-pump-btn-pressed" == msg.topic ):
			ValuesModule.set( "mixing_pump_state", ( False if value == "0" else True ) )
		if ( "device-manual-action/" + config.misc[ "roomID" ] + "/solenoid-valve-btn-pressed" == msg.topic ):
			ValuesModule.set( "water_valve_state", ( False if value == "0" else True ) )
		if ( "device-manual-action/" + config.misc[ "roomID" ] + "/drain-pump-btn-pressed" == msg.topic ):
			ValuesModule.set( "drain_pump_state", ( False if value == "0" else True ) )
		if ( "device-manual-action/" + config.misc[ "roomID" ] + "/extractor-btn-pressed" == msg.topic ):
			ValuesModule.set( "extractor_state", ( False if value == "0" else True ) )
		if ( "device-manual-action/" + config.misc[ "roomID" ] + "/feeding-pump-btn-pressed" == msg.topic ):
			ValuesModule.set( "feeding_pump_state", ( False if value == "0" else True ) )
		if ( "device-manual-action/" + config.misc[ "roomID" ] + "/lights-btn-pressed" == msg.topic ):
			ValuesModule.set( "lights_state", ( False if value == "0" else True ) )