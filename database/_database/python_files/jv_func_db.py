####### this is for the oriel datafiles #######

import numpy
from scipy import stats
import time
import datetime
import os

def calc_jv_db(datafile, base_file_path, jv_directory_name, sub_folder, directory_name, parameters_list):
	
	#Make a dictionary to hold the things calculated
	jv_dict = {}
	base_file_path = str(base_file_path)
	directory_name = str(directory_name)
	#For each file type this will be slightly different
	#First check the file type from the folder it was in
	jv_directory_name = str(jv_directory_name)
	#So for oriel get the parameters and the voltage and current data
	
	#Get the short filename from the file being worked on
	#file_name = datafile[-37:]
	file_name = os.path.basename(datafile)
	#datafile_name = datafile[-46:]
	#This should give us the filename minus the base path which is variable
	datafile_name = datafile[len(base_file_path):]
	
	jv_directory_sub_folder = sub_folder[len(jv_directory_name):]
	
	if jv_directory_sub_folder == "oriel_jvs":	
		light_source = 'Oriel PVLab'
		file_type = 'Oriel'
		#Get the scan settings from the file this is the 4th row of the data file 
		#genfrom txt will raise and exception if the number of columns in each row is not equal to the first read.
		#Tell it to ignor this with  invalid_raise=False
		#It will still print a complaint.
		#Only interested in the first row anyway
		scan_settings = numpy.genfromtxt(datafile, skip_header=4, delimiter='\t', dtype=float, invalid_raise=False, encoding='latin1')
		scan_settings_2 = numpy.genfromtxt(datafile, skip_header=7, delimiter='\t', dtype=float, invalid_raise=False, encoding='latin1')
		#the cell area in cm2 is in the first column
		cell_area_cm = scan_settings[0]
		masked_cell_area = 0.0
		
		masked_by_full_area = masked_cell_area / cell_area_cm 
		#convert cell area to m2
		cell_area_meter = cell_area_cm / 10000.0
		#the irradience is in the second column convert to wm2
		pin = ((scan_settings[1])*1000.00)
		##### Calculate a sun equivalents ### As this is for Oriel its easy and a bit pointless
		sun_equiv = pin / 1000	
		#### For Oriel there is no simple way to know if its a dark scan...
		### This might work
		if pin == 0:
			dark_light = 0
			lux = 0.0
			soak_suns = 0.0
		else:
			dark_light = 1	
			lux = 100000
			soak_suns = sun_equiv
		
		#get the pre-sweep delay
		pre_sweep_delay = scan_settings[2]
		soak_time = scan_settings[2]
		
		temperature = 24.0
		
		#get the number of scan points
		num_sweep_points = scan_settings[6]
		#and the dwell
		dwell_time = scan_settings[7]
		### max reverse bias (do these swap round in the software?)
		min_bias = scan_settings[4]
		## max forward bias 
		max_bias = scan_settings[5]
		
		### exposure time ####
		total_exposure_time = scan_settings_2[14]
		##### scan rate, this may not be accurate ######
		#### Get the exposure time and the min and max voltage and pre-sweep delay
		scan_time = total_exposure_time - pre_sweep_delay
		scan_range = max_bias - min_bias
		scan_rate = scan_range / scan_time
		#Get the device batch, split, device and pixel from the file_name
		batch = file_name[1:4]
		split = file_name[5:7]
		device = file_name[8:10]
		pixel = file_name[11:13]
		
		if check_device_name(batch,split,device,pixel) == False:
			print 'Failed to import due to file name error!'
		else:
			#get the time of scan from the file_name and convert to a timestamp
			second = file_name[-6:-4]
			minute = file_name[-9:-7]
			hour = file_name[-12:-10]
			day = file_name[-15:-13]
			month = file_name[-18:-16]
			year = file_name[-23:-19]
			#This should be unix time
			time_stamp = time.mktime(datetime.datetime.strptime(('%s%s%s%s%s%s' % (second, minute, hour, day, month, year)), "%S%M%H%d%m%Y").timetuple())
			#create a time stamp from the date and time given in the scan settings
			other_scan_settings = numpy.genfromtxt(datafile, skip_header=8, delimiter='\t', dtype=str, invalid_raise=False, encoding='latin1')
			scan_time = other_scan_settings[15]

			#Now get the voltage and current
			all_data = numpy.genfromtxt(datafile, skip_header=10, delimiter='\t', dtype=float, encoding='latin1')

			voltage_points = all_data[:,0]
			current_points = all_data[:,1]
			jv_dict = calculate_jv_parameters(jv_dict, current_points, voltage_points, file_name, cell_area_meter, cell_area_cm, pin, dwell_time, pre_sweep_delay, num_sweep_points, batch, split, device, pixel, time_stamp, light_source, dark_light, scan_rate, sun_equiv, datafile_name, soak_time, soak_suns, lux, temperature, file_type, masked_cell_area, masked_by_full_area)
			return jv_dict
		
	elif jv_directory_sub_folder == "swansea_jvs":
		light_source = 'Swansea PVLab'
		file_type = 'Swansea'
		#Files may change and be inconsistent at any time depending on the software version and computer installed on!!!!
		#Welcome to hell...
		scan_settings = numpy.genfromtxt(datafile, skip_header=4, delimiter='\t', dtype=float, invalid_raise=False, encoding='latin1')
		scan_settings_2 = numpy.genfromtxt(datafile, skip_header=7, delimiter='\t', dtype=float, invalid_raise=False, encoding='latin1')
		#the cell area in cm2 is in the first column
		cell_area_cm = float(scan_settings[0])
		masked_cell_area = 0.0
		
		masked_by_full_area = masked_cell_area / cell_area_cm 
		#convert cell area to m2
		cell_area_meter = cell_area_cm / 10000.0
		#the irradience is in the second column convert to wm2
		pin = ((scan_settings[1])*1000.00)
		sun_equiv = pin / 1000	
		if pin == 0:
			dark_light = 0
			lux = 0.0
			soak_suns = 0.0
		else:
			dark_light = 1
			soak_suns = sun_equiv
			lux = 100000

		#get the pre-sweep delay
		pre_sweep_delay = scan_settings[2]
		soak_time = pre_sweep_delay
		#get the number of scan points
		num_sweep_points = scan_settings[8]
		#and the dwell
		dwell_time = scan_settings[11]
		temperature = 24.0
		### max reverse bias (do these swap round in the software?)
		start_bias = scan_settings[5]
		## max forward bias 
		end_bias = scan_settings[6]
		min_bias = min([start_bias, end_bias])
		max_bias = max([start_bias, end_bias])
		### exposure time ####
		total_exposure_time = scan_settings_2[12]
		##### scan rate, this may not be accurate ######
		#### Get the exposure time and the min and max voltage and pre-sweep delay
		scan_time = total_exposure_time - pre_sweep_delay
		scan_range = max_bias - min_bias
		scan_rate = scan_range / scan_time
		#Get the device batch, split, device and pixel from the file_name
		#e.g. 'B111S00D00P00-000-2016-15-12 145537.IV'
		#The dates are year day month... 
		#The files might not keep consistent types...
		batch = file_name[1:4]
		split = file_name[5:7]
		device = file_name[8:10]
		pixel = file_name[11:13]
		
		if check_device_name(batch,split,device,pixel) == False:
			print 'Failed to import due to file name error!'
		else:
			#get the time of scan from the file_name and convert to a timestamp
			second = file_name[-5:-3]
			minute = file_name[-7:-5]
			hour = file_name[-9:-7]
			month = file_name[-12:-10]
			day = file_name[-15:-13]
			year = file_name[-20:-16]
			
			time_stamp = time.mktime(datetime.datetime.strptime(('%s%s%s%s%s%s' % (second, minute, hour, day, month, year)), "%S%M%H%d%m%Y").timetuple())
			#create a time stamp from the date and time given in the scan settings
			other_scan_settings = numpy.genfromtxt(datafile, skip_header=8, delimiter='\t', dtype=str, invalid_raise=False, encoding='latin1')
			scan_time = hour + ":" + minute + ":" + second

			#Now get the voltage and current
			all_data = numpy.genfromtxt(datafile, skip_header=10, delimiter='\t', dtype=float, encoding='latin1')

			voltage_points = all_data[:,0]
			#in mA
			current_points = all_data[:,2]
			#Convert to Amps
			current_points = current_points / 1000.0
			jv_dict = calculate_jv_parameters(jv_dict, current_points, voltage_points, file_name, cell_area_meter, cell_area_cm, pin, dwell_time, pre_sweep_delay, num_sweep_points, batch, split, device, pixel, time_stamp, light_source, dark_light, scan_rate, sun_equiv, datafile_name, soak_time, soak_suns, lux, temperature, file_type, masked_cell_area, masked_by_full_area)
			return jv_dict	
		
	elif jv_directory_sub_folder == "tpv2_jvs":
		
		file_type = 'TPV2'
		#find the datafile and corresponding status file
		file_sort = file_name[-35:-27]
	
		if file_sort != "datafile":
			pass
		else:
			#if it is a datafile find the matching status file and extract the scan conditions
			all_data = numpy.genfromtxt(datafile, skip_header=1, delimiter='\t', dtype=float, encoding='latin1')
			voltage_points = all_data[:,0]
			current_points = all_data[:,1]
			num_sweep_points = len(current_points)
			#find status file
			status_file_name = datafile[:-35] + "statusfile" + datafile[-27:]
		
			
			scan_settings = numpy.genfromtxt(status_file_name, delimiter='\t', dtype=None, invalid_raise=False, encoding='latin1')
			cell_area_cm = float(scan_settings[1][1])
			total_cell_area = float(scan_settings[22][1])
			masked_cell_area = total_cell_area - cell_area_cm
			cell_area_meter = cell_area_cm / 10000.0
			
			masked_by_full_area = masked_cell_area / cell_area_cm 
			
			temperature = float(scan_settings[4][1])
			#scan_temp_deg_c = scan_settings[5][1]
			light_source = scan_settings[20][1]
			if scan_settings[15][1]:
				sun_equiv = float(scan_settings[15][1])
			else:
				sun_equiv = 0.0
			
			#Iradiance by sun equivalents times 1000W/m2 
			pin = sun_equiv * 1000.0
			
			if scan_settings[6][1] == 0.0:
				dark_light = 0
				lux = 0.0	
			else:
				dark_light = 1	
				if not scan_settings[19][1]:
					lux = 100000.0
				else:
					lux = scan_settings[19][1]
			if not scan_settings[14][1]:
				soak_suns = sun_equiv
			else:
				soak_suns = scan_settings[14][1]
			#get the pre-sweep delay
			pre_sweep_delay = float(scan_settings[16][1])
			soak_time = pre_sweep_delay
			scan_rate = float(scan_settings[3][1])
			#This needs sorting
			dwell_time = 0
			
			#this should be done from a unix time stamp really
			time_string = scan_settings[2][1]
			year = time_string[:4]
			month = time_string[4:6]
			day = time_string[6:8]
			hour = time_string[8:10]
			minute = time_string[10:12]
			second = time_string[12:14]
			
			time_stamp = time.mktime(datetime.datetime.strptime(('%s%s%s%s%s%s' % (second, minute, hour, day, month, year)), "%S%M%H%d%m%Y").timetuple())
			
			#batch_sting = scan_settings[0][1]
			#batch = batch_sting[1:4]
			#split = batch_sting[5:7]
			#device = batch_sting[8:10]
			#pixel = batch_sting[11:13]
			
			batch = file_name[1:4]
			split = file_name[5:7]
			device = file_name[8:10]
			pixel = file_name[11:13]
			if check_device_name(batch,split,device,pixel) == False:
				print 'Failed to import due to file name error!'
			else:
				jv_dict = calculate_jv_parameters(jv_dict, current_points, voltage_points, file_name, cell_area_meter, cell_area_cm, pin, dwell_time, pre_sweep_delay, num_sweep_points, batch, split, device, pixel, time_stamp, light_source, dark_light, scan_rate, sun_equiv, datafile_name, soak_time, soak_suns, lux, temperature, file_type, masked_cell_area, masked_by_full_area)
				return jv_dict
			
	elif jv_directory_sub_folder == "mgr_jvs":
		
		file_type = 'mgr'
		#find the datafile and corresponding status file
		file_sort = file_name[-8:-4]
		
		if file_sort == "data":
			pass
		else:
			#only the light scan files have a scan parameters status data file, which makes things difficult
			#find if it is a dark or light file
			if file_name[-14:-10] == "Dark":
				dark_light = 0
			else:
				dark_light = 1	
			#if it is a datafile find the matching status file and extract the scan conditions
			all_data = numpy.genfromtxt(datafile, skip_header=1, delimiter='\t', dtype=float, encoding='latin1')
			voltage_points = all_data[:,0]
			current_points = all_data[:,1]
			pin = ((scan_settings[1][1])*10.00)
			##### Calculate a sun equivalents ### As this is for Oriel its easy and a bit pointless
			sun_equiv = pin / 1000	
			#if it is a light file there is a status data file
			if dark_light == 1:
				lux = 100000.0
				soak_suns = sun_equiv
				#find status file this includes the scan
				status_file_name = file_name[:-4] + "_data" + file_name[-4:]
			else:
				#Only look for the 1 sun and assume the scan settings are the same. MGR not good for this
				status_file_name = file_name[:-14] + "100" + file_name[-10:-4] + "_data.txt"
				lux = 0.0
				soak_suns = 0.0
				
			scan_settings = numpy.genfromtxt(status_file_name, delimiter='\t', dtype=None, invalid_raise=False, encoding='latin1')
			scan_settings2 = numpy.genfromtxt(status_file_name, skip_header=9, delimiter='\t', dtype=None, invalid_raise=False, encoding='latin1')
			scan_settings2 = str(scan_settings2)
			
			cell_area_cm = float(scan_settings[0][1])
			masked_cell_area = 0.0
			
			masked_by_full_area = masked_cell_area / cell_area_cm 
			
			cell_area_meter = cell_area_cm / 10000.0
			soak_time = 0.0
			light_source = 'MGR Solar Simulator'
			temperature = scan_settings[3][3]
			
			
			#no way of knowing how much light soaking was used by mgr
			pre_sweep_delay = 0
			#get the number of scan points
			num_sweep_points = len(current_points)
			#and the dwell
			dwell_time = scan_settings[7]
			### max reverse bias 
			start_bias = voltage_points[0]
			## max forward bias 
			end_bias = scan_settings[-1]
			min_bias = min([start_bias, end_bias])
			max_bias = max([start_bias, end_bias])
			### exposure time, mgr doesn't give this ####
			total_exposure_time = scan_settings2[48:-1]
			##### scan rate, this may not be accurate ######
			#mgr scan rate isn't obvious
			scan_time = scan_settings2[48:-1]
			scan_range = max_bias - min_bias
			scan_rate = scan_range / scan_time
			#Get the device batch, split, device and pixel from the file_name
			batch = status_file_name[-31:-27]
			split = file_name[-25:-23]
			device = file_name[-21:-19]
			pixel = file_name[-14:13]
			if check_device_name(batch,split,device,pixel) == False:
				print 'Failed to import due to file name error!'
			else:
				scan_time_stamp = scan_settings[1][3]
				
				#This is a total pain for mgr files. Use the time stamp
				#labview time stamp... 
				labview_stamp = scan_settings[2][3]
				#to get to unix time stamp add 2082844800
				unix_stamp = labview_stamp - 2082844800
				
				second = (datetime.datetime.fromtimestamp(int(unix_stamp)).strftime('%S'))
				minute = (datetime.datetime.fromtimestamp(int(unix_stamp)).strftime('%M'))
				hour = (datetime.datetime.fromtimestamp(int(unix_stamp)).strftime('%H'))
				day = (datetime.datetime.fromtimestamp(int(unix_stamp)).strftime('%d'))
				month = (datetime.datetime.fromtimestamp(int(unix_stamp)).strftime('%m'))
				year = (datetime.datetime.fromtimestamp(int(unix_stamp)).strftime('%Y'))
				#Blah!!!!
				time_stamp = time.mktime(datetime.datetime.strptime(('%s%s%s%s%s%s' % (second, minute, hour, day, month, year)), "%S%M%H%d%m%Y").timetuple())
				#create a time stamp from the date and time given in the scan settings
				other_scan_settings = numpy.genfromtxt(datafile, skip_header=8, delimiter='\t', dtype=str, invalid_raise=False, encoding='latin1')
				
				scan_time = scan_settings[1][3]

				#Now get the voltage and current
				all_data = numpy.genfromtxt(datafile, skip_header=10, delimiter='\t', dtype=float, encoding='latin1')

				voltage_points = all_data[:,0]
				#in mA
				current_points = all_data[:,1]
				#Convert to Amps
				current_points = current_points / 1000.0
				jv_dict = calculate_jv_parameters(jv_dict, current_points, voltage_points, file_name, cell_area_meter, cell_area_cm, pin, dwell_time, pre_sweep_delay, num_sweep_points, batch, split, device, pixel, time_stamp, light_source, dark_light, scan_rate, sun_equiv, datafile_name, soak_time, soak_suns, lux, temperature, file_type, masked_cell_area, masked_by_full_area)
				return jv_dict	
	
