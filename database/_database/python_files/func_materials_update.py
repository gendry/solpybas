import sqlite3

def materials_update(self, materials_dict, function_name, conn, x_id):
	conn = conn
	x_cond_dict = materials_dict
	function_name = function_name
	x_id = x_id
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
		
		if key == 'form' or key == 'temp' or key == 'delay' or key == 'power_plasma' or key == 'time_plasma' or key == 'vac_plasma' or key == 'gas_1' or key == 'gas_2' or key == 'gas_flow_1' or key == 'gas_flow_2': 
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
	
	
	#search_statement = search_statement + search_statement_and[4:]
	#search_statement_list =  tuple(search_statement_list)
	#search_results = conn.execute(search_statement, search_statement_list);
	#result = search_results.fetchall()	
	#result = [i[0] for i in result]

	
	print "Record updated successfully, id = %s" % x_id
	status = 'Record updated successfully, id = %s' % x_id
	conn.commit()
	#conn.close()
	return x_id, status
