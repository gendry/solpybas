import sqlite3
#This generically adds stuff to the depositions / treatments and dep_conds / treatmetn_conds tables...
def stack_update_function(self, conn, dsp_lst, stack_dict, device_stack_id):
	status = 'No status yet'
	#TABLE device_stacks (id INTEGER PRIMARY KEY, stack_name TEXT, bot_elec_pat INTEGER, top_elec_pat INTEGER)
	#TABLE device_stack_parts (id INTEGER PRIMARY KEY, device_stack_id INTEGER, stack_name TEXT, type_id INTEGER, part_id INTEGER)
			
	
	#This will be the new device_stacks_part id
	device_stacks_part_max_id = conn.execute('SELECT max(id) FROM device_stack_parts')
	device_stacks_part_max_id_result = device_stacks_part_max_id.fetchone()[0]
	
	#if an id exists increment it to use for later inserts or use 0 if not
	#this won't work if there is only one record i.e. returns a zero
	#convert to string to test truth value

	string_device_stacks_part_max_id_result = str(device_stacks_part_max_id_result)

	if string_device_stacks_part_max_id_result == 'None':
		device_stacks_part_id = 0
	else:
		device_stacks_part_id = device_stacks_part_max_id_result + 1
		
	conn.execute('UPDATE device_stacks SET top_elec_pat = ?, bot_elec_pat = ? WHERE id = ?', (stack_dict['top_elec_pat'],stack_dict['bot_elec_pat'],device_stack_id,));
	
	#The dsp_lst contains a list of dicts with the entries for the commit to dsp table
	for dsp_dict in dsp_lst:
		
		dsp_dict['device_stack_id'] = device_stack_id
		conn.execute("INSERT INTO device_stack_parts (id) VALUES (?)", (device_stacks_part_id,));
		#build a search statement to use later as go through the values
		#there must be a nicer way...
		search_statement = "SELECT id FROM device_stack_parts WHERE "
		search_statement_and = ''
		search_statement_list = []

		#find the names of the columns in the table returns a list of tuples
		search_test = conn.execute("pragma table_info('device_stack_parts')");
		test = search_test.fetchall()	
		
		column_dict = {}
		
		for i in test:
			column_dict['%s' % str(i[1])] = None

		del column_dict['id']

		for key in dsp_dict:
			answer = dsp_dict['%s' % key]
			column_dict['%s' % key] = answer
			

		for key, value in column_dict.iteritems():
			if value == None:
				conn.execute("UPDATE device_stack_parts SET "+key+" = ? WHERE id = ?", (value, device_stacks_part_id,));
				search_statement_and = search_statement_and + ' AND ' + key + ' IS NULL'
			else:
				conn.execute("UPDATE device_stack_parts SET "+key+" = ? WHERE id = ?", (value, device_stacks_part_id,));
				search_statement_and = search_statement_and + ' AND ' + key + ' = ?'
				search_statement_list.append(value) 
		
		#Dont bother checking...
		#search_statement = search_statement + search_statement_and[4:]
		#search_statement_list =  tuple(search_statement_list)
		#search_results = conn.execute(search_statement, search_statement_list);
		#result = search_results.fetchall()	
		#result = [i[0] for i in result]

		#if len(result) < 2:
		print "Record created successfully, id = %s" % device_stack_id
		status = 'Record created successfully, id = %s' % device_stack_id
		device_stacks_part_id = device_stacks_part_id+1
		#else:
			#result.remove(device_stacks_part_id)
			#print "Record already exists, id = %s" % result[0]
			#status = "Record already exists, id = %s" % result[0]
			#conn.execute("DELETE FROM device_stack_parts WHERE id = ?", (device_stacks_part_id,));
			#result[0] = device_stacks_part_id
	
	#this is a mess
	conn.commit()
	#conn.close()
	return device_stack_id, status
