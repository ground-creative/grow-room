#!/usr/bin/env python

from tuyalinksdk.client import TuyaClient
from tuyalinksdk.console_qrcode import qrcode_generate
from modules.values import ValuesModule
from modules.devices import DevicesModule
import config.config as config
import logging

class TuyaModule:
	
	def __init__( self, productid, uuid, authkey, mqttClient ):
		
		self.client = TuyaClient( productid, uuid, authkey )
		self.client.on_connected = self.on_connected
		self.client.on_qrcode = self.on_qrcode
		self.client.on_reset = self.on_reset
		self.client.on_dps = self.on_dps
		self.mqtt = mqttClient

	def on_connected( self ):
		
		print( 'Connected to tuya mqtt server!' )

	def on_qrcode( self, url ):
		
		qrcode_generate( url )

	def on_reset( self, data ):
		
		print( 'Reset:', data )

	def on_dps( self, dps ):
		
		print( 'DataPoints received: ', dps )
		key = next( iter(dps) )
		
		# Current water level
		if ( key == config.dps[ "cur_water_level" ] ):
			logging.info( "setting current water level to " + str( dps[ key ] ) )
			ValuesModule.set( "cur_water_level", dps[ key ] )
		
		# Relays states
		elif ( isinstance( dps[ key ], ( bool ) ) ):
			
			for function in config.dps:
				if ( config.dps[ function ] == key ):
					logging.info( "setting " + function.replace( "_" , " " ) + " to " + str( dps[ key ] ) )
					ValuesModule.set( function, dps[ key ] )
					subtopic = function.replace( "_state" , "" ).replace( "_" , "-" )
					self.mqtt.publish( config.misc[ "roomID" ] + "/" + subtopic  , int( dps[ key ] ) )
					
		values = self.values( ValuesModule.data( ) )
		logging.info( "Pushing action dps data from loop: %s", values )	
		self.client.push_dps( values )
		
	def values( self, data ):

		devices = DevicesModule.data( )
		dps = { }
		
		#values
		dps[ config.dps[ "lights_state" ] ] = data[ "lights_state" ]
		dps[ config.dps[ "extractor_state" ] ] = data[ "extractor_state" ]
		dps[ config.dps[ "water_valve_state" ] ] = data[ "water_valve_state" ]
		dps[ config.dps[ "mixing_pump_state" ] ] = data[ "mixing_pump_state" ]
		dps[ config.dps[ "fan_state" ] ] = data[ "fan_state" ]
		dps[ config.dps[ "feeding_pump_state" ] ] = data[ "feeding_pump_state" ]
		dps[ config.dps[ "drain_pump_state" ] ] = data[ "drain_pump_state" ]
		dps[ config.dps[ "cur_water_level" ] ] = data[ "cur_water_level" ]
		
		# devices states
		dps[ config.dps[ "display_network_state" ] ] = devices[ "display_network_state" ]
		
		return dps