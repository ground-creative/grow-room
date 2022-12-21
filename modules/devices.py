#!/usr/bin/env python

import config.config as config
from datetime import datetime

class DevicesModule:
	def set_current( connection ):
		DevicesModule._connection = connection
		DevicesModule._values = { }
		cursor = DevicesModule._connection.cursor( )
		rows = DevicesModule._connection.execute( "SELECT * FROM devices" ).fetchall( )
		for device in rows:
			if device[ "id" ] == config.misc[ "roomID" ] + "-main-controller":
				DevicesModule._values[ "display_network_state" ] = device[ "state" ]
			if device[ "id" ] == config.misc[ "roomID" ] + "-air-sensors":
				DevicesModule._values[ "airsensors_network_state" ] = device[ "state" ]
			if device[ "id" ] == config.misc[ "roomID" ] + "-doser-one":
				DevicesModule._values[ "doser_one_network_state" ] = device[ "state" ]
			if device[ "id" ] == config.misc[ "roomID" ] + "-doser-two":
				DevicesModule._values[ "doser_two_network_state" ] = device[ "state" ]
			if device[ "id" ] == config.misc[ "roomID" ] + "-water-tester":
				DevicesModule._values[ "water_tester_network_state" ] = device[ "state" ]
	def data( key =  None ):
		if ( key is None ):
			return DevicesModule._values
		return DevicesModule._values[ key ]
		
	def set( key, value , deviceID = None ):
		DevicesModule._values[ key ] = value
		if ( deviceID is not None ):
			time_update = datetime.now( )
			DevicesModule._connection.cursor( ).execute( "UPDATE devices SET state = ?, last_seen = ? WHERE id = ?" , ( value, time_update, deviceID ) )
			DevicesModule._connection.commit( )