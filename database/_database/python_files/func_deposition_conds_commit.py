import sqlite3
#This generically adds stuff to the depositions / treatments and dep_conds / treatmetn_conds tables...
def dep_conds_mod(self, cond_lst, dep_met_id_select_result, function_name, conn, other_col, other_table, method_col, conds_col, name_col, name):
	conn = conn
	dep_met_id_select_result = dep_met_id_select_result
	cond_lst = cond_lst
	#Don't think this is needed
	function_name = function_name
	other_table = other_table
	other_col = other_col
	method_col = method_col
	conds_col = conds_col  
	name_col = name_col
	name = name
	status = 'fucked'
	#Get the next row id from the deposition_conds table
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
	
	#Find the next dep_conds_id this is the same as looking for the next id of the depositions table
	dep_conds_max_id = conn.execute('SELECT max('+other_col+') FROM '+function_name+'')
	dep_max_id = dep_conds_max_id.fetchone()[0]
	
	#if an id exists increment it to use for later inserts or use 0 if not
	#this won't work if there is only one record i.e. returns a zero
	#convert to string to test truth value

	string_dep_max_id = str(dep_max_id)

	if string_dep_max_id == 'None':
		dep_conds_id = 0
	else:
		dep_conds_id = dep_max_id + 1
	
	####Get the max depositions row id for adding in a record there later (is this table needed?, why wasn't the dep_met stored in the deposition_conds table?)
	
	depositions_max_id = conn.execute('SELECT max(id) FROM '+other_table+'')
	depositions_max_id_result = depositions_max_id.fetchone()[0]
	
	#if an id exists increment it to use for later inserts or use 0 if not
	#this won't work if there is only one record i.e. returns a zero
	#convert to string to test truth value

	string_depositions_max_id_result = str(depositions_max_id_result)

	if string_depositions_max_id_result == 'None':
		depositions_id = 0
	else:
		depositions_id = depositions_max_id_result + 1
		
	
	###Each spin setting will need a new row id but same dep_conds_id
	#the cond_lst contains dicts with the coating conditions in, add the dep_conds_id (depossitions id) to this and insert
	for cl in cond_lst:
		print cl
		x_cond_dict = cl
		x_cond_dict['%s' % other_col] = dep_conds_id
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
			x_id = x_id+1
		else:
			result.remove(x_id)
			print "Record already exists, id = %s" % result[0]
			status = "Record already exists, id = %s" % result[0]
			conn.execute("DELETE FROM "+function_name+" WHERE id = ?", (x_id,));
			result[0] = x_id
	
	#this is a mess
	#Make it an if to find out if it is the depositions or treatments- bit clunky...
	conn.execute('INSERT INTO '+other_table+' (id, '+method_col+', '+conds_col+','+name_col+') VALUES (?,?,?,?)', (depositions_id,dep_met_id_select_result,dep_conds_id,name));
	conn.commit()
	#conn.close()
	return dep_conds_id, status
