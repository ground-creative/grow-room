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
		ValuesModule._values[ "airco_state" ] = bool( row[ "airco_state" ] )
		ValuesModule._values[ "cur_water_level" ] = row[ "cur_water_level" ]
		ValuesModule._values[ "in_temp" ] = 0
		ValuesModule._values[ "out_temp" ] = 0
		ValuesModule._values[ "in_hum" ] = 0
		ValuesModule._values[ "in_co2" ] = 0
		ValuesModule._values[ "water_temp" ] = 0
		ValuesModule._values[ "ph" ] = 0
		ValuesModule._values[ "ppm" ] = 0
		ValuesModule._values[ "ec" ] = 0
		ValuesModule._values[ "con_lcd" ] = bool( row[ "con_lcd" ] )
		ValuesModule._values[ "air_sen_oled" ] = bool( row[ "air_sen_oled" ] )
	def data( key =  None ):
		if ( key is None ):
			return ValuesModule._values
		return ValuesModule._values[ key ]
	def set( key, value , dbInsert = True ):
		ValuesModule._values[ key ] = value
		if ( dbInsert ):
			ValuesModule._connection.cursor( ).execute( "UPDATE dp SET " +  key + " = ?", ( value, ) )
			ValuesModule._connection.commit( )