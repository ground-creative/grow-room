#!/usr/bin/env python

class ValuesModule:
	def set_current(connection):
		ValuesModule._connection = connection
		cursor = ValuesModule._connection.cursor()
		row = ValuesModule._connection.execute("SELECT * FROM dp").fetchone()
		ValuesModule._values = {}
		ValuesModule._values["feeding_pump_state"] = bool( row["feeding_pump_state"] )
		ValuesModule._values["lights_state"] = bool( row["lights_state"] )
		ValuesModule._values["drain_pump_state"] = bool( row["drain_pump_state"] )
		ValuesModule._values["mixing_pump_state"] = bool( row["mixing_pump_state"] )
		ValuesModule._values["fan_state"] = bool( row["fan_state"] )
		ValuesModule._values["extractor_state"] = bool( row["extractor_state"] )
		ValuesModule._values["water_valve_state"] = bool( row["water_valve_state"] )
		ValuesModule._values["airco_state"] = bool( row["airco_state"] )
		ValuesModule._values["cur_water_level"] = row["cur_water_level"]
		ValuesModule._values["in_temp"] = 0
		ValuesModule._values["out_temp"] = 0
		ValuesModule._values["in_hum"] = 0
		ValuesModule._values["in_co2"] = 0
		ValuesModule._values["water_temp"] = 0
		ValuesModule._values["ph"] = 0
		ValuesModule._values["ppm"] = 0
		ValuesModule._values["ec"] = 0
		ValuesModule._values["sal"] = 0
		ValuesModule._values["con_lcd"] = bool(row["con_lcd"])
		ValuesModule._values["air_sen_oled"] = bool(row["air_sen_oled"])
		ValuesModule._values["water_tester_oled"] = bool(row["water_tester_oled"])
		ValuesModule._values["main_con_night_mode"] = bool(row["main_con_night_mode"])
		ValuesModule._values["air_sen_night_mode"] = bool(row["air_sen_night_mode"])
		ValuesModule._values["water_tester_night_mode"] = bool(row["water_tester_night_mode"])
		ValuesModule._values["doser_one_night_mode"] = bool(row["doser_one_night_mode"])
		ValuesModule._values["doser_two_night_mode"] = bool(row["doser_two_night_mode"])
		ValuesModule._values["pause_cycle"] = bool(row["pause_cycle"])
		ValuesModule._values["cycle_min_ppm"] = row["cycle_min_ppm"]
		ValuesModule._values["dose_sleep_time"] = row["dose_sleep_time"]
		ValuesModule._values["cycle_topup_value"] = row["cycle_topup_value"]
		ValuesModule._values["doser_one_pump_one_name"] = row["doser_one_pump_one_name"]
		ValuesModule._values["doser_one_pump_two_name"] = row["doser_one_pump_two_name"]
		ValuesModule._values["doser_one_pump_three_name"] = row["doser_one_pump_three_name"]
		ValuesModule._values["doser_one_pump_four_name"] = row["doser_one_pump_four_name"]
		ValuesModule._values["doser_one_pump_five_name"] = row["doser_one_pump_five_name"]
		ValuesModule._values["doser_one_pump_six_name"] = row["doser_one_pump_six_name"]
		ValuesModule._values["doser_one_pump_one_dose"] = row["doser_one_pump_one_dose"]
		ValuesModule._values["doser_one_pump_two_dose"] = row["doser_one_pump_two_dose"]
		ValuesModule._values["doser_one_pump_three_dose"] = row["doser_one_pump_three_dose"]
		ValuesModule._values["doser_one_pump_four_dose"] = row["doser_one_pump_four_dose"]
		ValuesModule._values["doser_one_pump_five_dose"] = row["doser_one_pump_five_dose"]
		ValuesModule._values["doser_one_pump_six_dose"] = row["doser_one_pump_six_dose"]
	def data(key =  None):
		if (key is None):
			return ValuesModule._values
		return ValuesModule._values[key]
	def set(key, value , dbInsert = True):
		ValuesModule._values[key] = value
		if (dbInsert):
			ValuesModule._connection.cursor().execute("UPDATE dp SET " +  key + " = ?", (value,))
			ValuesModule._connection.commit()