def check_device_name(batch,split,device,pixel):
	#Check that the batch, split, device, pixels are actually numbers
	if batch.isdigit() and len(batch) == 3 and split.isdigit() and len(split) == 2 and device.isdigit() and len(device) == 2 and pixel.isdigit() and len(pixel) == 2:
		return True
	else:
		return False
		
def calculate_jv_parameters(jv_dict, current_points, voltage_points, file_name, cell_area_meter, cell_area_cm, pin, dwell_time, pre_sweep_delay, num_sweep_points, batch, split, device, pixel, time_stamp, light_source, dark_light, scan_rate, sun_equiv, datafile_name, soak_time, soak_suns, lux, temperature, file_type, masked_cell_area, masked_by_full_area):
	#make and array of jsc values from the cell area in cm and the current array multiply each by 1000 to get mA
	current_density_points = numpy.divide(numpy.multiply(current_points, 1000), cell_area_cm)

	#isc or jsc where curve V = 0
	#the interp function will only work if the first set of points is increasing
	#check for this and reverse arrays (and then change the sign if needed?) or for a flat line give an error and skip
	#this is fine for a standard -1 to +1 voltage sweep but won't work for a cyclic sweep need modified routine for that
	is_vol_increasing = numpy.average(numpy.diff(voltage_points))
	#Check if that is true or not
	if is_vol_increasing > 0:
		isc = (numpy.interp(0, voltage_points, current_points))
		#this is a waste as its just isc/cell_area_cm
		jsc = (numpy.interp(0, voltage_points, current_density_points))
	else:
		#check if its decreasing if it isn't increasing
		if is_vol_increasing < 0:
			#if it is decreasing reverse the arrays and then find the points
			voltage_points_rev = voltage_points[::-1]
			current_points_rev = current_points[::-1]
			current_density_points_rev = current_density_points[::-1]
			isc = (numpy.interp(0, voltage_points_rev, current_points_rev))
			jsc = (numpy.interp(0, voltage_points_rev, current_density_points_rev))
		else:
			#if it isn't increasing and it isn't decreasing its probably flat so just give it some zeros and see what happens.
			isc = 0
			jsc = 0
			
	#voc where curve  I = 0
	#this is not as simple as for voltage as some points may increase whilst others decrease
	is_cur_increasing = numpy.average(numpy.diff(current_points))
	#Check if that is true or not
	if is_cur_increasing > 0:
		voc = (numpy.interp(0, current_points, voltage_points))
	else:
		#check if its decreasing if it isn't increasing
		if is_cur_increasing < 0:
			#if it is decreasing reverse the arrays and then find the points
			voltage_points_rev2 = voltage_points[::-1]
			current_points_rev2 = current_points[::-1]
			voc = (numpy.interp(0, current_points_rev2, voltage_points_rev2))
		else:
			#if it isn't increasing and it isn't decreasing its probably flat so just give it some zeros and see what happens.
			voc = 0.

	#If voc is zero the cell is most likely short and can be excluded and the later calculations skipped as they will not work with 0
	if voc == 0.:
		pass	

	else:
		#Find the Rsh from the gradient around 0V e.g. from -0.2 to 0.2V
		#Wont always have points at -0.2 and 0.2 so find the index of the values closest to these
		#Not sure how this method came about, it works by adding on the value to the list so that the value close to this e.g. -0.202 becomes 0.02 and then making abs and finding the index of the minimum which should be zero...
		idx = (numpy.abs(voltage_points--0.2)).argmin()
		idx2 = (numpy.abs(voltage_points-0.2)).argmin()

		#Depending on if it is a forward or reverse scan will mean the arrays are going in opposite directions
		#so need to swap where calculate between denpending on this
		if numpy.any(current_points[idx2:idx]):	
		#Get the gradient of the line between these points
			slope_rsh, intercept_rsh, r_value_rsh, p_value_rsh, std_err_rsh = stats.linregress(voltage_points[idx2:idx],current_points[idx2:idx])
			#Rsh is equal to the inverse of the slope, make it Ohms.cm2
			rsh = 1/(abs(slope_rsh)/cell_area_cm)
	
		elif numpy.any(current_points[idx:idx2]):
			#Get the gradient of the line between these points
			slope_rsh, intercept_rsh, r_value_rsh, p_value_rsh, std_err_rsh = stats.linregress(voltage_points[idx:idx2],current_points[idx:idx2])
			#Rsh is equal to the inverse of the slope, make it Ohms.cm2
			rsh = 1/(abs(slope_rsh)/cell_area_cm)
		

		else:
			rsh = 0
	
		#Find the Rs from the gradient around 0A e.g. from -0.0005 to 0.0005A
		#Is this really the best place to find the Rs
		#Wont always have points at -0.0005 and 0.0005 so find the index of the values closest to these
		#this is all funny because current is going towards neg????
		#For larger area cells e.g. 1cm2 with a fast scan rate this needs modification...
		#idxI = (numpy.abs(current_points--0.0005)).argmin()
		#idxI2 = (numpy.abs(current_points-0.0005)).argmin()	
		#Could simply find the min value and chose the point either side of this instead...
		idxI = (numpy.abs(current_points--0.0005)).argmin()
		#And check not at ends of array
		if idxI == len(current_points)-1:
			idxI2 = idxI-2
		elif idxI == 0:
			idxI2 = 2
		#Expand around the original value
		else:
			idxI2 = idxI+1
			idxI = idxI-1	
		
			
		if numpy.any(current_points[idxI:idxI2]):
			#print current_points[idxI:idxI2]
			#Get the gradient of the line between these points
			slope_rs, intercept_rs, r_value_rs, p_value_rs, std_err_rs = stats.linregress(voltage_points[idxI:idxI2], current_points[idxI:idxI2])
			#Rs is equal to the inverse of the slope, make it Ohms.cm2
			rs = 1./(abs(slope_rs)/cell_area_cm)
			#print cell_area_cm
			#print slope_rs
			#print rs
		elif numpy.any(current_points[idxI2:idxI]):
			print 'here'
			#print current_points[idxI:idxI2]
			#Get the gradient of the line between these points
			slope_rs, intercept_rs, r_value_rs, p_value_rs, std_err_rs = stats.linregress(voltage_points[idxI2:idxI], current_points[idxI2:idxI])
			#Rs is equal to the inverse of the slope, make it Ohms.cm2
			rs = 1./(abs(slope_rs)/cell_area_cm)
			#print cell_area_cm
			#print slope_rs
			#print rs
		else:
			print 'No!'
			rs = 0
	
		#Find the max power point P=IV max 
		#Just look at the curve between isc and voc and find max V and I
		#If voc is neg or voc is pos need to change the > < used
		if voc > 0:
			i_quad = current_points[(voltage_points>0) & (voltage_points<voc)]
			v_quad = voltage_points[(voltage_points>0) & (voltage_points<voc)]
			j_quad = current_density_points[(voltage_points>0) & (voltage_points<voc)]
		elif voc < 0:
			i_quad = current_points[(voltage_points<0) & (voltage_points>voc)]
			v_quad = voltage_points[(voltage_points<0) & (voltage_points>voc)]
			j_quad = current_density_points[(voltage_points<0) & (voltage_points>voc)]
		else:
			i_quad = numpy.asarray([0.,])
			v_quad = numpy.asarray([0.,])
			j_quad = numpy.asarray([0.,])

		#multiply the current and voltage points to get powers 
		powers = (i_quad*v_quad)
		powersj = (j_quad*v_quad)
		#from the powers find the max power point
		#get the array as positive values so can find the max
		#Should always be making power so should be given as positive anyway...???
		powers_pos = numpy.fabs(powers)
		powersj_pos = numpy.fabs(powersj)
		powers_pos
			
		try:
			pmax = numpy.amax(powers_pos)
			#Find Vmax and Imax
			vmax = v_quad[numpy.argmax(powers_pos)]
			imax = i_quad[numpy.argmax(powers_pos)]
		except ValueError:	
			pmax = 0.
			vmax = 0.
			imax = 0.
			
		try:
			mpd = numpy.amax(powersj_pos)
			jmax = j_quad[numpy.argmax(powersj_pos)]
		except ValueError:
			mpd = 0
			jmax = 0
			

		if voc < 0:
			vmax = vmax * -1
			
		if isc < 0:
			imax = imax * -1
			jmax = jmax * -1

		#Calculate the Fill Factor from Pmax/(Isc*Voc) *100 for %
		theopmax = ((numpy.sqrt(numpy.square(isc*voc))))
		if theopmax == 0:
			ff = 0
			ffperc = 0
		else:	
			ff = pmax/theopmax
			ffperc = ff*100

		# calculate the PCE for the cell. Multiply by 100 for percentage.
		if pin == 0:
			pce = 0
		else:
			pce = (pmax/(pin*cell_area_meter))*100

		#A list of the parameters calculated
		parameters = [pce, voc, isc, jsc, ffperc, mpd, vmax, imax, jmax, pmax, rs, rsh]

		#Work out what type of scan it was and add the parameters to a list to plot for each split
		#Average over a few points as SMU current limit can sometimes mean applied voltage is read multiple times and not the attempted voltage
		#Seems to work ok....
		#Anode and cathode have to be connected up to red/black correct way depending on cell architecture...
		#Wouldn't work for uneven voltage steps?
		half = int(len(voltage_points))/2
		
		if numpy.sum(voltage_points[0:half]) < numpy.sum(voltage_points[half:-1]):
			scan_type = "forward"
			
		else:
			scan_type = "reverse"
	
		#add the splits dict to the jv_dict to be returned
		jv_dict['scan_type'] = scan_type
		jv_dict['file_name'] = file_name
		jv_dict['cell_area_cm'] = cell_area_cm
		jv_dict['pin'] = pin
		jv_dict['parameters'] = parameters
		jv_dict['dwell_time'] = dwell_time
		jv_dict['pre_sweep_delay'] = pre_sweep_delay
		jv_dict['num_sweep_points'] = num_sweep_points
		jv_dict['batch'] = batch
		jv_dict['split'] = split
		jv_dict['device'] = device
		jv_dict['pixel'] = pixel
		jv_dict['time_stamp'] = time_stamp
		jv_dict['light_source'] = light_source
		jv_dict['dark_light'] = dark_light
		jv_dict['scan_rate'] = scan_rate
		jv_dict['sun_equiv'] = sun_equiv
		jv_dict['datafile'] = datafile_name
		jv_dict['soak_time'] = soak_time
		jv_dict['soak_suns'] = soak_suns
		jv_dict['lux'] = lux
		jv_dict['temperature'] = temperature
		jv_dict['file_type'] = file_type
		jv_dict['masked_cell_area'] = masked_cell_area
		jv_dict['masked_by_full_area'] = masked_by_full_area
		return jv_dict
