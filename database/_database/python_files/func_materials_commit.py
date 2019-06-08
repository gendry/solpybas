import sqlite3

def materials_mod(self, materials_dict, function_name, conn):
	conn = conn
	x_cond_dict = materials_dict
	function_name = function_name
	
	function_name_string_length = len('materials')

	x_conds_max_id = conn.execute('SELECT max(id) FROM '+function_name+'')
	x_max_id = x_conds_max_id.fetchone()[0]
	
	#if an id exists increment it to use for later inserts or use 0 if not
	#this won't work if there is only one record i.e. returns a zero
	#convert to string to test truth value

	string_x_max_id = str(x_max_id)

	if string_x_max_id == 'None':
		x_id = 0
	else:
		x_id = x_max_id + 1

	conn.execute("INSERT INTO "+function_name+" (id) VALUES (?)", (x_id,));
	#build a search statement to use later as go through the values
	#there must be a nicer way...
	search_statement = "SELECT id FROM "+function_name+" WHERE "
	search_statement_and = ''
	search_statement_list = []

	#find the names of the columns in the table returns a list of tuples
	search_test = conn.execute("pragma table_info('"+function_name+"')");
	test = search_test.fetchall()	
	
	column_dict = {}
	
	for i in test:
		column_dict['%s' % str(i[1])] = None

	del column_dict['id']

	for key in x_cond_dict:
		answer = x_cond_dict['%s' % key]
		
		if key == 'form' or key == 'temp' or key == 'delay' or key == 'power_plasma' or key == 'time_plasma' or key == 'vac_plasma' or key == 'gas_1' or key == 'gas_2' or key == 'gas_flow_1' or key == 'gas_flow_2' or key == 'mat_id': 
			column_dict['%s' % key] = answer
		
		elif key == 'dip_agi':
			if str(answer) == 'None':
				pass
			else:
				column_dict['%s' % key] = answer
				
		elif key == 'sub_temp':
			if str(answer) == 'None':
				pass
			else:
				column_dict['%s' % key] = answer
				
		elif key == 'dip_temp':
			if str(answer) == 'None':
				pass
			else:
				column_dict['%s' % key] = answer
				
		elif key == 'dip_time':
			if str(answer) == 'None':
				pass
			else:
				column_dict['%s' % key] = answer
				
		elif key == 'dip_quan':
			if str(answer) == 'None':
				pass
			else:
				column_dict['%s' % key] = answer
				
		elif key[:12] == 'split_stack_':
			if str(answer) == 'None':
				pass
			else:
				column_dict['%s' % key] = answer
				
		elif key[:11] == 'dev_tre_met':
			if str(answer) == 'None':
				pass
			else:
				column_dict['%s' % key] = answer
		elif key[:11] == 'split_desc_':
			if str(answer) == 'None':
				pass
			else:
				column_dict['%s' % key] = answer		
		elif key[:11] == 'split_name_':
			if str(answer) == 'None':
				pass
			else:
				column_dict['%s' % key] = answer		
		elif key[:6] == 'split_':
			if str(answer) == 'None':
				pass
			else:
				column_dict['%s' % key] = answer
		elif key[:9] == 'num_devs_':
			if str(answer) == 'None':
				pass
			else:
				column_dict['%s' % key] = answer
		elif key[:8] == 'num_pix_':
			if str(answer) == 'None':
				pass
			else:
				column_dict['%s' % key] = answer
		elif key[:6] == 'yield_':
			if str(answer) == 'None':
				pass
			else:
				column_dict['%s' % key] = answer									
		elif key == 'dry_atm':
			if str(answer) == 'None':
				pass
			else:
				column_dict['%s' % key] = answer	
		elif key == 'dry_met':
			if str(answer) == 'None':
				pass
			else:
				column_dict['%s' % key] = answer		
		elif key == 'spin_atm':
			if str(answer) == 'None':
				pass
			else:
				column_dict['%s' % key] = answer	
		elif key == 'spin_coater_id':
			if str(answer) == 'None':
				pass
			else:
				column_dict['%s' % key] = answer
		elif key == 'batch_num':
			if str(answer) == 'None':
				pass
			else:
				column_dict['%s' % key] = answer		
		elif key == 'plasma_cleaner':
			if str(answer) == 'None':
				pass
			else:
				column_dict['%s' % key] = answer
		elif key == 'tre_met_id':
			if str(answer) == 'None':
				pass
			else:
				column_dict['%s' % key] = answer									
		elif key == 'units':
			column_dict['%s' % key] = answer
		elif answer == '0':
			pass
			
		elif key == 'name':
			if str(answer) == 'None':
				pass
			else:
				column_dict['%s' % key] = answer
		else:
			column_dict['%s' % key] = answer
		

	for key, value in column_dict.iteritems():
		if value == None:
			conn.execute("UPDATE "+function_name+" SET "+key+" = ? WHERE id = ?", (value, x_id,));
			search_statement_and = search_statement_and + ' AND ' + key + ' IS NULL'
		else:
			conn.execute("UPDATE "+function_name+" SET "+key+" = ? WHERE id = ?", (value, x_id,));
			search_statement_and = search_statement_and + ' AND ' + key + ' = ?'
			search_statement_list.append(value) 
	
	
	search_statement = search_statement + search_statement_and[4:]
	search_statement_list =  tuple(search_statement_list)
	search_results = conn.execute(search_statement, search_statement_list);
	result = search_results.fetchall()	
	result = [i[0] for i in result]

	if len(result) < 2:
		print "Record created successfully, id = %s" % x_id
		status = 'Record created successfully, id = %s' % x_id
	else:
		result.remove(x_id)
		print "Record already exists, id = %s" % result[0]
		status = "Record already exists, id = %s" % result[0]
		conn.execute("DELETE FROM "+function_name+" WHERE id = ?", (x_id,));
		result[0] = x_id
	conn.commit()
	#conn.close()
	return x_id, status
