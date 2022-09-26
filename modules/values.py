#!/usr/bin/env python

class ValuesModule:
	
	def set_current( connection ):
		
		ValuesModule._connection = connection
		cursor = ValuesModule._connection.cursor( )
		row = ValuesModule._connection.execute( "SELECT * FROM dp" ).fetchone( )
		ValuesModule._values = { }
		ValuesModule._values[ "feeding_pump_state" ] = bool( row[ "feeding_pump_state" ] )
		ValuesModule._values[ "lights_state" ] = bool( row[ "lights_state" ] )
		ValuesModule._values[ "drain_pump_state" ] = bool( row[ "drain_pump_state" ] )
		ValuesModule._values[ "mixing_pump_state" ] = bool( row[ "mixing_pump_state" ] )
		ValuesModule._values[ "fan_state" ] = bool( row[ "fan_state" ] )
		ValuesModule._values[ "extractor_state" ] = bool( row[ "extractor_state" ] )
		ValuesModule._values[ "water_valve_state" ] = bool( row[ "water_valve_state" ] )
		ValuesModule._values[ "cur_water_level" ] = row[ "cur_water_level" ]
		
	def data( key =  None ):
		
		if ( key is None ):
			return ValuesModule._values
			
		return ValuesModule._values[ key ]
		
	def set( key, value , dbInsert = True ):
		
		ValuesModule._values[ key ] = value
		
		if ( dbInsert ):
			ValuesModule._connection.cursor( ).execute( "UPDATE dp SET " +  key + " = ?", ( value, ) )
			ValuesModule._connection.commit( )