import sqlite3
#This generically adds stuff to the depositions / treatments and dep_conds / treatmetn_conds tables...
def batch_commit_function(self, conn, splits_lst, batch_dict):
	status = 'No status yet'
	#TABLE device_stacks (id INTEGER PRIMARY KEY, stack_name TEXT, bot_elec_pat INTEGER, top_elec_pat INTEGER)
	#TABLE device_stack_parts (id INTEGER PRIMARY KEY, device_stack_id INTEGER, stack_name TEXT, type_id INTEGER, part_id INTEGER)
			
	#Get the next row id from the device_batches table
	#This will be batch_id
	device_batches_id_max = conn.execute('SELECT max(id) FROM device_batches')
	device_batches_id_max_result = device_batches_id_max.fetchone()[0]
	
	#if an id exists increment it to use for later inserts or use 0 if not
	#this won't work if there is only one record i.e. returns a zero
	#convert to string to test truth value

	string_device_batches_id_max_result = str(device_batches_id_max_result)

	if string_device_batches_id_max_result == 'None':
		device_batches_id = 0
	else:
		device_batches_id = device_batches_id_max_result + 1
	
	
	#This will be the splits id
	splits_max_id = conn.execute('SELECT max(id) FROM device_stack_parts')
	splits_max_id_result = splits_max_id.fetchone()[0]
	
	#if an id exists increment it to use for later inserts or use 0 if not
	#this won't work if there is only one record i.e. returns a zero
	#convert to string to test truth value

	string_splits_max_id_result = str(splits_max_id_result)

	if string_splits_max_id_result == 'None':
		splits_id = 0
	else:
		splits_id = splits_max_id_result + 1
		
	conn.execute('INSERT INTO device_batches (id, batch_num, batch_name, batch_desc, batch_notes, owner) VALUES (?,?,?,?,?,?)', (device_batches_id,batch_dict['batch_num'],batch_dict['batch_name'],batch_dict['batch_desc'],batch_dict['batch_notes'],batch_dict['owner'],));
	
	#The dsp_lst contains a list of dicts with the entries for the commit to dsp table
	for split_dict in splits_lst:
		
		split_dict['batch_id'] = device_batches_id
		conn.execute("INSERT INTO splits (id) VALUES (?)", (splits_id,));
		#build a search statement to use later as go through the values
		#there must be a nicer way...
		search_statement = "SELECT id FROM splits WHERE "
		search_statement_and = ''
		search_statement_list = []

		#find the names of the columns in the table returns a list of tuples
		search_test = conn.execute("pragma table_info('splits')");
		test = search_test.fetchall()	
		
		column_dict = {}
		
		for i in test:
			column_dict['%s' % str(i[1])] = None

		del column_dict['id']

		for key in split_dict:
			answer = split_dict['%s' % key]
			column_dict['%s' % key] = answer
			

		for key, value in column_dict.iteritems():
			if value == None:
				conn.execute("UPDATE splits SET "+key+" = ? WHERE id = ?", (value, splits_id,));
				search_statement_and = search_statement_and + ' AND ' + key + ' IS NULL'
			else:
				conn.execute("UPDATE splits SET "+key+" = ? WHERE id = ?", (value, splits_id,));
				search_statement_and = search_statement_and + ' AND ' + key + ' = ?'
				search_statement_list.append(value) 
		
		#Dont bother checking...
		#search_statement = search_statement + search_statement_and[4:]
		#search_statement_list =  tuple(search_statement_list)
		#search_results = conn.execute(search_statement, search_statement_list);
		#result = search_results.fetchall()	
		#result = [i[0] for i in result]

		#if len(result) < 2:
		print "Record created successfully, id = %s" % splits_id
		status = 'Record created successfully, id = %s' % device_batches_id
		splits_id = splits_id+1
		#else:
			#result.remove(device_stacks_part_id)
			#print "Record already exists, id = %s" % result[0]
			#status = "Record already exists, id = %s" % result[0]
			#conn.execute("DELETE FROM device_stack_parts WHERE id = ?", (device_stacks_part_id,));
			#result[0] = device_stacks_part_id
	
	#this is a mess
	conn.commit()
	#conn.close()
	return device_batches_id, status
