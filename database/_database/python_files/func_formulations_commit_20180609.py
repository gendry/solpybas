import sqlite3
#for ordered dicts
import collections

def formulations_mod(formulation_conds_inputs_dict, formulation_props_inputs_dict, formulation_inputs_dict, conn):
	conn = conn
	#First check that the formulation has a unique name
	form_dict = formulation_inputs_dict
	
	form_name_select = conn.execute('SELECT id FROM formulations WHERE form_name = ?', (form_dict['form_name'],))
	form_name_select_result = form_name_select.fetchall()
	
	if form_name_select_result:
		form_id = False
		print "Formulation name not unique."
	else:
		print form_name_select_result
			
		#There are three tables
		#One (form_conds) for the conditions the formulaton was made under
		#Each row is a set of conditions
		#Multiple sets on conditions can be linked using the same conds_id
		
		#Another (form_props) for the properties of the formulation, a row is the id and is linked via the form_id
		
		#The other (formulations) with the materials batches making up each formulation
		#Each row is a record of a material batch used and the formulation is made up of rows linked via the form_id
		
		#First go through the conditions table, get the next row id
		#Also get the next conds_id
		#And enter the conditions values for the row and enter in the conds_id
		#Adding in further conditions isn't implemented at this stage, but could be by adding in a new row using a previous conds_id
		#Would cause problems with loading up the conditions to the gui- which to use...
		#How would the timeline be recorded? Need a period or something
		
		#Get the highest id for the form_conds records and increment
		cond_row_max_id = conn.execute('SELECT max(id) FROM form_conds')
		conds_row_max_id = cond_row_max_id.fetchone()[0]
		#if an id exists increment it to use for later inserts or use 0 if not
		#this won't work if there is only one record i.e. returns a zero
		#convert to string to test truth value

		string_conds_row_max_id = str(conds_row_max_id)

		if string_conds_row_max_id == 'None':
			conds_row_id = 0
		else:
			conds_row_id = conds_row_max_id + 1
		
		#Get the highest conds_id for the form_conds records and increment
		conds_id_max_id = conn.execute('SELECT max(conds_id) FROM form_conds')
		conds_id_max_id = conds_id_max_id.fetchone()[0]
		#if an id exists increment it to use for later inserts or use 0 if not
		#this won't work if there is only one record i.e. returns a zero
		#convert to string to test truth value

		string_conds_id_max_id = str(conds_id_max_id)

		if string_conds_id_max_id == 'None':
			form_conds_id = 0
		else:
			form_conds_id = conds_id_max_id + 1
			
		#Now there is a row number to enter the conditions in and a cond_id to go with this
		#Enter in the information, this might result in dead rows if the formulation is rejected in the next stage, but it isn't critical
		conds_dict = formulation_conds_inputs_dict
		#Add the form_conds_id to the dictionary 
		conds_dict['conds_id'] = form_conds_id
		
		##Insert the parameters into the tables
		conn.execute("INSERT INTO form_conds (id) VALUES (?)", (conds_row_id,));
		
		#build a search statement to use later as go through the values
		#there must be a nicer way...
		search_statement = "SELECT id FROM form_conds WHERE '"
		search_statement_and = ''
		search_statement_list = []

		#find the names of the columns in the table returns a list of tuples
		search_test = conn.execute("pragma table_info('form_conds')");
		test = search_test.fetchall()	

		column_dict = {}
		for i in test:
			column_dict['%s' % str(i[1])] = None

		del column_dict['id']

		for key in conds_dict:
			answer = conds_dict['%s' % key]
			answer = str(answer)	
			if answer:
				column_dict['%s' % key] = answer
			else:
				pass


		for key, value in column_dict.iteritems():
			if value == None:
				conn.execute("UPDATE form_conds SET "+key+" = ? WHERE id = ?", (value, conds_row_id,));
				search_statement_and = search_statement_and + ' AND ' + key + ' IS NULL'
			else:
				conn.execute("UPDATE form_conds SET "+key+" = ? WHERE id = ?", (value, conds_row_id,));
				search_statement_and = search_statement_and + ' AND ' + key + ' = ?'
				search_statement_list.append(value) 
				
		#The length selected depends on the length of the table name, this could probaly be avoided
		search_statement = search_statement[:32] + search_statement_and + search_statement[33:34]
		search_statement = search_statement[:32] + search_statement[36:] 
		search_statement_list =  tuple(search_statement_list)
		search_results = conn.execute(search_statement, search_statement_list);
		result = search_results.fetchall()	
		result = [i[0] for i in result]

		if len(result) < 2:
			print "form_conds record created successfully, id = %s" % conds_row_id
		else:
			result.remove(conds_row_id)
			print "form_conds record already exists, id = %s" % result[0]
			conn.execute("DELETE FROM form_conds WHERE id = ?", (conds_row_id,));
			result[0] = conds_row_id
			
		####################
		###################
		####################
		
			
		####################
		###################
		####################
		
		
		
		###Now enter in the formulatons info and use the conds_id	
		#Get the next row
		formulation_row_max_id = conn.execute('SELECT max(id) FROM formulations')
		form_row_max_id = formulation_row_max_id.fetchone()[0]
		#if an id exists increment it to use for later inserts or use 0 if not
		#this won't work if there is only one record i.e. returns a zero
		#convert to string to test truth value

		string_form_row_max_id = str(form_row_max_id)

		if string_form_row_max_id == 'None':
			form_row_id = 0
		else:
			form_row_id = form_row_max_id + 1
		
		print form_row_id
		#For each material batch in the formulation a new row in the table is needed 
		#with a common conds_id and a common form_id
		#(mixing formulations- take each row for each form_id and duplicate with proportional quantities and give a new overall form_id) 
		
		#Get the next form_id
		#Get the highest conds_id for the form_conds records and increment
		form_id_max_id = conn.execute('SELECT max(form_id) FROM formulations')
		form_id_max_id = form_id_max_id.fetchone()[0]
		#if an id exists increment it to use for later inserts or use 0 if not
		#this won't work if there is only one record i.e. returns a zero
		#convert to string to test truth value

		string_form_id_max_id = str(form_id_max_id)

		if string_form_id_max_id == 'None':
			form_id = 0
		else:
			form_id = form_id_max_id + 1
		
		#Add the form_id and conds_id to the dict (could add the props too but not sure which is most logical way round)
		#Add the conds_id to the dict
		form_dict['conds_id'] = form_conds_id
		#Add the conds_id to the dict
		form_dict['form_id'] = form_id
		
		#The dict is made up of fields one of which is a list of lists
		#Go through this list and for each sub list create a new row in the table
		for i in formulation_inputs_dict['lst']:
			form_insert_dict = {}
			#This is sort of pointless
			#print 'this is the state:'
			#print form_dict['state']
			form_insert_dict['state'] = int(form_dict['state'])
			form_insert_dict['conds_id'] = form_dict['conds_id']
			form_insert_dict['form_id'] = form_dict['form_id']
			form_insert_dict['form_name'] = formulation_inputs_dict['form_name']
			#i is a list of the mat_id, mat_bat_id and quantity
			#Add them into the first row then increment to the next row
			#This can be done by using a new dict and reusing the code
			form_insert_dict['mat_id'] = i[0]
			form_insert_dict['mat_bat_id'] = i[1]
			form_insert_dict['quantity'] = i[2]
			##Insert the parameters into the tables
			conn.execute("INSERT INTO formulations (id) VALUES (?)", (form_row_id,));
			
			#build a search statement to use later as go through the values
			#there must be a nicer way...
			search_statement = "SELECT id FROM formulations WHERE '"
			search_statement_and = ''
			search_statement_list = []

			#find the names of the columns in the table returns a list of tuples
			search_test = conn.execute("pragma table_info('formulations')");
			test = search_test.fetchall()	

			column_dict = {}
			for i in test:
				column_dict['%s' % str(i[1])] = None

			del column_dict['id']

			for key in form_insert_dict:
				answer = form_insert_dict['%s' % key]
				answer = str(answer)	
				if answer:
					column_dict['%s' % key] = answer
				else:
					pass


			for key, value in column_dict.iteritems():
				if value == None:
					conn.execute("UPDATE formulations SET "+key+" = ? WHERE id = ?", (value, form_row_id,));
					search_statement_and = search_statement_and + ' AND ' + key + ' IS NULL'
				else:
					conn.execute("UPDATE formulations SET "+key+" = ? WHERE id = ?", (value, form_row_id,));
					search_statement_and = search_statement_and + ' AND ' + key + ' = ?'
					search_statement_list.append(value) 
			
			search_statement = search_statement[:34] + search_statement_and + search_statement[35:36]
			search_statement = search_statement[:34] + search_statement[38:] 
			search_statement_list =  tuple(search_statement_list)
			search_results = conn.execute(search_statement, search_statement_list);
			result = search_results.fetchall()	
			result = [i[0] for i in result]

			if len(result) < 2:
				print "Record created successfully, id = %s" % form_id
				form_row_id = form_row_id + 1
			
			else:
				result.remove(form_row_id)
				print "Record already exists, row id = %s" % result[0]
				conn.execute("DELETE FROM formulations WHERE id = ?", (form_row_id,));
				result[0] = form_id

		####################
		###################
		####################
		
		#Now insert the properties of the formulation into the form_props table
		#Use the form_id from the formulatons table as an identifier.
			
		####################
		###################
		####################
		
		#Get the highest id for the form_props records and increment
		prop_row_max_id = conn.execute('SELECT max(id) FROM form_props')
		prop_row_max_id = prop_row_max_id.fetchone()[0]
		#if an id exists increment it to use for later inserts or use 0 if not
		#this won't work if there is only one record i.e. returns a zero
		#convert to string to test truth value

		string_prop_row_max_id = str(prop_row_max_id)

		if string_prop_row_max_id == 'None':
			props_row_id = 0
		else:
			props_row_id = prop_row_max_id + 1
		
		props_dict = formulation_props_inputs_dict
		#Add the form_id to the dictionary 
		props_dict['form_id'] = form_id
		
		##Insert the parameters into the tables
		conn.execute("INSERT INTO form_props (id) VALUES (?)", (props_row_id,));
		
		#build a search statement to use later as go through the values
		#there must be a nicer way...
		search_statement = "SELECT id FROM form_props WHERE '"
		search_statement_and = ''
		search_statement_list = []

		#find the names of the columns in the table returns a list of tuples
		search_test = conn.execute("pragma table_info('form_props')");
		test = search_test.fetchall()	

		column_dict = {}
		for i in test:
			column_dict['%s' % str(i[1])] = None

		del column_dict['id']

		for key in props_dict:
			answer = props_dict['%s' % key]
			answer = str(answer)	
			if answer:
				column_dict['%s' % key] = answer
			else:
				pass


		for key, value in column_dict.iteritems():
			if value == None:
				conn.execute("UPDATE form_props SET "+key+" = ? WHERE id = ?", (value, props_row_id,));
				search_statement_and = search_statement_and + ' AND ' + key + ' IS NULL'
			else:
				conn.execute("UPDATE form_props SET "+key+" = ? WHERE id = ?", (value, props_row_id,));
				search_statement_and = search_statement_and + ' AND ' + key + ' = ?'
				search_statement_list.append(value) 
		
		search_statement = search_statement[:32] + search_statement_and + search_statement[33:34]
		search_statement = search_statement[:32] + search_statement[36:] 
		search_statement_list =  tuple(search_statement_list)
		search_results = conn.execute(search_statement, search_statement_list);
		result = search_results.fetchall()	
		result = [i[0] for i in result]

		if len(result) < 2:
			print "form_props record created successfully, id = %s" % props_row_id
		else:
			result.remove(props_row_id)
			print "form_props record already exists, id = %s" % result[0]
			conn.execute("DELETE FROM form_props WHERE id = ?", (props_row_id,));
			result[0] = props_row_id
		
		
		
		conn.commit()
	#conn.close()
	return form_id
	
