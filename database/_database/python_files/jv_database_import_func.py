####This will make a basic IV plot from a single data file with columns of voltage, current and current density
import numpy
from scipy import stats
import os
import time
import datetime
from jv_func_db import calc_jv_db	
import sqlite3

 
def import_batch_data(self, conn, batch_num, base_file_path):
	#make some dictionaries to hold the values for each parameter, need for both forward and reverse curves
	parameters_list = ['PCE', 'Voc', 'Isc', 'Jsc', 'FF', 'MPD', 'Vmax', 'Imax', 'Jmax', 'Pmax', 'Rs', 'Rsh']

	conn = conn
	batch_num = batch_num
	base_file_path = base_file_path
	#### Batch num is an integer of 1 to 3 characters long but the folder name is BXXX
	batch_fol = 'B%03d' % batch_num
	batch_folder_name = str(base_file_path) + batch_fol
	#JV scans sub folder
	jv_directory_name = str(batch_folder_name) +"/jv_data/"
	#JV rig name folder
	list_jv_sub_folders = []
	
	oriel_directory_name = str(jv_directory_name) + "oriel_jvs" 
	tpv2_directory_name = str(jv_directory_name) + "tpv2_jvs" 
	swansea_directory_name = str(jv_directory_name) + "swansea_jvs" 
	mgr_directory_name = str(jv_directory_name) + "mgr_jvs" 
	
	list_jv_sub_folders.append(oriel_directory_name)
	list_jv_sub_folders.append(tpv2_directory_name)
	list_jv_sub_folders.append(swansea_directory_name)
	list_jv_sub_folders.append(mgr_directory_name) 
	
	#find the maximum device id
	dev_select_max_id = conn.execute('SELECT max(id) FROM dev_ids')
	dev_max_id = dev_select_max_id.fetchone()[0]
	#if an id exists increment it to use for later inserts or use 0 if not
	#this won't work if there is only one record i.e. returns a zero
	#convert to string to test truth value
	string_dev_max_id = str(dev_max_id)
	
	if string_dev_max_id == 'None':
		dev_max_id = 0
	else:
		dev_max_id = dev_max_id + 1

	#find the maximum scan id
	jv_select_max_id = conn.execute('SELECT max(id) FROM jv_scan_results')
	jv_max_id = jv_select_max_id.fetchone()[0]

	if not jv_max_id:
		jv_max_id = 0
	else:
		jv_max_id = jv_max_id + 1
	for sub_folder in list_jv_sub_folders:
		
		for root, dirs, files in os.walk(sub_folder):
			
			dirs.sort()	
			#for each folder in the sub jv folder get the .txt files to work on. 
			for directory in dirs:
				
				#to build the file path
				directory_name = ("%s/%s" % (sub_folder, directory))
				
				datafiles = []
				
				for datafile in os.listdir(directory_name):
					if datafile.endswith(".txt"):
						datafiles.append("%s/%s" % (directory_name, datafile))
					elif datafile.endswith(".IV"):
						datafiles.append("%s/%s" % (directory_name, datafile))	
				#For each .txt found in the jv sub folder pass the file name to the jv calc function and work on it			
				
				for datafile in datafiles:
					#print datafile
					jv_dict = calc_jv_db(datafile, base_file_path, jv_directory_name, sub_folder, directory_name, parameters_list)
					if jv_dict:
						#check if the device matches and device ids and use that id if it does. If not create a new id. 
						select_dev_id = conn.execute('SELECT id, batch, split, device, pixel FROM dev_ids WHERE batch=? AND split=? AND device=? AND pixel=?', (jv_dict['batch'], jv_dict['split'], jv_dict['device'], jv_dict['pixel']));
						
						all_dev_ids = select_dev_id.fetchall()
						if not all_dev_ids:
							dev_id = dev_max_id
							
							dev_max_id = dev_max_id +1
							#add the devices to the database
							conn.execute("INSERT INTO dev_ids (id, batch, split, device, pixel) VALUES (?,?,?,?,?)", (dev_id, jv_dict['batch'], jv_dict['split'], jv_dict['device'], jv_dict['pixel'])); 
							
						else:
							
							dev_id = all_dev_ids[0][0]
							 

						#check if the scan already exists in the database table using the timestamp value (should always be unique).
						select_device_scan = conn.execute('SELECT id, time_stamp, dev_id FROM jv_scan_results WHERE dev_id=?', (dev_id,));

						all_device_scans = select_device_scan.fetchall()
						match = [item for item in all_device_scans if jv_dict['time_stamp'] in item]
						if match:
							pass
						else:	
							#insert the values calculated into the database table jv_scan_results
							conn.execute("INSERT INTO jv_scan_results (id, time_stamp, dev_id, scan_type, pce, voc, isc, jsc, ff, mpd, vmax, imax, jmax, pmax, rs, rsh, cell_area, irradiance, pre_sweep_delay, num_sweep_points, dwell_time, light_source, dark_light, scan_rate, sun_equiv, datafile, soak_time, soak_suns, lux, temperature, file_type, masked_area, masked_by_full_area) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (jv_max_id, jv_dict['time_stamp'], dev_id, jv_dict['scan_type'], jv_dict['parameters'][0], jv_dict['parameters'][1], jv_dict['parameters'][2], jv_dict['parameters'][3], jv_dict['parameters'][4], jv_dict['parameters'][5], jv_dict['parameters'][6], jv_dict['parameters'][7], jv_dict['parameters'][8], jv_dict['parameters'][9], jv_dict['parameters'][10], jv_dict['parameters'][11], jv_dict['cell_area_cm'], jv_dict['pin'], jv_dict['pre_sweep_delay'], jv_dict['num_sweep_points'], jv_dict['dwell_time'],jv_dict['light_source'],jv_dict['dark_light'],jv_dict['scan_rate'],jv_dict['sun_equiv'],jv_dict['datafile'],jv_dict['soak_time'],jv_dict['soak_suns'],jv_dict['lux'],jv_dict['temperature'],jv_dict['file_type'],jv_dict['masked_cell_area'],jv_dict['masked_by_full_area'],));
							jv_max_id = jv_max_id + 1
							

					else:
						pass					


	conn.commit()
	print "Records created successfully"
	
