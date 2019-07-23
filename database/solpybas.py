###########################
#This is quite messy...
###########################

#import tkinter and modules to make gui
from Tkinter import *
from tkColorChooser import askcolor 
import tkFileDialog
import tkMessageBox
import tkSimpleDialog
#import tkk for the tabs
from ttk import *
#sqlite3 for the database
import sqlite3
#for ordered dicts
import collections
#import time 
import time
#import datatime for the formulation date creation
import datetime
#import the function to add formulation to database
from func_formulations_commit_20180609 import formulations_mod
from func_materials_commit import materials_mod
from func_deposition_conds_commit import dep_conds_mod

from jv_database_import_func import import_batch_data
from func_materials_update import materials_update 
from function_stack_commit import stack_commit_function
from function_stack_update import stack_update_function
from function_batch_commit import batch_commit_function
from function_batch_update import batch_update_function
from func_pretty_box_plot import sort_data, split_pos, bp_cols, plot_list
#from read_barcode_func import read_barcode_func
#for ordered dicts
import collections

import numpy
from scipy import stats
from scipy.stats import binned_statistic

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
import matplotlib.mlab as mlab
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker

#for sorting two lists
import operator

import math

import itertools
#import pylab
import os
import platform
import ast
from PIL import Image
from zebra import zebra
from zebra_qr import print_lab

class Plotter:
	def __init__(self, master):
		
		
		self.mat_type_list = ['Metal', 'Solvent', 'Polymer', 'Inorganic', 'Organic', 'Dopant', 'TCF', 'Encapsulant']
		#self.tab_bat_sup_list = ['', 'Sigma', 'VWR', 'Alfa', 'Dyesol', 'Heraeus Clevios', 'Solenne']
		self.tab_bat_units_list = ['Grams', 'Millilitres', 'Units', '']
		self.tab_treat_dry_met_list = ['', 'Hot Plate', 'Natural', 'Lab Oven', 'Vacuum Oven','Smartcoater Ovens','Bench Top Coater Ovens','FOM Ovens']
		self.formulations_mod = formulations_mod
		self.materials_mod = materials_mod
		self.dep_conds_mod = dep_conds_mod
		self.stack_commit_function = stack_commit_function
		self.stack_update_function = stack_update_function
		self.batch_commit_function = batch_commit_function
		self.batch_update_function = batch_update_function
		self.sort_data = sort_data 
		self.split_pos = split_pos 
		self.bp_cols = bp_cols 
		self.plot_list = plot_list
		#self.read_barcode_func = read_barcode_func
		
		self.import_batch_data = import_batch_data
		self.materials_update = materials_update
		self.printer = 'ZDesigner TLP 2824-Z'
		#self.barcode_scanner = '/dev/input/by-id/usb-Datalogic_Scanning__Inc._Handheld_Barcode_Scanner_S_N_G12L15639-event-kbd'
		self.print_lab = print_lab
		self.image_finam = "blank.gif"
		self.export_file_name = 'fail.txt'
		
		db_name = 'db_r2r_20180610v0.db'
		if platform.system() == "Windows":
			self.conn = sqlite3.connect('..\\..\\_database\\sqlite\\%s' % db_name)
			self.base_file_path = '..\\..\\_database\\batches\\'
			self.top_elec_pat_file = '..\\..\\_database\\deps\\top_electrode_patterns.dat'
			self.bot_elec_pat_file = '..\\..\\_database\\deps\\bottom_electrode_patterns.dat'
		else:
			self.conn = sqlite3.connect('../../_database/sqlite/%s' % db_name)
			#### the base file path for data files
			self.base_file_path = '../../_database/batches/'
			self.top_elec_pat_file = '../../_database/deps/top_electrode_patterns.dat'
			self.bot_elec_pat_file = '../../_database/deps/bottom_electrode_patterns.dat'

		self.wholeframe = Notebook(master)
		#tab 1 for Device Stacks
		self.tab_stacks = Frame(self.wholeframe)
		#tab 2 for layers
		self.tab_layers = Frame(self.wholeframe)
		#tab 3 for formulations
		self.tab_form = Frame(self.wholeframe)
		#tab 4 for treatments
		self.tab_treat = Frame(self.wholeframe)
		#tab materials list
		self.tab_materials = Frame(self.wholeframe)
		#tab materials batches
		self.tab_mat_batch = Frame(self.wholeframe)
		#tab for the device batches
		self.tab_batches = Frame(self.wholeframe)
		#tab for the device jv results
		self.tab_jvresults = Frame(self.wholeframe)
		#tab for the queries
		self.tab_queries = Frame(self.wholeframe)
		
		self.wholeframe.add(self.tab_jvresults, text = "JV Results", compound=TOP)
		self.wholeframe.add(self.tab_batches, text = "Device Batches")
		self.wholeframe.add(self.tab_stacks, text = "Device Stacks")
		self.wholeframe.add(self.tab_treat, text = "Treatments")
		self.wholeframe.add(self.tab_layers, text = "Layers")
		self.wholeframe.add(self.tab_form, text = "Formulations")
		self.wholeframe.add(self.tab_mat_batch, text = "Materials Batches")
		self.wholeframe.add(self.tab_materials, text = "Materials")
		self.wholeframe.add(self.tab_queries, text = "Queries")
		
		self.wholeframe.grid()
		Plotter.formulation_tk(self)
		Plotter.materials_tk(self)
		Plotter.mat_batch_tk(self)
		Plotter.layers_tk(self)
		Plotter.treatments_tk(self)
		Plotter.stacks_tk(self)
		Plotter.batches_tk(self)
		Plotter.jvresults_tk(self)
		Plotter.queries_tk(self)
		#To hold the device ids selection
		self.device_list = None
		self.device_ids = None
		self.area_ids = None
		self.source_ids = None
		self.sun_ids = None
		self.rate_ids = None
		self.soak_ids = None
		self.soak_sun_ids = None
		self.lux_ids = None
		self.time_ids = None
		
	def queries_tk(self, *args):
		##### A canvas in the frame ######
		self.tab_queries_canvas = Canvas(self.tab_queries, width=1300, height=650)
		self.tab_queries_canvas.grid(row=0, column=0)
		
		#A frame in canvas to hold all the other widgets
		self.tab_queries_frame = Frame(self.tab_queries_canvas, width=1300, height=650)
		self.tab_queries_frame.grid(row=1, column=0, sticky=W)
		
		###Basic query to find the batch numbers / splits containing a particular thing#
		################################################################################
		#Frame to hold basic query selection
		self.tab_queries_basic_frame = LabelFrame(self.tab_queries_frame, text='Basic Query- Return Batches Containing X')
		self.tab_queries_basic_frame.grid(row=0, column=0, sticky=SW, columnspan=25)
		#A combo box to contain the things that can be searched e.g. layer, formulation
		##### thing to select ################
		self.tab_queries_thing_label = Label(self.tab_queries_basic_frame, text="Containing:")
		self.tab_queries_thing_label.grid(row=0, column=0, sticky=E)
		
		### Combobox for the deposited formulation ############
		self.tab_queries_thing_list = ['Stack','Layer','Formulation','Material Batch','Material']
		self.tab_queries_thing_box_var = StringVar()
		self.tab_queries_thing_box = Combobox(self.tab_queries_basic_frame, textvariable=self.tab_queries_thing_box_var, width=25)
		self.tab_queries_thing_box.bind('<<ComboboxSelected>>', self.tab_queries_thing_name_populate_combo)
		self.tab_queries_thing_box['values'] = self.tab_queries_thing_list
		self.tab_queries_thing_box.grid(row=0, column=1, sticky=W)
		self.tab_queries_thing_box.state(['readonly'])
		#If the names were stored in db
		#self.tab_queries_thing_get_list()
		
		##### names of things selected ################
		self.tab_queries_name_label = Label(self.tab_queries_basic_frame, text="Name:")
		self.tab_queries_name_label.grid(row=1, column=0, sticky=E)
		
		### Combobox for the deposited formulation ############
		self.tab_queries_name_list = []
		self.tab_queries_name_box_var = StringVar()
		self.tab_queries_name_box = Combobox(self.tab_queries_basic_frame, textvariable=self.tab_queries_name_box_var, width=100)
		self.tab_queries_name_box.bind('<<ComboboxSelected>>', self.tab_queries_name_box_clear_text)
		self.tab_queries_name_box['values'] = self.tab_queries_name_list
		self.tab_queries_name_box.grid(row=1, column=1, sticky=W)
		self.tab_queries_name_box.state(['readonly'])
		
		#Button to run the query
		self.tab_queries_run_basic_but = Button(self.tab_queries_basic_frame, text='Run Query!', command=self.tab_queries_run_basic_function)
		self.tab_queries_run_basic_but.grid(row=2, column=1, sticky=W)
		
		
	
	
		#################################################
		##################################################
		#Frame to hold tag query
		self.tab_queries_tag_frame = LabelFrame(self.tab_queries_frame, text='Tag Query- Return batch description containing keywords')
		self.tab_queries_tag_frame.grid(row=1, column=0, sticky=SW, columnspan=25)
		
		self.tab_queries_tag_label = Label(self.tab_queries_tag_frame, text="Keywords:")
		self.tab_queries_tag_label.grid(row=0, column=0, sticky=E)
		
		self.tab_queries_tag_entry_var = StringVar()
		self.tab_queries_tag_entry = Entry(self.tab_queries_tag_frame, textvariable=self.tab_queries_tag_entry_var, width=100)
		self.tab_queries_tag_entry.grid(row=0, column=1, columnspan=4, sticky=W)
		
		#Button to run the query
		self.tab_queries_run_tag_but = Button(self.tab_queries_tag_frame, text='Search Keywords', command=self.tab_queries_run_tag_function)
		self.tab_queries_run_tag_but.grid(row=2, column=1, sticky=W)
		
		self.tab_queries_results_frame = LabelFrame(self.tab_queries_frame, text='Query- Results')
		self.tab_queries_results_frame.grid(row=2, column=0, sticky=SW, columnspan=25)
		
		self.tab_queries_basic_status_lab_var = StringVar()
		self.tab_queries_basic_status_lab = Label(self.tab_queries_results_frame, textvariable=self.tab_queries_basic_status_lab_var)
		self.tab_queries_basic_status_lab.grid(row=0, column=0, sticky=W, columnspan=4)
		self.tab_queries_basic_status_lab_var.set('Status:')
		
		#Results box for the list of batches
		self.tab_queries_basic_text = Text(self.tab_queries_results_frame, width=120, height=5)
		self.tab_queries_basic_text.grid(row=1, column=0, columnspan=10, sticky=W)
	
	def tab_queries_run_tag_function(self,*args):	
		#Clear the status and results
		self.tab_queries_name_box_clear_text()
		#Clear the previous selection from the JV selection listboxes
		self.tab_jvresults_batch_listbox.selection_clear(0,'end')
		self.tab_jvresults_split_listbox.selection_clear(0,'end')
		#Get the string with the keywords in
		#Then break this into separate words
		keywords = self.tab_queries_tag_entry.get()
		keywords_lst = [x.strip().lower() for x in keywords.split(',')]
		#Go through the keywords and look for matches in the batch descriptions
		#Go through all the batches and select the description
		desc_selec = self.conn.execute('SELECT batch_num, batch_name, batch_desc, batch_notes FROM device_batches')
		desc_selec_results = desc_selec.fetchall()
		
		batch_lst = []
		for i in desc_selec_results:
			b = i[0]
			for r in range(3):
				print r
				r = r+1
				w = i[r]
				
				#Remove any special characters and replace with space
				w = re.sub('[^A-Za-z0-9]+', ' ', w)
				#Separate words into list
				w = [x.strip().lower() for x in w.split(' ')]
				if any(word in w for word in keywords_lst):
					batch_lst.append(b)
					break
		
		
		b_lst = list(self.tab_jvresults_batch_listbox.get(0, "end"))
		b_lst = [i[0] for i in b_lst]
		
		text_str = ''			
		for index, i in enumerate(batch_lst):
			if index == 0:
				text_str = 'Batches: B%s' % i
			else:
				text_str = '%s, B%s' % (text_str,i)
			#Find the index that corresponds the the batch num
			index = b_lst.index(i)
			#Set the selection using the index found
			self.tab_jvresults_batch_listbox.selection_set(index)
		#Call the function to populate the splits list box using the batches highlighted...
		self.tab_jvresults_populate_split_listbox()
		
		#Update the results text
		self.tab_queries_basic_text.insert(END, text_str)
		#Update the status box
		self.tab_queries_basic_status_lab_var.set('Status: Query run.')	
	def tab_queries_name_box_clear_text(self,*args):
		self.tab_queries_basic_status_lab_var.set('Status:')	
		self.tab_queries_basic_text.delete(1.0,END)	
	def tab_queries_get_device_stack_ids(self, layers_lst):
		device_stack_ids_lst = []
		#Select the device_stack_ids from the device_stack_parts table where the type is layer and the parts_id is the layer id from the list
		for i in layers_lst:
			id_select = self.conn.execute('SELECT device_stack_id FROM device_stack_parts WHERE type_id = ? AND part_id = ?', ('0',i,));
			id_select_results = id_select.fetchall()
			
			for i in id_select_results:
				i = i[0]
				device_stack_ids_lst.append(i)
		
		#Get the unique values these should be the ids for the device stacks table?!
		search_results_unique = set(i for i in device_stack_ids_lst)
		search_results_unique = list(search_results_unique)	
		return search_results_unique
	
	
	def tab_queries_get_mat_ids(self, mat_names):
		mat_ids_lst = []
		#Select the mat_ids from the mat_bat table where code is in the list
		for i in mat_names:
			id_select = self.conn.execute('SELECT id FROM materials WHERE common_name = ?', (i,));
			id_select_results = id_select.fetchall()
			
			for i in id_select_results:
				mat_ids_lst.append(i)
		
		print mat_ids_lst
		#Now find the formulations that contain those materials
		form_ids_lst = []
		for i in mat_ids_lst:
			id_select = self.conn.execute('SELECT form_id FROM formulations WHERE mat_id = ?', (i[0],));
			id_select_results = id_select.fetchall()
			for i in id_select_results:
				i = i[0]
				form_ids_lst.append(i)
		
		#Get the unique values these should be the ids for the device stacks table?!
		search_results_unique = set(i for i in form_ids_lst)
		form_ids_unique = list(search_results_unique)
			
		
		#Use these form_ids to find the layers that contain them...
		layers_ids_lst = []
		for i in form_ids_unique:
			id_select = self.conn.execute('SELECT id FROM layers WHERE form_id = ?', (i,));
			id_select_results = id_select.fetchall()
			
			for i in id_select_results:
				i = i[0]
				layers_ids_lst.append(i)
		
		#Get the unique values these should be the ids for the device stacks table?!
		search_results_unique = set(i for i in layers_ids_lst)
		layers_ids_unique = list(search_results_unique)
		
		return layers_ids_unique
		
	def tab_queries_get_mat_bat_ids(self, mat_bat_codes):
		mat_ids_lst = []
		#Select the mat_ids from the mat_bat table where code is in the list
		for i in mat_bat_codes:
			id_select = self.conn.execute('SELECT id, mat_id FROM mat_bat WHERE batch_code = ?', (i,));
			id_select_results = id_select.fetchall()
			
			for i in id_select_results:
				mat_ids_lst.append([i[0],i[1]])
		
		
		#Now find the formulations that contain those materials and batches 
		form_ids_lst = []
		for i in mat_ids_lst:

			id_select = self.conn.execute('SELECT form_id FROM formulations WHERE mat_id = ? AND mat_bat_id = ?', (i[1],i[0],));
			id_select_results = id_select.fetchall()
			for i in id_select_results:
				i = i[0]
				form_ids_lst.append(i)
		
		#Get the unique values these should be the ids for the device stacks table?!
		search_results_unique = set(i for i in form_ids_lst)
		form_ids_unique = list(search_results_unique)
			
		
		#Use these form_ids to find the layers that contain them...
		layers_ids_lst = []
		for i in form_ids_unique:
			id_select = self.conn.execute('SELECT id FROM layers WHERE form_id = ?', (i,));
			id_select_results = id_select.fetchall()
			
			for i in id_select_results:
				i = i[0]
				layers_ids_lst.append(i)
		
		#Get the unique values these should be the ids for the device stacks table?!
		search_results_unique = set(i for i in layers_ids_lst)
		layers_ids_unique = list(search_results_unique)
		
		return layers_ids_unique
		
	def tab_queries_get_form_ids(self, form_names):
		form_ids_lst = []
		#Select the form_ids from the formulations table where name is in the list
		for i in form_names:
			id_select = self.conn.execute('SELECT form_id FROM formulations WHERE form_name = ?', (i,));
			id_select_results = id_select.fetchall()
			
			for i in id_select_results:
				i = i[0]
				form_ids_lst.append(i)
		
		#Get the unique values these should be the ids for the device stacks table?!
		search_results_unique = set(i for i in form_ids_lst)
		form_ids_unique = list(search_results_unique)	
		
		#Use these form_ids to find the layers that contain them...
		layers_ids_lst = []
		for i in form_ids_unique:
			id_select = self.conn.execute('SELECT id FROM layers WHERE form_id = ?', (i,));
			id_select_results = id_select.fetchall()
			
			for i in id_select_results:
				i = i[0]
				layers_ids_lst.append(i)
		
		#Get the unique values these should be the ids for the device stacks table?!
		search_results_unique = set(i for i in layers_ids_lst)
		layers_ids_unique = list(search_results_unique)
		
		return layers_ids_unique
			
	def tab_queries_get_layer_ids(self, layer_ids):
		#Select the stack ids from the stack table
		layers_lst = []
		for i in layer_ids:
			
			id_select = self.conn.execute('SELECT id FROM layers WHERE layer_name = ?', (i,));
			id_select_result = id_select.fetchone()[0]
			
			layers_lst.append(id_select_result)
			
		return layers_lst
		
	def tab_queries_get_stack_ids(self, stack_ids):
		#Select the stack ids from the stack table
		stacks_lst = []
		for i in stack_ids:
			id_select = self.conn.execute('SELECT id FROM device_stacks WHERE stack_name = ?', (i,));
			id_select_result = id_select.fetchone()[0]
			
			stacks_lst.append(id_select_result)
		return stacks_lst 
		
	def tab_queries_get_splits_ids(self, stacks_lst):
		#Find all the splits that contain the stack id (split_stack)
		split_ids_lst = []
		for i in stacks_lst:
			#Select the ids from the splits table
			id_select = self.conn.execute('SELECT id FROM splits WHERE split_stack = ?', (i,));
			id_select_result = id_select.fetchone()[0]
			
			split_ids_lst.append(id_select_result)
		
		return split_ids_lst	
			
	def tab_queries_run_basic_function(self,*args):
		self.tab_queries_basic_status_lab_var.set('Status:')	
		self.tab_queries_basic_text.delete(1.0,END)	
		#Clear the previous selection from the JV selection listboxes
		self.tab_jvresults_batch_listbox.selection_clear(0,'end')
		self.tab_jvresults_split_listbox.selection_clear(0,'end')
		#Use the thing selected to decide which table to look in first
		thing = self.tab_queries_thing_box.get()
		#Separate these out in to different functions to make this less cluttered? Could pass one to the other?
		
		if thing == 'Stack':
			#First get the stack id
			stack_ids = [self.tab_queries_name_box_var.get()]
			
			stacks_lst = self.tab_queries_get_stack_ids(stack_ids)
			#then look for the splits that contain this id
			splits_ids = self.tab_queries_get_splits_ids(stacks_lst)
		elif thing == 'Layer':
			#Find the stacks containing the layers then pass on...
			layer_ids = [self.tab_queries_name_box_var.get()]
			#Find all the layer ids
			layers_lst = self.tab_queries_get_layer_ids(layer_ids)
			#Now find the deviec_stack_parts that contain that layer and return the device_stack_id that should be the stack_id
			device_stack_ids = self.tab_queries_get_device_stack_ids(layers_lst)
			
			#then look for the splits that contain this id
			splits_ids = self.tab_queries_get_splits_ids(device_stack_ids)
		elif thing == 'Formulation':
			#get the formulation name...
			form_names = [self.tab_queries_name_box_var.get()]
			#Find the ids of that form name
			layers_ids = self.tab_queries_get_form_ids(form_names)
			
			#Now find the deviec_stack_parts that contain that layer and return the device_stack_id that should be the stack_id
			device_stack_ids = self.tab_queries_get_device_stack_ids(layers_ids)
			
			#then look for the splits that contain this id
			splits_ids = self.tab_queries_get_splits_ids(device_stack_ids)
			
		elif thing == 'Material Batch':
			#Find the id that corresponmds to the batch code
			#Find the mat_id in that table for that id too
			#Find the formulations that contain that mat_id and mat_bat_id
			mat_bat_codes = [self.tab_queries_name_box_var.get()]
			layers_ids = self.tab_queries_get_mat_bat_ids(mat_bat_codes)
			
			#Now find the deviec_stack_parts that contain that layer and return the device_stack_id that should be the stack_id
			device_stack_ids = self.tab_queries_get_device_stack_ids(layers_ids)
			
			#then look for the splits that contain this id
			splits_ids = self.tab_queries_get_splits_ids(device_stack_ids)
				
		elif thing == 'Material':
			material_name = [self.tab_queries_name_box_var.get()]
			#Find the id of the material
			#Then go through the formulations list and find any that have that mat_id....
			layers_ids = self.tab_queries_get_mat_ids(material_name)
			
			#Now find the deviec_stack_parts that contain that layer and return the device_stack_id that should be the stack_id
			device_stack_ids = self.tab_queries_get_device_stack_ids(layers_ids)
			
			#then look for the splits that contain this id
			splits_ids = self.tab_queries_get_splits_ids(device_stack_ids)
			
		else:
			pass
		
		batch_lst = []	
		split_name_lst = []
		#Go through the splits ids and find the batches
		for i in splits_ids:
			#Select the batch id from the splits table using the ids
			id_select = self.conn.execute('SELECT batch_id FROM splits WHERE id = ?', (i,));
			id_select_result = id_select.fetchone()[0]
			
			batch_lst.append(id_select_result)
			#If the splits are wanted get these and highlight them too. Use splits_ids to get names...
			split_select = self.conn.execute('SELECT split FROM splits WHERE id = ?', (i,));
			split_select_result = split_select.fetchone()[0]
			
			split_name_lst.append('B%sS%s' % (id_select_result, split_select_result))
		
		#Print the batch numbers to the text box and highlight in the selection box (could also highlight the splits by going back through the splits ids)
		text_str = ''
		for index, i in enumerate(split_name_lst):
			if index == 0:
				text_str = 'Batches and splits: %s' % (i) 
			else:
				text_str = '%s, %s' % (text_str,i)
		#Use the splits ids returned to the look up the batch numbers...
		self.tab_queries_basic_text.insert(END, text_str)
		#Highlight selection in the jv_results listbox
		#For the batches this could be done by the index as the batches are numbered sequentially
		#Should really check the list to find the index of the batch number then select
		#Get the values as a list then the index
		
		# print self.tab_jvresults_batch_listbox.get(0, "end") returns a tuple of tuples, make it into a list and select the first item in each tuple
		b_lst = list(self.tab_jvresults_batch_listbox.get(0, "end"))
		b_lst = [i[0] for i in b_lst]
		for i in batch_lst:
			#Find the index that corresponds the the batch num
			index = b_lst.index(i)
			#Set the selection using the index found
			self.tab_jvresults_batch_listbox.selection_set(index)
		#Call the function to populate the splits list box using the batches highlighted...
		self.tab_jvresults_populate_split_listbox()
		#Get the splits and highlight the appropriate ones
		#The splits are numbered B0S0 etc. 
		s_lst = list(self.tab_jvresults_split_listbox.get(0, "end"))
		for i in split_name_lst:
			#Find the index that corresponds the the split num
			index = s_lst.index(i)
			#Set the selection using the index found
			self.tab_jvresults_split_listbox.selection_set(index)
		self.tab_jvresults_populate_device_listbox()
		#Update the status box
		self.tab_queries_basic_status_lab_var.set('Status: Query run.')	
		
	def tab_queries_thing_name_populate_combo(self,*args):
		self.tab_queries_name_box['values'] = []
		self.tab_queries_name_box.set('')
		#Check what the selection in the thing combo is and then use this to fetch the names from the table
		thing = self.tab_queries_thing_box.get()
		self.tab_queries_name_list = []
		if thing == 'Stack':
			#Select the stack names from the stack table
			name_select = self.conn.execute('SELECT stack_name FROM device_stacks');
			name_select_result = name_select.fetchall()
			
			#Take the names and add to the combo
			for i in name_select_result:
				#tuple of tuples
				i = i[0]
				self.tab_queries_name_list.append(i)
		elif thing == 'Layer':
			#Select the layer names from the layers table
			name_select = self.conn.execute('SELECT layer_name FROM layers');
			name_select_result = name_select.fetchall()
			
			#Take the names and add to the combo
			for i in name_select_result:
				#tuple of tuples
				i = i[0]
				self.tab_queries_name_list.append(i)
		elif thing == 'Formulation':
			#Select the formulation names from the formulations table
			name_select = self.conn.execute('SELECT form_name FROM formulations');
			name_select_result = name_select.fetchall()
			
			lst = []
			#Take the names and add to the combo
			for i in name_select_result:
				#tuple of tuples
				i = i[0]
				lst.append(i)
				
			x = set(i for i in lst)
			x = list(x)
			self.tab_queries_name_list = x
				
		elif thing == 'Material Batch':
			#Select the material batch codes from the mat_bat table
			name_select = self.conn.execute('SELECT batch_code FROM mat_bat');
			name_select_result = name_select.fetchall()

			#Take the names and add to the combo
			for i in name_select_result:
				#tuple of tuples
				#for some reason the batch_code is some other form?
				i = str(i[0])
				self.tab_queries_name_list.append(i)
				
		elif thing == 'Material':
			#Select the material names from the mat_bat table
			name_select = self.conn.execute('SELECT common_name FROM materials');
			name_select_result = name_select.fetchall()
			
			#Take the names and add to the combo
			for i in name_select_result:
				#tuple of tuples
				i = i[0]
				self.tab_queries_name_list.append(i)
		else:
			pass	
		
		#Set the names combo with values found
		self.tab_queries_name_box['values'] = self.tab_queries_name_list
		
		
	def jvresults_tk(self, *args):
		##### A canvas in the frame ######
		self.tab_jvresults_canvas = Canvas(self.tab_jvresults, width=1300, height=650)
		self.tab_jvresults_canvas.grid(row=0, column=0)
		
		#A frame in canvas to hold all the other widgets
		self.tab_jvresults_frame = Frame(self.tab_jvresults_canvas, width=1300, height=650)
		self.tab_jvresults_frame.grid(row=1, column=0, sticky=W)
		
		#A scroll bar in the tab that controls the canvas position
		self.tab_jvresults_scroll = Scrollbar(self.tab_jvresults, orient='vertical', command=self.tab_jvresults_canvas.yview)
		
		self.tab_jvresults_canvas.configure(yscrollcommand=self.tab_jvresults_scroll.set)
		
		self.tab_jvresults_scroll.grid(row=0, column=1, sticky=N+S)
		#A window for the canvas
		self.tab_jvresults_canvas.create_window((4,4), window=self.tab_jvresults_frame, anchor="nw")
		
		self.tab_jvresults_frame.bind("<Configure>", self.update_jvresults_canvas_scroll)
		
		#Another frame in the first frame
		self.tab_jvresults_selec_frame = Frame(self.tab_jvresults_frame, width=1300, height=650)
		self.tab_jvresults_selec_frame.grid(row=0, column=0, sticky=W)
		
		
		########## Labels for each of the selection parameters ##########
		#################################################################
		##### for selections ########
		self.tab_jvresults_listboxes_frame = LabelFrame(self.tab_jvresults_selec_frame, text='Scan Selection')
		self.tab_jvresults_listboxes_frame.grid(row=0, column=0, sticky=SW, columnspan=25)
		
		self.tab_jvresults_batch_label = Label(self.tab_jvresults_listboxes_frame, text='Batch')
		self.tab_jvresults_batch_label.grid(row=0, column=0)
		
		self.tab_jvresults_batch_listbox_vsb = Scrollbar(self.tab_jvresults_listboxes_frame, orient='vertical')
		self.tab_jvresults_batch_listbox_vsb.grid(row=1, column=1, sticky=N+S)
		
		self.tab_jvresults_batch_listbox = Listbox(self.tab_jvresults_listboxes_frame, yscrollcommand=self.tab_jvresults_batch_listbox_vsb.set, exportselection=False, width=5, selectmode=EXTENDED)
		self.tab_jvresults_batch_listbox.grid(row=1, column=0, sticky=W)
		self.tab_jvresults_batch_listbox.bind('<<ListboxSelect>>', self.tab_jvresults_populate_split_listbox)
		self.tab_jvresults_populate_batch_listbox()
		
		self.tab_jvresults_batch_listbox_vsb.config(command=self.tab_jvresults_batch_listbox_vsb_yview)	
		
		self.tab_jvresults_bat_all_but = Button(self.tab_jvresults_listboxes_frame, text='All', width=4, command=self.tab_jvresults_bat_all_selction)
		self.tab_jvresults_bat_all_but.grid(row=3, column=0)
		
		self.tab_jvresults_split_label = Label(self.tab_jvresults_listboxes_frame, text='Split')
		self.tab_jvresults_split_label.grid(row=0, column=2)
		
		self.tab_jvresults_split_listbox_vsb = Scrollbar(self.tab_jvresults_listboxes_frame, orient='vertical')
		self.tab_jvresults_split_listbox_vsb.grid(row=1, column=3, sticky=N+S)
		
		self.tab_jvresults_split_listbox = Listbox(self.tab_jvresults_listboxes_frame, yscrollcommand=self.tab_jvresults_split_listbox_vsb.set, exportselection=False, width=8, selectmode=EXTENDED)
		self.tab_jvresults_split_listbox.grid(row=1, column=2, sticky=W)
		self.tab_jvresults_split_listbox.bind('<<ListboxSelect>>', self.tab_jvresults_populate_device_listbox)
		self.tab_jvresults_split_listbox_vsb.config(command=self.tab_jvresults_split_listbox_vsb_yview)	
		
		self.tab_jvresults_split_all_but = Button(self.tab_jvresults_listboxes_frame, text='All', width=4, command=self.tab_jvresults_split_all_selction)
		self.tab_jvresults_split_all_but.grid(row=3, column=2)

		self.tab_jvresults_device_label = Label(self.tab_jvresults_listboxes_frame, text='Device')
		self.tab_jvresults_device_label.grid(row=0, column=4)
		
		self.tab_jvresults_device_listbox_vsb = Scrollbar(self.tab_jvresults_listboxes_frame, orient='vertical')
		self.tab_jvresults_device_listbox_vsb.grid(row=1, column=5, sticky=N+S)
		
		self.tab_jvresults_device_listbox = Listbox(self.tab_jvresults_listboxes_frame, yscrollcommand=self.tab_jvresults_device_listbox_vsb.set, exportselection=False, width=10, selectmode=EXTENDED)
		self.tab_jvresults_device_listbox.grid(row=1, column=4, sticky=W)
		self.tab_jvresults_device_listbox.bind('<<ListboxSelect>>', self.tab_jvresults_populate_pixel_listbox)
		self.tab_jvresults_device_listbox_vsb.config(command=self.tab_jvresults_device_listbox_vsb_yview)
		
		self.tab_jvresults_device_all_but = Button(self.tab_jvresults_listboxes_frame, text='All', width=4, command=self.tab_jvresults_device_all_selction)
		self.tab_jvresults_device_all_but.grid(row=3, column=4)
		
		self.tab_jvresults_pixel_label = Label(self.tab_jvresults_listboxes_frame, text='Pixel')
		self.tab_jvresults_pixel_label.grid(row=0, column=6)
		
		self.tab_jvresults_pixel_listbox_vsb = Scrollbar(self.tab_jvresults_listboxes_frame, orient='vertical')
		self.tab_jvresults_pixel_listbox_vsb.grid(row=1, column=7, sticky=N+S)
		
		self.tab_jvresults_pixel_listbox = Listbox(self.tab_jvresults_listboxes_frame, yscrollcommand=self.tab_jvresults_pixel_listbox_vsb.set, exportselection=False, width=10, selectmode=EXTENDED)
		self.tab_jvresults_pixel_listbox.grid(row=1, column=6, sticky=W)
		self.tab_jvresults_pixel_listbox.bind('<<ListboxSelect>>', self.tab_jvresults_area_listbox_update)
		self.tab_jvresults_pixel_listbox_vsb.config(command=self.tab_jvresults_pixel_listbox_vsb_yview)
		
		self.tab_jvresults_pixel_all_but = Button(self.tab_jvresults_listboxes_frame, text='All', width=4, command=self.tab_jvresults_pixel_all_selction)
		self.tab_jvresults_pixel_all_but.grid(row=3, column=6)
		
		self.tab_jvresults_area_label = Label(self.tab_jvresults_listboxes_frame, text='Area')
		self.tab_jvresults_area_label.grid(row=0, column=8)
		
		self.tab_jvresults_area_listbox_vsb = Scrollbar(self.tab_jvresults_listboxes_frame, orient='vertical')
		self.tab_jvresults_area_listbox_vsb.grid(row=1, column=9, sticky=N+S)
		
		self.tab_jvresults_area_listbox = Listbox(self.tab_jvresults_listboxes_frame, yscrollcommand=self.tab_jvresults_area_listbox_vsb.set, exportselection=False, width=5, selectmode=EXTENDED)
		self.tab_jvresults_area_listbox.grid(row=1, column=8, sticky=W)
		self.tab_jvresults_area_listbox.bind('<<ListboxSelect>>', self.tab_jvresults_light_source_listbox_update)
		self.tab_jvresults_area_listbox_vsb.config(command=self.tab_jvresults_area_listbox_vsb_yview)
		
		self.tab_jvresults_area_all_but = Button(self.tab_jvresults_listboxes_frame, text='All', width=4, command=self.tab_jvresults_area_all_selction)
		self.tab_jvresults_area_all_but.grid(row=3, column=8)
		
		
		self.tab_jvresults_source_label = Label(self.tab_jvresults_listboxes_frame, text='Light Source')
		self.tab_jvresults_source_label.grid(row=0, column=10)
		
		self.tab_jvresults_source_listbox_vsb = Scrollbar(self.tab_jvresults_listboxes_frame, orient='vertical')
		self.tab_jvresults_source_listbox_vsb.grid(row=1, column=11, sticky=N+S)
		
		self.tab_jvresults_source_listbox = Listbox(self.tab_jvresults_listboxes_frame, yscrollcommand=self.tab_jvresults_source_listbox_vsb.set, exportselection=False, width=10, selectmode=EXTENDED)
		self.tab_jvresults_source_listbox.grid(row=1, column=10, sticky=W)
		self.tab_jvresults_source_listbox.bind('<<ListboxSelect>>', self.tab_jvresults_suns_listbox_update)
		self.tab_jvresults_source_listbox_vsb.config(command=self.tab_jvresults_source_listbox_vsb_yview)
		
		self.tab_jvresults_source_all_but = Button(self.tab_jvresults_listboxes_frame, text='All', width=4, command=self.tab_jvresults_source_all_selction)
		self.tab_jvresults_source_all_but.grid(row=3, column=10)
		
		
		self.tab_jvresults_suns_label = Label(self.tab_jvresults_listboxes_frame, text='Sun Equivalents')
		self.tab_jvresults_suns_label.grid(row=0, column=12)
		
		self.tab_jvresults_suns_listbox_vsb = Scrollbar(self.tab_jvresults_listboxes_frame, orient='vertical')
		self.tab_jvresults_suns_listbox_vsb.grid(row=1, column=13, sticky=N+S)
		
		self.tab_jvresults_suns_listbox = Listbox(self.tab_jvresults_listboxes_frame, yscrollcommand=self.tab_jvresults_suns_listbox_vsb.set, exportselection=False, width=12, selectmode=EXTENDED)
		self.tab_jvresults_suns_listbox.grid(row=1, column=12, sticky=W)
		self.tab_jvresults_suns_listbox.bind('<<ListboxSelect>>', self.tab_jvresults_rate_listbox_update)
		self.tab_jvresults_suns_listbox_vsb.config(command=self.tab_jvresults_suns_listbox_vsb_yview)
		
		self.tab_jvresults_suns_all_but = Button(self.tab_jvresults_listboxes_frame, text='All', width=4, command=self.tab_jvresults_suns_all_selction)
		self.tab_jvresults_suns_all_but.grid(row=3, column=12)
		
		
		self.tab_jvresults_rate_label = Label(self.tab_jvresults_listboxes_frame, text='Scan Rate (V/s)')
		self.tab_jvresults_rate_label.grid(row=0, column=14)
		
		self.tab_jvresults_rate_listbox_vsb = Scrollbar(self.tab_jvresults_listboxes_frame, orient='vertical')
		self.tab_jvresults_rate_listbox_vsb.grid(row=1, column=15, sticky=N+S)
		
		self.tab_jvresults_rate_listbox = Listbox(self.tab_jvresults_listboxes_frame, yscrollcommand=self.tab_jvresults_rate_listbox_vsb.set, exportselection=False, width=12, selectmode=EXTENDED)
		self.tab_jvresults_rate_listbox.grid(row=1, column=14, sticky=W)
		self.tab_jvresults_rate_listbox.bind('<<ListboxSelect>>', self.tab_jvresults_soak_time_listbox_update)
		self.tab_jvresults_rate_listbox_vsb.config(command=self.tab_jvresults_rate_listbox_vsb_yview)
		
		self.tab_jvresults_rate_all_but = Button(self.tab_jvresults_listboxes_frame, text='All', width=4, command=self.tab_jvresults_rate_all_selction)
		self.tab_jvresults_rate_all_but.grid(row=3, column=14)
		
		
		self.tab_jvresults_soak_time_label = Label(self.tab_jvresults_listboxes_frame, text='Soak Time')
		self.tab_jvresults_soak_time_label.grid(row=0, column=16)
		
		self.tab_jvresults_soak_time_listbox_vsb = Scrollbar(self.tab_jvresults_listboxes_frame, orient='vertical')
		self.tab_jvresults_soak_time_listbox_vsb.grid(row=1, column=17, sticky=N+S)
		
		self.tab_jvresults_soak_time_listbox = Listbox(self.tab_jvresults_listboxes_frame, yscrollcommand=self.tab_jvresults_soak_time_listbox_vsb.set, exportselection=False, width=8, selectmode=EXTENDED)
		self.tab_jvresults_soak_time_listbox.grid(row=1, column=16, sticky=W)
		self.tab_jvresults_soak_time_listbox.bind('<<ListboxSelect>>', self.tab_jvresults_soak_suns_listbox_update)
		self.tab_jvresults_soak_time_listbox_vsb.config(command=self.tab_jvresults_soak_time_listbox_vsb_yview)
		
		self.tab_jvresults_soak_time_all_but = Button(self.tab_jvresults_listboxes_frame, text='All', width=4, command=self.tab_jvresults_soak_time_all_selction)
		self.tab_jvresults_soak_time_all_but.grid(row=3, column=16)
		
		self.tab_jvresults_soak_suns_label = Label(self.tab_jvresults_listboxes_frame, text='Soak Suns')
		self.tab_jvresults_soak_suns_label.grid(row=0, column=18)
		
		self.tab_jvresults_soak_suns_listbox_vsb = Scrollbar(self.tab_jvresults_listboxes_frame, orient='vertical')
		self.tab_jvresults_soak_suns_listbox_vsb.grid(row=1, column=19, sticky=N+S)
		
		self.tab_jvresults_soak_suns_listbox = Listbox(self.tab_jvresults_listboxes_frame, yscrollcommand=self.tab_jvresults_soak_suns_listbox_vsb.set, exportselection=False, width=8, selectmode=EXTENDED)
		self.tab_jvresults_soak_suns_listbox.grid(row=1, column=18, sticky=W)
		self.tab_jvresults_soak_suns_listbox.bind('<<ListboxSelect>>', self.tab_jvresults_lux_listbox_update)
		self.tab_jvresults_soak_suns_listbox_vsb.config(command=self.tab_jvresults_soak_suns_listbox_vsb_yview)
		
		self.tab_jvresults_soak_suns_all_but = Button(self.tab_jvresults_listboxes_frame, text='All', width=4, command=self.tab_jvresults_soak_suns_all_selction)
		self.tab_jvresults_soak_suns_all_but.grid(row=3, column=18)
		
		
		self.tab_jvresults_lux_label = Label(self.tab_jvresults_listboxes_frame, text='Lux')
		self.tab_jvresults_lux_label.grid(row=0, column=20)
		
		self.tab_jvresults_lux_listbox_vsb = Scrollbar(self.tab_jvresults_listboxes_frame, orient='vertical')
		self.tab_jvresults_lux_listbox_vsb.grid(row=1, column=21, sticky=N+S)
		
		self.tab_jvresults_lux_listbox = Listbox(self.tab_jvresults_listboxes_frame, yscrollcommand=self.tab_jvresults_lux_listbox_vsb.set, exportselection=False, width=8, selectmode=EXTENDED)
		self.tab_jvresults_lux_listbox.grid(row=1, column=20, sticky=W)
		self.tab_jvresults_lux_listbox.bind('<<ListboxSelect>>', self.tab_jvresults_time_listbox_update)
		self.tab_jvresults_lux_listbox_vsb.config(command=self.tab_jvresults_lux_listbox_vsb_yview)
		
		self.tab_jvresults_lux_all_but = Button(self.tab_jvresults_listboxes_frame, text='All', width=4, command=self.tab_jvresults_lux_all_selction)
		self.tab_jvresults_lux_all_but.grid(row=3, column=20)
		
		self.tab_jvresults_time_label = Label(self.tab_jvresults_listboxes_frame, text='Time')
		self.tab_jvresults_time_label.grid(row=0, column=22)
		
		self.tab_jvresults_time_listbox_vsb = Scrollbar(self.tab_jvresults_listboxes_frame, orient='vertical')
		self.tab_jvresults_time_listbox_vsb.grid(row=1, column=23, sticky=N+S)
		
		self.tab_jvresults_time_listbox = Listbox(self.tab_jvresults_listboxes_frame, yscrollcommand=self.tab_jvresults_time_listbox_vsb.set, exportselection=False, width=17, selectmode=EXTENDED)
		self.tab_jvresults_time_listbox.grid(row=1, column=22, sticky=W)
		self.tab_jvresults_time_listbox.bind('<<ListboxSelect>>', self.tab_jvresults_scan_listbox_update)
		self.tab_jvresults_time_listbox_vsb.config(command=self.tab_jvresults_time_listbox_vsb_yview)
		
		self.tab_jvresults_time_all_but = Button(self.tab_jvresults_listboxes_frame, text='All', width=4, command=self.tab_jvresults_time_all_selction)
		self.tab_jvresults_time_all_but.grid(row=3, column=22)
		
		self.tab_jvresults_scan_label = Label(self.tab_jvresults_listboxes_frame, text='Scan')
		self.tab_jvresults_scan_label.grid(row=0, column=24)
		
		self.tab_jvresults_scan_listbox_vsb = Scrollbar(self.tab_jvresults_listboxes_frame, orient='vertical')
		self.tab_jvresults_scan_listbox_vsb.grid(row=1, column=25, sticky=N+S)
		
		self.tab_jvresults_scan_listbox = Listbox(self.tab_jvresults_listboxes_frame, yscrollcommand=self.tab_jvresults_scan_listbox_vsb.set, exportselection=False, width=10, selectmode=EXTENDED)
		self.tab_jvresults_scan_listbox.grid(row=1, column=24, sticky=W)
		self.tab_jvresults_scan_listbox.bind('<<ListboxSelect>>')
		self.tab_jvresults_scan_listbox_vsb.config(command=self.tab_jvresults_scan_listbox_vsb_yview)


		self.tab_jvresults_scan_all_but = Button(self.tab_jvresults_listboxes_frame, text='All', width=4, command=self.tab_jvresults_scan_all_selction)
		self.tab_jvresults_scan_all_but.grid(row=3, column=24)
		
		self.tab_jvresults_everything_but = Button(self.tab_jvresults_listboxes_frame, text='Select Everything', width=18, command=self.tab_jvresults_scan_everything_selction)
		self.tab_jvresults_everything_but.grid(row=4, column=23,sticky=W,columnspan=3)
		###### frame for the parameter selection ############
		self.tab_jvresults_comp_frame = LabelFrame(self.tab_jvresults_selec_frame, text='Parameters to Plot')
		self.tab_jvresults_comp_frame.grid(row=4, column=0, sticky=NW, columnspan=15)
		
		self.tab_jvresults_quit_but = Button(self.tab_jvresults_selec_frame, text='QUIT', command=self.quit)
		self.tab_jvresults_quit_but.grid(row=5, column=0, sticky=W, columnspan=15)
		
		self.tab_jvresults_comp_normx_var = IntVar()
		self.tab_jvresults_comp_normx = Checkbutton(self.tab_jvresults_comp_frame, text='Normalise X', variable=self.tab_jvresults_comp_normx_var)
		self.tab_jvresults_comp_normx.grid(row=0, column=0,sticky=W)
		
		self.tab_jvresults_comp_normy_var = IntVar()
		self.tab_jvresults_comp_normy = Checkbutton(self.tab_jvresults_comp_frame, text='Normalise Y', variable=self.tab_jvresults_comp_normy_var)
		self.tab_jvresults_comp_normy.grid(row=0, column=1,sticky=W)
		
		self.tab_jvresults_comp_logx_var = IntVar()
		self.tab_jvresults_comp_logx = Checkbutton(self.tab_jvresults_comp_frame, text='Linear/Log x', variable=self.tab_jvresults_comp_logx_var)
		self.tab_jvresults_comp_logx.grid(row=0, column=2,sticky=W)
		
		self.tab_jvresults_comp_logy_var = IntVar()
		self.tab_jvresults_comp_logy = Checkbutton(self.tab_jvresults_comp_frame, text='Linear/Log y', variable=self.tab_jvresults_comp_logy_var)
		self.tab_jvresults_comp_logy.grid(row=0, column=3,sticky=W)
		
		self.tab_jvresults_comp_ex_xless_lab = Label(self.tab_jvresults_comp_frame, text='X Exclude <=')
		self.tab_jvresults_comp_ex_xless_lab.grid(row=1, column=0,sticky=W)
		
		self.tab_jvresults_comp_ex_xless_spinbox_var = StringVar()
		self.tab_jvresults_comp_ex_xless_spinbox = Spinbox(self.tab_jvresults_comp_frame, from_=0, to=1000000000000, format="%.6f", increment=0.000001, textvariable=self.tab_jvresults_comp_ex_xless_spinbox_var, width=10) 
		self.tab_jvresults_comp_ex_xless_spinbox.grid(row=2, column=0, sticky=W)
		self.tab_jvresults_comp_ex_xless_spinbox_var.set(0.001)
		
		
		self.tab_jvresults_comp_ex_xmore_lab = Label(self.tab_jvresults_comp_frame, text='X Exclude >=')
		self.tab_jvresults_comp_ex_xmore_lab.grid(row=1, column=1,sticky=W)
		
		self.tab_jvresults_comp_ex_xmore_spinbox_var = StringVar()
		self.tab_jvresults_comp_ex_xmore_spinbox = Spinbox(self.tab_jvresults_comp_frame, from_=0, to=1000000000000, format="%.6f", increment=0.000001, textvariable=self.tab_jvresults_comp_ex_xmore_spinbox_var, width=13) 
		self.tab_jvresults_comp_ex_xmore_spinbox.grid(row=2, column=1, sticky=W)
		self.tab_jvresults_comp_ex_xmore_spinbox_var.set(100000000000.0) 
		
		self.tab_jvresults_comp_ex_yless_lab = Label(self.tab_jvresults_comp_frame, text='Y Exclude <=')
		self.tab_jvresults_comp_ex_yless_lab.grid(row=1, column=2,sticky=W)
		
		self.tab_jvresults_comp_ex_yless_spinbox_var = StringVar()
		self.tab_jvresults_comp_ex_yless_spinbox = Spinbox(self.tab_jvresults_comp_frame, from_=0, to=1000000000000, format="%.6f", increment=0.000001, textvariable=self.tab_jvresults_comp_ex_yless_spinbox_var, width=10) 
		self.tab_jvresults_comp_ex_yless_spinbox.grid(row=2, column=2, sticky=W)
		self.tab_jvresults_comp_ex_yless_spinbox_var.set(0.001)
		
		
		self.tab_jvresults_comp_ex_ymore_lab = Label(self.tab_jvresults_comp_frame, text='Y Exclude >=')
		self.tab_jvresults_comp_ex_ymore_lab.grid(row=1, column=3,sticky=W)
		
		self.tab_jvresults_comp_ex_ymore_spinbox_var = StringVar()
		self.tab_jvresults_comp_ex_ymore_spinbox = Spinbox(self.tab_jvresults_comp_frame, from_=0, to=1000000000000, format="%.6f", increment=0.000001, textvariable=self.tab_jvresults_comp_ex_ymore_spinbox_var, width=13) 
		self.tab_jvresults_comp_ex_ymore_spinbox.grid(row=2, column=3, sticky=W)
		self.tab_jvresults_comp_ex_ymore_spinbox_var.set(100000000000.0)
		
		###### combo box for parameter to plot#######
		self.tab_jvresults_x_lab = Label(self.tab_jvresults_comp_frame, text='X-Axis Parameter:')
		self.tab_jvresults_x_lab.grid(row=3, column=0, sticky=W)
		
		self.tab_jvresults_comp_xpara_box_var = StringVar()
		self.tab_jvresults_comp_xpara_box_list = ['pce', 'voc', 'jsc', 'isc', 'ff', 'mpd', 'pmax', 'vmax', 'jmax', 'imax', 'rs', 'rsh', 'sun_equiv', 'scan_rate', 'cell_area', 'soak_time', 'soak_suns', 'irradiance', 'time_stamp', 'lux', 'temperature', 'masked_by_full_area']
		self.tab_jvresults_comp_xpara_box = Combobox(self.tab_jvresults_comp_frame, textvariable=self.tab_jvresults_comp_xpara_box_var, width=15)
		self.tab_jvresults_comp_xpara_box.bind('<<ComboboxSelected>>')
		self.tab_jvresults_comp_xpara_box['values'] = self.tab_jvresults_comp_xpara_box_list
		self.tab_jvresults_comp_xpara_box.grid(row=3, column=1, sticky=W)
		self.tab_jvresults_comp_xpara_box.state(['readonly'])
		self.tab_jvresults_comp_xpara_box_var.set('rs')
		
		self.tab_jvresults_y_lab = Label(self.tab_jvresults_comp_frame, text='Y-Axis Parameter:')
		self.tab_jvresults_y_lab.grid(row=4, column=0, sticky=W)
		
		self.tab_jvresults_comp_ypara_box_var = StringVar()
		self.tab_jvresults_comp_ypara_box_list = ['pce', 'voc', 'jsc', 'isc', 'ff', 'mpd', 'pmax', 'vmax', 'jmax', 'imax', 'rs', 'rsh', 'sun_equiv', 'scan_rate', 'cell_area', 'soak_time', 'soak_suns', 'irradiance', 'time_stamp', 'lux', 'temperature']
		self.tab_jvresults_comp_ypara_box = Combobox(self.tab_jvresults_comp_frame, textvariable=self.tab_jvresults_comp_ypara_box_var, width=15)
		self.tab_jvresults_comp_ypara_box.bind('<<ComboboxSelected>>')
		self.tab_jvresults_comp_ypara_box['values'] = self.tab_jvresults_comp_ypara_box_list
		self.tab_jvresults_comp_ypara_box.grid(row=4, column=1, sticky=W)
		self.tab_jvresults_comp_ypara_box.state(['readonly'])
		self.tab_jvresults_comp_ypara_box_var.set('pce')
		
		self.tab_jvresults_av_lab = Label(self.tab_jvresults_comp_frame, text='Average By:')
		self.tab_jvresults_av_lab.grid(row=5, column=0, sticky=E)
		
		self.tab_jvresults_comp_av_box_var = StringVar()
		self.tab_jvresults_comp_av_box_list = ['Split', 'Device', 'Pixel']
		self.tab_jvresults_comp_av_box = Combobox(self.tab_jvresults_comp_frame, textvariable=self.tab_jvresults_comp_av_box_var, width=15)
		self.tab_jvresults_comp_av_box.bind('<<ComboboxSelected>>')
		self.tab_jvresults_comp_av_box['values'] = self.tab_jvresults_comp_av_box_list
		self.tab_jvresults_comp_av_box.grid(row=5, column=1, sticky=W)
		self.tab_jvresults_comp_av_box.state(['readonly'])
		self.tab_jvresults_comp_av_box_var.set('Split')
	
		#for lifetime bins and x scale
		self.tab_jvresults_lifetime_bin_lab = Label(self.tab_jvresults_comp_frame, text='Lifetime Bin Units and Size:')
		self.tab_jvresults_lifetime_bin_lab.grid(row=6, column=0, sticky=E, columnspan=2)
		
		self.tab_jvresults_comp_xscale_box_var = StringVar()
		self.tab_jvresults_comp_xscale_box_list = ['seconds', 'minutes', 'hours', 'days']
		self.tab_jvresults_comp_xscale_box = Combobox(self.tab_jvresults_comp_frame, textvariable=self.tab_jvresults_comp_xscale_box_var, width=15)
		self.tab_jvresults_comp_xscale_box.bind('<<ComboboxSelected>>')
		self.tab_jvresults_comp_xscale_box['values'] = self.tab_jvresults_comp_xscale_box_list
		self.tab_jvresults_comp_xscale_box.grid(row=6, column=2, sticky=E)
		self.tab_jvresults_comp_xscale_box.state(['readonly'])
		self.tab_jvresults_comp_xscale_box_var.set('seconds')
		
		#Bin size
		self.tab_jvresults_comp_bin_spinbox_var = StringVar()
		self.tab_jvresults_comp_bin_spinbox = Spinbox(self.tab_jvresults_comp_frame, from_=0, to=1000000000000000, format="%.1f", increment=1.0, textvariable=self.tab_jvresults_comp_bin_spinbox_var, width=10) 
		self.tab_jvresults_comp_bin_spinbox.grid(row=6, column=3, sticky=W)
		self.tab_jvresults_comp_bin_spinbox_var.set(1) 
		
		###Historam
		self.tab_jvresults_comp_hist_var = IntVar()
		self.tab_jvresults_comp_hist = Checkbutton(self.tab_jvresults_comp_frame, text='Histogram', variable=self.tab_jvresults_comp_hist_var)
		self.tab_jvresults_comp_hist.grid(row=7, column=0,sticky=W)
		
		self.tab_jvresults_hist_lab = Label(self.tab_jvresults_comp_frame, text='Histogram Bin Size:')
		self.tab_jvresults_hist_lab.grid(row=7, column=1, sticky=E)
		
		self.tab_jvresults_comp_bin_hist_spinbox_var = StringVar()
		self.tab_jvresults_comp_bin_hist_spinbox = Spinbox(self.tab_jvresults_comp_frame, from_=0, to=1000000000000000, format="%.1f", increment=0.01, textvariable=self.tab_jvresults_comp_bin_hist_spinbox_var, width=10) 
		self.tab_jvresults_comp_bin_hist_spinbox.grid(row=7, column=2, sticky=W)
		self.tab_jvresults_comp_bin_hist_spinbox_var.set(1) 
		
		self.tab_jvresults_comp_sd_var = IntVar()
		self.tab_jvresults_comp_sd = Checkbutton(self.tab_jvresults_comp_frame, text='Std Dev', variable=self.tab_jvresults_comp_sd_var)
		self.tab_jvresults_comp_sd.grid(row=8, column=0,sticky=W)
		
		self.tab_jvresults_comp_sd_shade_var = IntVar()
		self.tab_jvresults_comp_sd_shade = Checkbutton(self.tab_jvresults_comp_frame, text='Shade SD Line', variable=self.tab_jvresults_comp_sd_shade_var)
		self.tab_jvresults_comp_sd_shade.grid(row=8, column=1,sticky=W)
		
		self.tab_jvresults_comp_plot_but = Button(self.tab_jvresults_comp_frame, text='Plot Box Plots', command=self.tab_jvresults_plot_box_plot_function)
		self.tab_jvresults_comp_plot_but.grid(row=9, column=0,sticky=W)
		
		self.tab_jvresults_ab_plot_but = Button(self.tab_jvresults_comp_frame, text='Plot A vs B', command=self.tab_jvresults_plot_ab_function)
		self.tab_jvresults_ab_plot_but.grid(row=9, column=1,sticky=W)
		
		self.tab_jvresults_export_but = Button(self.tab_jvresults_comp_frame, text='Export', command=self.tab_jvresults_export_selection_function)
		self.tab_jvresults_export_but.grid(row=9, column=2,sticky=W)
		
		self.tab_jvresults_rean_check_var = IntVar()
		self.tab_jvresults_rean_check = Checkbutton(self.tab_jvresults_comp_frame, text='Re-Annotate', variable=self.tab_jvresults_rean_check_var)
		self.tab_jvresults_rean_check.grid(row=9, column=3,sticky=W)
		
		self.tab_jvresults_comp_plot_pretty_but = Button(self.tab_jvresults_comp_frame, text='Plot Pretty Box Plots', command=self.tab_jvresults_plot_pretty_box_plot_function)
		self.tab_jvresults_comp_plot_pretty_but.grid(row=10, column=0,sticky=W,columnspan=4)
		#### Frame for the data filtering
		self.tab_jvresults_para_frame = Frame(self.tab_jvresults_selec_frame)
		self.tab_jvresults_para_frame.grid(row=4, column=15, sticky=SW, columnspan=10)	
		
		####################
		##########################
		###############################
		####################################
		self.tab_jvresults_selec_red_frame = LabelFrame(self.tab_jvresults_selec_frame, text='Refine Selection')
		self.tab_jvresults_selec_red_frame.grid(row=4, column=12, sticky=NW, columnspan=15)
		
		self.tab_jvresults_check_il_var = IntVar()
		self.tab_jvresults_check_il = Checkbutton(self.tab_jvresults_selec_red_frame, variable=self.tab_jvresults_check_il_var)
		self.tab_jvresults_check_il.grid(row=0, column=0,sticky=E)
		self.tab_jvresults_check_il_var.set(True)
		###### combo box for light dark both #######
		self.tab_jvresults_para_light_box_var = StringVar()
		self.tab_jvresults_para_light_box_list = ['Light Only', 'Dark Only', 'Together', 'Separate']
		self.tab_jvresults_para_light_box = Combobox(self.tab_jvresults_selec_red_frame, textvariable=self.tab_jvresults_para_light_box_var, width=15)
		self.tab_jvresults_para_light_box.bind('<<ComboboxSelected>>')
		self.tab_jvresults_para_light_box['values'] = self.tab_jvresults_para_light_box_list
		self.tab_jvresults_para_light_box.grid(row=0, column=1, sticky=W)
		self.tab_jvresults_para_light_box.state(['readonly'])
		self.tab_jvresults_para_light_box.current(0)
		
		
		self.tab_jvresults_check_dir_var = IntVar()
		self.tab_jvresults_check_dir = Checkbutton(self.tab_jvresults_selec_red_frame, variable=self.tab_jvresults_check_dir_var)
		self.tab_jvresults_check_dir.grid(row=1, column=0,sticky=E)
		self.tab_jvresults_check_dir_var.set(True)
		###### combo box with the scan directions to plot #######
		self.tab_jvresults_para_direc_box_var = StringVar()
		self.tab_jvresults_para_direc_box_list = ['Forward Only', 'Reverse Only', 'Together', 'Separate']
		self.tab_jvresults_para_direc_box = Combobox(self.tab_jvresults_selec_red_frame, textvariable=self.tab_jvresults_para_direc_box_var, width=15)
		self.tab_jvresults_para_direc_box.bind('<<ComboboxSelected>>')
		self.tab_jvresults_para_direc_box['values'] = self.tab_jvresults_para_direc_box_list
		self.tab_jvresults_para_direc_box.grid(row=1, column=1, sticky=W)
		self.tab_jvresults_para_direc_box.state(['readonly'])
		self.tab_jvresults_para_direc_box_var.set('Scan Directions')
		
		
		self.tab_jvresults_check_sun_var = IntVar()
		self.tab_jvresults_check_sun = Checkbutton(self.tab_jvresults_selec_red_frame, variable=self.tab_jvresults_check_sun_var)
		self.tab_jvresults_check_sun.grid(row=2, column=0,sticky=E)
		
		###### spin for the suns equivalents light levels to plot ############
		self.tab_jvresults_para_level_lab = Label(self.tab_jvresults_selec_red_frame, text='Sun Equivalents')
		self.tab_jvresults_para_level_lab.grid(row=2, column=1, sticky=W)
		
		self.tab_jvresults_para_level_tol_lab = Label(self.tab_jvresults_selec_red_frame, text='Tolerance (%)')
		self.tab_jvresults_para_level_tol_lab.grid(row=2, column=2, sticky=W)
		
		self.tab_jvresults_para_level_spinbox_var = StringVar()
		self.tab_jvresults_para_level_spinbox = Spinbox(self.tab_jvresults_selec_red_frame, from_=0, to=99, format="%.5f", increment=0.00001, textvariable=self.tab_jvresults_para_level_spinbox_var, width=15) 
		self.tab_jvresults_para_level_spinbox.grid(row=3, column=1, sticky=W)
		self.tab_jvresults_para_level_spinbox_var.set(1.0) 
		
		self.tab_jvresults_para_level_tol_spinbox_var = StringVar()
		self.tab_jvresults_para_level_tol_spinbox = Spinbox(self.tab_jvresults_selec_red_frame, from_=0.01, to=100, format="%.2f", increment=0.01, textvariable=self.tab_jvresults_para_level_tol_spinbox_var, width=5) 
		self.tab_jvresults_para_level_tol_spinbox.grid(row=3, column=2, sticky=W)
		self.tab_jvresults_para_level_tol_spinbox_var.set(5.00) 
		
		
		self.tab_jvresults_check_rate_var = IntVar()
		self.tab_jvresults_check_rate = Checkbutton(self.tab_jvresults_selec_red_frame, variable=self.tab_jvresults_check_rate_var)
		self.tab_jvresults_check_rate.grid(row=4, column=0,sticky=E)
		
		###### spin for the scan rates to plot ############
		self.tab_jvresults_para_rate_lab = Label(self.tab_jvresults_selec_red_frame, text='Scan Rate (V/s)')
		self.tab_jvresults_para_rate_lab.grid(row=4, column=1, sticky=W)
		
		self.tab_jvresults_para_rate_tol_lab = Label(self.tab_jvresults_selec_red_frame, text='Tolerance (%)')
		self.tab_jvresults_para_rate_tol_lab.grid(row=4, column=2, sticky=W)
		
		self.tab_jvresults_para_rate_spinbox_var = StringVar()
		self.tab_jvresults_para_rate_spinbox = Spinbox(self.tab_jvresults_selec_red_frame, from_=0, to=99, format="%.5f", increment=0.00001, textvariable=self.tab_jvresults_para_rate_spinbox_var, width=15) 
		self.tab_jvresults_para_rate_spinbox.grid(row=5, column=1, sticky=W)
		self.tab_jvresults_para_rate_spinbox_var.set(0.07) 
		
		self.tab_jvresults_para_rate_tol_spinbox_var = StringVar()
		self.tab_jvresults_para_rate_tol_spinbox = Spinbox(self.tab_jvresults_selec_red_frame, from_=0.01, to=100, format="%.2f", increment=0.01, textvariable=self.tab_jvresults_para_rate_tol_spinbox_var, width=5) 
		self.tab_jvresults_para_rate_tol_spinbox.grid(row=5, column=2, sticky=W)
		self.tab_jvresults_para_rate_tol_spinbox_var.set(10.00) 
		
		
		###### combo box for first last scan #######
		self.tab_jvresults_para_first_last_box_var = StringVar()
		self.tab_jvresults_para_first_last_box_list = ['First Scan Only', 'Last Scan Only']
		self.tab_jvresults_para_first_last_box = Combobox(self.tab_jvresults_selec_red_frame, textvariable=self.tab_jvresults_para_first_last_box_var, width=15)
		self.tab_jvresults_para_first_last_box.bind('<<ComboboxSelected>>')
		self.tab_jvresults_para_first_last_box['values'] = self.tab_jvresults_para_first_last_box_list
		self.tab_jvresults_para_first_last_box.grid(row=6, column=1, sticky=W)
		self.tab_jvresults_para_first_last_box.state(['readonly'])
		self.tab_jvresults_para_first_last_box.current(0)
		
		
		self.tab_jvresults_check_first_last_var = IntVar()
		self.tab_jvresults_check_first_last = Checkbutton(self.tab_jvresults_selec_red_frame, variable=self.tab_jvresults_check_first_last_var)
		self.tab_jvresults_check_first_last.grid(row=6, column=0,sticky=E)
		self.tab_jvresults_check_first_last_var.set(False)
		
		self.tab_jvresults_selec_box_var = StringVar()
		self.tab_jvresults_selec_list = []
		self.tab_jvresults_selec_box = Combobox(self.tab_jvresults_selec_red_frame, textvariable=self.tab_jvresults_selec_box_var, width=20)
		self.tab_jvresults_selec_box.bind('<<ComboboxSelected>>', self.update_jvresults_selec_info)
		self.tab_jvresults_selec_box['values'] = self.tab_jvresults_selec_list
		self.tab_jvresults_selec_box.grid(row=6, column=2, columnspan=3, sticky=W)
		self.tab_jvresults_selec_box.state(['readonly'])
		self.update_jvresults_selec_combo()

		###
		
		self.tab_jvresults_para_save_selec_but = Button(self.tab_jvresults_selec_red_frame, text='Save Data Selection', command=self.tab_jvresults_save_selection)
		self.tab_jvresults_para_save_selec_but.grid(row=7, column=0, sticky=E)
		
		self.tab_jvresults_para_load_selec_but = Button(self.tab_jvresults_selec_red_frame, text='Load Data Selection', command=self.tab_jvresults_load_selection)
		self.tab_jvresults_para_load_selec_but.grid(row=7, column=1, sticky=W)
		
		self.tab_jvresults_para_merge_selec_but = Button(self.tab_jvresults_selec_red_frame, text='Merge Data Selection', command=self.tab_jvresults_merge_selection)
		self.tab_jvresults_para_merge_selec_but.grid(row=7, column=2, sticky=W)
		
		self.tab_jvresults_selec_name_entry_var = StringVar()
		self.tab_jvresults_selec_entry = Entry(self.tab_jvresults_selec_red_frame, textvariable=self.tab_jvresults_selec_name_entry_var, width=40)
		self.tab_jvresults_selec_entry.grid(row=8, column=0, columnspan=4, sticky=W)
		
		self.tab_jvresults_selec_lab_var = StringVar()
		self.tab_jvresults_selec_lab = Label(self.tab_jvresults_selec_red_frame, textvariable=self.tab_jvresults_selec_lab_var)
		self.tab_jvresults_selec_lab.grid(row=9, column=0, sticky=W, columnspan=4)
		self.tab_jvresults_selec_lab_var.set('Status:')
		
		##
		self.tab_jvresults_shunt_var = IntVar()
		self.tab_jvresults_shunt_but = Checkbutton(self.tab_jvresults_selec_red_frame, text='Exclude Shunts', variable=self.tab_jvresults_shunt_var)
		self.tab_jvresults_shunt_but.grid(row=10, column=0, sticky=W)
		self.tab_jvresults_shunt_var.set(1)
		
		self.tab_jvresults_short_var = IntVar()
		self.tab_jvresults_short_but = Checkbutton(self.tab_jvresults_selec_red_frame, text='Exclude Shorts', variable=self.tab_jvresults_short_var)
		self.tab_jvresults_short_but.grid(row=10, column=1, sticky=W)
		self.tab_jvresults_short_var.set(1)
		
		self.tab_jvresults_fail_var = IntVar()
		self.tab_jvresults_fail_but = Checkbutton(self.tab_jvresults_selec_red_frame, text='Exclude Fails', variable=self.tab_jvresults_fail_var)
		self.tab_jvresults_fail_but.grid(row=10, column=2, sticky=W)
		self.tab_jvresults_fail_var.set(1)
		
		self.tab_jvresults_over_var = IntVar()
		self.tab_jvresults_over_but = Checkbutton(self.tab_jvresults_selec_red_frame, text='Exclude Overs', variable=self.tab_jvresults_over_var)
		self.tab_jvresults_over_but.grid(row=11, column=0, sticky=W)
		self.tab_jvresults_over_var.set(1)
		
		self.tab_jvresults_under_var = IntVar()
		self.tab_jvresults_under_but = Checkbutton(self.tab_jvresults_selec_red_frame, text='Exclude Unders', variable=self.tab_jvresults_under_var)
		self.tab_jvresults_under_but.grid(row=11, column=1, sticky=W)
		self.tab_jvresults_under_var.set(1)
		
		self.tab_jvresults_cross_var = IntVar()
		self.tab_jvresults_cross_but = Checkbutton(self.tab_jvresults_selec_red_frame, text='Exclude Crosstalk', variable=self.tab_jvresults_cross_var)
		self.tab_jvresults_cross_but.grid(row=11, column=2,sticky=W)
		self.tab_jvresults_cross_var.set(1)
		
		self.tab_jvresults_ok_var = IntVar()
		self.tab_jvresults_ok_but = Checkbutton(self.tab_jvresults_selec_red_frame, text='Exclude OK', variable=self.tab_jvresults_ok_var)
		self.tab_jvresults_ok_but.grid(row=12, column=0,sticky=W)
		self.tab_jvresults_ok_var.set(0)
		
		
		self.tab_jvresults_para_refresh_but = Button(self.tab_jvresults_selec_red_frame, text='Refresh Data Selection', command=self.tab_jvresults_refresh_selection)
		self.tab_jvresults_para_refresh_but.grid(row=13, column=0, sticky=W)
		
		#################################################
		###### frame for the box plot ############
		self.tab_jvresults_plot_frame = LabelFrame(self.tab_jvresults_selec_frame, text='Box Plot')
		self.tab_jvresults_plot_frame.grid(row=10, column=0, sticky=SW, columnspan=25)
		
		
		###
		#This is to make the subplots of the figure changable
		self.gs = gridspec.GridSpec(1,1)
		self.gs2 = gridspec.GridSpec(2,3)
		
		#Make the figure, put in a canvas and make the toolbar
		self.fig = plt.figure(figsize=(12,6))
		#
		self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab_jvresults_plot_frame)
		self.canvas.get_tk_widget().grid(row=0)
		self.canvas._tkcanvas.grid(row=1)
		self.ax = self.fig.add_subplot(self.gs[0])
		self.box = self.ax.get_position()
		self.ax.set_position([self.box.x0, self.box.y0, self.box.width * 0.8, self.box.height])
		# Put a legend to the right of the current axis
		self.tab_jvresults_toolbar_frame = Frame(self.tab_jvresults_selec_frame)
		self.tab_jvresults_toolbar_frame.grid(row=11, column=0, columnspan=25)
		self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.tab_jvresults_toolbar_frame)
		self.canvas.mpl_connect('key_press_event', self.on_key_event)
		self.canvas.mpl_connect('pick_event', self.on_pick)
		
		line, = self.ax.plot(numpy.random.rand(100), 'o', picker=5, label='Noise')
		self.ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
		
		
		
		##### For the jv plots ############
		self.tab_jvresults_jv_plot_para_frame = LabelFrame(self.tab_jvresults_selec_frame, text='JV Plot Selections')
		self.tab_jvresults_jv_plot_para_frame.grid(row=13, column=0, sticky=SW, columnspan=25)
		
		###### combo box for light dark both #######
		self.tab_jvresults_jv_light_box_var = StringVar()
		self.tab_jvresults_jv_light_box_list = ['Light Only', 'Dark Only', 'Both']
		self.tab_jvresults_jv_light_box = Combobox(self.tab_jvresults_jv_plot_para_frame, textvariable=self.tab_jvresults_jv_light_box_var, width=15)
		self.tab_jvresults_jv_light_box.bind('<<ComboboxSelected>>')
		self.tab_jvresults_jv_light_box['values'] = self.tab_jvresults_jv_light_box_list
		self.tab_jvresults_jv_light_box.grid(row=0, column=0, sticky=W)
		self.tab_jvresults_jv_light_box.state(['readonly'])
		self.tab_jvresults_jv_light_box.current(0)
		
		self.tab_jvresults_jv_log_box_var = StringVar()
		self.tab_jvresults_jv_log_box_list = ['Linear', 'Semi-log']
		self.tab_jvresults_jv_log_box = Combobox(self.tab_jvresults_jv_plot_para_frame, textvariable=self.tab_jvresults_jv_log_box_var, width=15)
		self.tab_jvresults_jv_log_box.bind('<<ComboboxSelected>>')
		self.tab_jvresults_jv_log_box['values'] = self.tab_jvresults_jv_log_box_list
		self.tab_jvresults_jv_log_box.grid(row=0, column=1, sticky=W)
		self.tab_jvresults_jv_log_box.state(['readonly'])
		self.tab_jvresults_jv_log_box.current(0)
		
		self.tab_jvresults_jv_iv_box_var = StringVar()
		self.tab_jvresults_jv_iv_box_list = ['Current Density', 'Current']
		self.tab_jvresults_jv_iv_box = Combobox(self.tab_jvresults_jv_plot_para_frame, textvariable=self.tab_jvresults_jv_iv_box_var, width=15)
		self.tab_jvresults_jv_iv_box.bind('<<ComboboxSelected>>')
		self.tab_jvresults_jv_iv_box['values'] = self.tab_jvresults_jv_iv_box_list
		self.tab_jvresults_jv_iv_box.grid(row=0, column=2, sticky=W)
		self.tab_jvresults_jv_iv_box.state(['readonly'])
		self.tab_jvresults_jv_iv_box.current(0)
		
		self.tab_jvresults_jv_marker_check_var = IntVar()
		self.tab_jvresults_jv_marker_check = Checkbutton(self.tab_jvresults_jv_plot_para_frame, text='Plot Markers?', variable=self.tab_jvresults_jv_marker_check_var)
		self.tab_jvresults_jv_marker_check.grid(row=0, column=3) 
		
		self.tab_jvresults_jv_av_check_var = IntVar()
		self.tab_jvresults_jv_av_check = Checkbutton(self.tab_jvresults_jv_plot_para_frame, text='Plot Average JVs?', variable=self.tab_jvresults_jv_av_check_var)
		self.tab_jvresults_jv_av_check.grid(row=1, column=0)
		
		self.tab_jvresults_jv_stat_check_var = IntVar()
		self.tab_jvresults_jv_stat_check = Checkbutton(self.tab_jvresults_jv_plot_para_frame, text='Plot JVs by Status?', variable=self.tab_jvresults_jv_stat_check_var)
		self.tab_jvresults_jv_stat_check.grid(row=2, column=0)
		
		self.tab_jvresults_jv_plot_but = Button(self.tab_jvresults_jv_plot_para_frame, text='Plot JV Curves', command=self.tab_jvresults_plot_jv_plot_function)
		self.tab_jvresults_jv_plot_but.grid(row=3, column=0, sticky=W)
		
		 
		##### For the scan exclusion bits ############
		self.tab_jvresults_jv_plot_exclu_frame = LabelFrame(self.tab_jvresults_selec_frame, text='Update Scan Status')
		self.tab_jvresults_jv_plot_exclu_frame.grid(row=12, column=0, sticky=SW, columnspan=10)
		
		self.tab_jvresults_comp_selected_id_lab_var = StringVar()
		self.tab_jvresults_selected_id_entry = Entry(self.tab_jvresults_jv_plot_exclu_frame, textvariable=self.tab_jvresults_comp_selected_id_lab_var, width=20,state='readonly')
		self.tab_jvresults_selected_id_entry.grid(row=0, column=0, columnspan=2, sticky=W)
		self.tab_jvresults_comp_selected_id_lab_var.set('Selected scan ID = ?')
		###### combo box for scan status #######
		self.tab_jvresults_scan_status_var = StringVar()
		self.tab_jvresults_scan_status_list = ['Short', 'Shunt', 'Measurement Failure', 'Crosstalk', 'Area over', 'Area under', 'ok']
		self.tab_jvresults_scan_status_box = Combobox(self.tab_jvresults_jv_plot_exclu_frame, textvariable=self.tab_jvresults_scan_status_var, width=15)
		self.tab_jvresults_scan_status_box.bind('<<ComboboxSelected>>')
		self.tab_jvresults_scan_status_box['values'] = self.tab_jvresults_scan_status_list
		self.tab_jvresults_scan_status_box.grid(row=0, column=1, sticky=W)
		self.tab_jvresults_scan_status_box.state(['readonly'])
		self.tab_jvresults_scan_status_box.current(0)
		
		self.tab_jvresults_scan_status_but = Button(self.tab_jvresults_jv_plot_exclu_frame, text='Update Scan Status', command=self.tab_jvresults_scan_status_selection)
		self.tab_jvresults_scan_status_but.grid(row=0, column=2, sticky=W)
		
		self.tab_jvresults_all_scan_status_but = Button(self.tab_jvresults_jv_plot_exclu_frame, text='Update Pixel Scan Status', command=self.tab_jvresults_all_pixel_scan_status_selection)
		self.tab_jvresults_all_scan_status_but.grid(row=0, column=3, sticky=W)
		
		
		self.tab_jvresults_scan_dark_but = Button(self.tab_jvresults_jv_plot_exclu_frame, text='Mark As Dark Scan', command=self.tab_jvresults_scan_dark_mark)
		self.tab_jvresults_scan_dark_but.grid(row=1, column=0, sticky=W)
		
		self.tab_jvresults_scan_light_but = Button(self.tab_jvresults_jv_plot_exclu_frame, text='Mark As Light Scan', command=self.tab_jvresults_scan_light_mark)
		self.tab_jvresults_scan_light_but.grid(row=1, column=1, sticky=W)
		
		self.tab_jvresults_set_light_level_lab = Label(self.tab_jvresults_jv_plot_exclu_frame, text='Update Scan Light Level:')
		self.tab_jvresults_set_light_level_lab.grid(row=1, column=2, sticky=W)
		
		self.tab_jvresults_set_light_level_spinbox_var = StringVar()
		self.tab_jvresults_set_light_level_spinbox = Spinbox(self.tab_jvresults_jv_plot_exclu_frame, from_=0, to=99, format="%.5f", increment=0.00001, textvariable=self.tab_jvresults_set_light_level_spinbox_var, width=15) 
		self.tab_jvresults_set_light_level_spinbox.grid(row=1, column=3, sticky=E)
		self.tab_jvresults_set_light_level_spinbox_var.set(0.0)
		
		self.tab_jvresults_scan_all_dark_but = Button(self.tab_jvresults_jv_plot_exclu_frame, text='Mark ALL Dark Scans', command=self.tab_jvresults_scan_dark_mark_all)
		self.tab_jvresults_scan_all_dark_but.grid(row=2, column=0, sticky=W)
		
		self.tab_jvresults_scan_all_light_but = Button(self.tab_jvresults_jv_plot_exclu_frame, text='Mark ALL Light Scans', command=self.tab_jvresults_scan_light_mark_all)
		self.tab_jvresults_scan_all_light_but.grid(row=2, column=1, sticky=E)
		
		
		
		##### for jv plot ########
		self.tab_jvresults_jv_plot_frame = LabelFrame(self.tab_jvresults_selec_frame, text='JV Plot')
		self.tab_jvresults_jv_plot_frame.grid(row=14, column=0, sticky=SW, columnspan=25)
		
		self.jv_fig = plt.figure('jvplot', figsize=(12,6))
		self.jv_canvas = FigureCanvasTkAgg(self.jv_fig, master=self.tab_jvresults_jv_plot_frame)
		self.jv_canvas.get_tk_widget().grid(row=0)
		self.jv_canvas._tkcanvas.grid(row=1)
		self.jv_ax = self.jv_fig.add_subplot(111)
		self.jv_box = self.jv_ax.get_position()
		self.jv_ax.set_position([self.jv_box.x0, self.jv_box.y0, self.jv_box.width * 0.8, self.jv_box.height])
		self.tab_jvresults_jv_toolbar_frame = Frame(self.tab_jvresults_selec_frame)
		self.tab_jvresults_jv_toolbar_frame.grid(row=15, column=0, columnspan=25)
		self.jv_toolbar = NavigationToolbar2TkAgg(self.jv_canvas, self.tab_jvresults_jv_toolbar_frame)
		
		self.jv_canvas.mpl_connect('key_press_event', self.on_key_event_jv)
		self.jv_canvas.mpl_connect('pick_event', self.on_pick_jv)
		
		line, = self.jv_ax.plot(numpy.random.rand(100), 'o', picker=5, label='Noise')
		self.jv_ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	
	def tab_jvresults_scan_dark_mark_all(self,*args):
		
		result = tkMessageBox.askyesno("Mark ALL scans dark?", "Do you want to mark ALL scans dark?", icon='warning')

		if result == True:
			####get all the scan ids
			selection = self.tab_jvresults_scan_listbox.curselection()
			scan_ids = []
			for i in selection:
				scan_id = self.tab_jvresults_scan_listbox.get(i)
				scan_ids.append(scan_id)
			##the scan status
			dark_light = 0
			### Update the scan status in database#########
			for i in scan_ids:
				self.conn.execute('UPDATE jv_scan_results SET dark_light = ?, sun_equiv = ? WHERE id = ?',(dark_light, 0, i,));
				###check this doesn;t cause other problems
				self.conn.commit()
		else:
			print "Cancelled"
		
	
	def tab_jvresults_scan_light_mark_all(self,*args):
		result = tkMessageBox.askyesno("Mark ALL scans light?", 'Do you want to mark ALL scans light?\nWill be marked as %s sun light intensity' % (self.tab_jvresults_set_light_level_spinbox_var.get()), icon='warning')

		if result == True:
			####get all the scan ids
			selection = self.tab_jvresults_scan_listbox.curselection()
			scan_ids = []
			for i in selection:
				scan_id = self.tab_jvresults_scan_listbox.get(i)
				scan_ids.append(scan_id)
			##the scan status
			dark_light = 1
			### Update the scan status in database#########
			for i in scan_ids:
				self.conn.execute('UPDATE jv_scan_results SET dark_light = ?, sun_equiv = ? WHERE id = ?',(dark_light, self.tab_jvresults_set_light_level_spinbox_var.get(), i,));
				###check this doesn;t cause other problems
				self.conn.commit()
		else:
			print "Cancelled" 
					
	def tab_jvresults_scan_dark_mark(self,*args):
		###Check if a scan has been selected #####
		scan_exist = self.tab_jvresults_comp_selected_id_lab_var.get()
		### scan status
		dark_light = 0
		### Update the scan status in database#########
		if scan_exist.isdigit():
			##needed???
			scan_exist = int(scan_exist)
			self.conn.execute('UPDATE jv_scan_results SET dark_light = ?, sun_equiv = ? WHERE id = ?',(dark_light, 0, scan_exist,));
			###check this doesn;t cause other problems
			self.conn.commit()
	def tab_jvresults_scan_light_mark(self,*args):
		
		###Check if a scan has been selected #####
		scan_exist = self.tab_jvresults_comp_selected_id_lab_var.get()
		### Get the scan status from the combo########
		dark_light = 1
		### Update the scan status in database#########
		if scan_exist.isdigit():
			##needed???
			scan_exist = int(scan_exist)
			result = tkMessageBox.askyesno("Mark single scan light?", 'Do you want to mark scan (%s) light?\nWill be marked as %s sun light intensity' % (scan_exist,self.tab_jvresults_set_light_level_spinbox_var.get()), icon='warning')
			if result == True:
				self.conn.execute('UPDATE jv_scan_results SET dark_light = ? WHERE id = ?',(dark_light, scan_exist,));
				###check this doesn;t cause other problems
				self.conn.commit()
		else:
			print 'Cancelled'
	def tab_jvresults_scan_status_selection(self, *args):
		###Check if a scan has been selected #####
		scan_exist = self.tab_jvresults_comp_selected_id_lab_var.get()
		### Get the scan status from the combo########
		scan_status = self.tab_jvresults_scan_status_box.get()
		### Update the scan status in database#########
		if scan_exist.isdigit():
			##needed???
			scan_exist = int(scan_exist)
			self.conn.execute('UPDATE jv_scan_results SET scan_status = ? WHERE id = ?',(scan_status, scan_exist,));
			###check this doesn;t cause other problems
			self.conn.commit()
			
	def tab_jvresults_all_pixel_scan_status_selection(self, *args):
		###Check if a scan has been selected #####
		scan_exist = self.tab_jvresults_comp_selected_id_lab_var.get()
		### Get the scan status from the combo########
		scan_status = self.tab_jvresults_scan_status_box.get()
		### Find which pixel corresponds the scan is from (the dev_id)#########
		if scan_exist.isdigit():
			##needed???
			scan_exist = int(scan_exist)
			dev_id_select = self.conn.execute('SELECT dev_id FROM jv_scan_results WHERE id = ?',(scan_exist,));
			dev_id_select_result = dev_id_select.fetchone()[0]
			
			#Use the dev_id to find the batch number and split etc...
			code_select = self.conn.execute('SELECT batch, split, device, pixel FROM dev_ids WHERE id = ?',(dev_id_select_result,));
			code_select_result = code_select.fetchone()
			#Ask if you really want to do this...
			result = tkMessageBox.askyesno("Update Status for ALL scans of pixel?", 'Do you want to update the status of all scans with dev_id (%s) (B%sS%sD%sP%s)?\nEvery scan in database for pixel will be marked as %s' % (dev_id_select_result,code_select_result[0],code_select_result[1],code_select_result[2],code_select_result[3],scan_status), icon='warning')
			if result == True:
				#Find all the scans that have that dev_id
				scan_ids_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE dev_id = ?',(dev_id_select_result,));
				scan_ids_select_results = scan_ids_select.fetchall()
				#Go through the scans and update the status...
				for i in scan_ids_select_results:
					i = i[0]
					self.conn.execute('UPDATE jv_scan_results SET scan_status = ? WHERE id = ?',(scan_status, i,));
				
				###commit it 
				self.conn.commit()
			else:
				print 'Update status cancelled'
				
	def update_jvresults_selec_combo(self, *args):
		self.tab_jvresults_selec_list = []
		self.tab_jvresults_selec_box.set('')
		## get the name of the device stacks ###
		tab_jvresults_select = self.conn.execute('SELECT selection_name FROM data_selection')
		tab_jvresults_select_results = tab_jvresults_select.fetchall()
		
		if tab_jvresults_select_results:	
			for i in tab_jvresults_select_results:
				if str(i[0]):
					self.tab_jvresults_selec_list.append(i[0])
		self.tab_jvresults_selec_list = list(reversed(self.tab_jvresults_selec_list))			
		self.tab_jvresults_selec_box['values'] = self.tab_jvresults_selec_list
		
	def update_jvresults_selec_info(self, *args):
		pass
	def tab_jvresults_save_selection(self, *args):
		###### check if the selection name already exists #######	
		selec_exists_select = self.conn.execute('SELECT id FROM data_selection WHERE selection_name = ?', (self.tab_jvresults_selec_entry.get(),))
		selec_exists_select_result = selec_exists_select.fetchall()
		
		if selec_exists_select_result:
			self.tab_jvresults_selec_lab_var.set('Status: Selection name already exists.')
		else:
			selection = self.tab_jvresults_scan_listbox.curselection()
			scan_ids = []
			for i in selection:
				scan_id = self.tab_jvresults_scan_listbox.get(i)
				scan_ids.append(scan_id)
			device_batch_dict = {
						'selection_name':self.tab_jvresults_selec_entry.get(),
						'selection':str(scan_ids),
						}
		
			function_name = 'data_selection'
			selec_inserted = self.materials_mod(self, device_batch_dict, function_name, self.conn)	
			self.tab_jvresults_selec_lab_var.set("Status: Data selection inserted.")
			self.update_jvresults_selec_combo()	
	
	def tab_jvresults_merge_selection(self, *args):
		selec_exists_select = self.conn.execute('SELECT id FROM data_selection WHERE selection_name = ?', (self.tab_jvresults_selec_box.get(),))
		selec_exists_select_result = selec_exists_select.fetchall()
		
		if selec_exists_select_result:
			selec_fetch = self.conn.execute('SELECT selection FROM data_selection WHERE selection_name = ?', (self.tab_jvresults_selec_box.get(),))
			selec_fetch_result = selec_fetch.fetchall()
			
			if selec_fetch_result:
				#To merge just don't clear the previous
				#self.tab_jvresults_scan_listbox.delete(0,END)
				scan_ids = ast.literal_eval(selec_fetch_result[0][0])
				scan_ids = list(scan_ids)
				scan_ids = map(int, scan_ids)
				scan_ids = sorted(scan_ids)
				
				for i in scan_ids:
					i = str(i)
					self.tab_jvresults_scan_listbox.insert(END, i)
				self.tab_jvresults_scan_listbox.select_set(0,END)
				self.tab_jvresults_split_listbox.delete(0,END)
				self.tab_jvresults_device_listbox.delete(0,END)
				self.tab_jvresults_pixel_listbox.delete(0,END)
				self.tab_jvresults_area_listbox.delete(0,END)
				self.tab_jvresults_source_listbox.delete(0,END)
				self.tab_jvresults_suns_listbox.delete(0,END)
				self.tab_jvresults_soak_time_listbox.delete(0,END)
				self.tab_jvresults_soak_suns_listbox.delete(0,END)
				self.tab_jvresults_lux_listbox.delete(0,END)
				self.tab_jvresults_time_listbox.delete(0,END)
				self.tab_jvresults_rate_listbox.delete(0,END)
				self.tab_jvresults_selec_lab_var.set('Status: Selection loaded.')
			else:
				self.tab_jvresults_selec_lab_var.set('Status: No selection loaded.')
		else:
			self.tab_jvresults_selec_lab_var.set('Status: No selection loaded.')
				
	def tab_jvresults_load_selection(self, *args):
		selec_exists_select = self.conn.execute('SELECT id FROM data_selection WHERE selection_name = ?', (self.tab_jvresults_selec_box.get(),))
		selec_exists_select_result = selec_exists_select.fetchall()
		
		if selec_exists_select_result:
			selec_fetch = self.conn.execute('SELECT selection FROM data_selection WHERE selection_name = ?', (self.tab_jvresults_selec_box.get(),))
			selec_fetch_result = selec_fetch.fetchall()
			
			if selec_fetch_result:
				self.tab_jvresults_scan_listbox.delete(0,END)
				scan_ids = ast.literal_eval(selec_fetch_result[0][0])
				scan_ids = list(scan_ids)
				scan_ids = map(int, scan_ids)
				scan_ids = sorted(scan_ids)
				
				for i in scan_ids:
					i = str(i)
					self.tab_jvresults_scan_listbox.insert(END, i)
				self.tab_jvresults_scan_listbox.select_set(0,END)
				self.tab_jvresults_split_listbox.delete(0,END)
				self.tab_jvresults_device_listbox.delete(0,END)
				self.tab_jvresults_pixel_listbox.delete(0,END)
				self.tab_jvresults_area_listbox.delete(0,END)
				self.tab_jvresults_source_listbox.delete(0,END)
				self.tab_jvresults_suns_listbox.delete(0,END)
				self.tab_jvresults_soak_time_listbox.delete(0,END)
				self.tab_jvresults_soak_suns_listbox.delete(0,END)
				self.tab_jvresults_lux_listbox.delete(0,END)
				self.tab_jvresults_time_listbox.delete(0,END)
				self.tab_jvresults_rate_listbox.delete(0,END)
				self.tab_jvresults_selec_lab_var.set('Status: Selection loaded.')
			else:
				self.tab_jvresults_selec_lab_var.set('Status: No selection loaded.')
		else:
			self.tab_jvresults_selec_lab_var.set('Status: No selection loaded.')
	def tab_jvresults_refresh_selection(self, *args):		
		##### get the scan ids from the list box
		selection = self.tab_jvresults_scan_listbox.curselection()
		scan_ids = []
		for i in selection:
			scan_id = self.tab_jvresults_scan_listbox.get(i)
			scan_ids.append(scan_id)
		##### empty the current items in the listbox 
		self.tab_jvresults_scan_listbox.delete(0,END)
		
		if self.tab_jvresults_shunt_var.get() == True:
				##### Filter scan ids by shunt or not ######
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					shunt = 'Shunt'
					### get the shunt scans then remove them from the list
					shunt_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_status = ?', (scan_id, shunt,))
					shunt_filter_select_result = shunt_filter_select.fetchall()

					if not shunt_filter_select_result:
						pass
					else:	
						filtered_scans.append(shunt_filter_select_result[0])
				filtered_scans = [i[0] for i in filtered_scans]
				#### this is a list of 		
				scan_ids = [int(x) for x in scan_ids if x not in filtered_scans]
				
		if self.tab_jvresults_short_var.get() == True:
				##### Filter scan ids by shunt or not ######
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					s = 'Short'
					### get the shunt scans then remove them from the list
					short_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_status = ?', (scan_id, s,))
					short_filter_select_result = short_filter_select.fetchall()

					if not short_filter_select_result:
						pass
					else:	
						filtered_scans.append(short_filter_select_result[0])
						
				filtered_scans = [i[0] for i in filtered_scans]
				#### this is a list of 		
				scan_ids = [int(x) for x in scan_ids if x not in filtered_scans]
				
		if self.tab_jvresults_under_var.get() == True:
				##### Filter scan ids by shunt or not ######
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					s = 'Area under'
					### get the shunt scans then remove them from the list
					s_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_status = ?', (scan_id, s,))
					s_filter_select_result = s_filter_select.fetchall()

					if not s_filter_select_result:
						pass
					else:	
						filtered_scans.append(s_filter_select_result[0])
				filtered_scans = [i[0] for i in filtered_scans]
				#### this is a list of 		
				scan_ids = [int(x) for x in scan_ids if x not in filtered_scans]
		
		if self.tab_jvresults_over_var.get() == True:
				##### Filter scan ids by shunt or not ######
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					s = 'Area over'
					### get the shunt scans then remove them from the list
					s_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_status = ?', (scan_id, s,))
					s_filter_select_result = s_filter_select.fetchall()

					if not s_filter_select_result:
						pass
					else:	
						filtered_scans.append(s_filter_select_result[0])
				filtered_scans = [i[0] for i in filtered_scans]
				#### this is a list of 		
				scan_ids = [int(x) for x in scan_ids if x not in filtered_scans]
		
		if self.tab_jvresults_cross_var.get() == True:
				##### Filter scan ids by shunt or not ######
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					s = 'Crosstalk'
					### get the shunt scans then remove them from the list
					s_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_status = ?', (scan_id, s,))
					s_filter_select_result = s_filter_select.fetchall()

					if not s_filter_select_result:
						pass
					else:	
						filtered_scans.append(s_filter_select_result[0])
				filtered_scans = [i[0] for i in filtered_scans]
				#### this is a list of 		
				scan_ids = [int(x) for x in scan_ids if x not in filtered_scans]
		
		if self.tab_jvresults_fail_var.get() == True:
				##### Filter scan ids by shunt or not ######
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					s = 'Measurement Failure'
					### get the shunt scans then remove them from the list
					s_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_status = ?', (scan_id, s,))
					s_filter_select_result = s_filter_select.fetchall()

					if not s_filter_select_result:
						pass
					else:	
						filtered_scans.append(s_filter_select_result[0])
				filtered_scans = [i[0] for i in filtered_scans]
				#### this is a list of 		
				scan_ids = [int(x) for x in scan_ids if x not in filtered_scans]
				
		if self.tab_jvresults_ok_var.get() == True:
				##### Filter scan ids by shunt or not ######
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					s = 'ok'
					### get the shunt scans then remove them from the list
					s_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_status = ?', (scan_id, s,))
					s_filter_select_result = s_filter_select.fetchall()

					if not s_filter_select_result:
						pass
					else:	
						filtered_scans.append(s_filter_select_result[0])
				filtered_scans = [i[0] for i in filtered_scans]
				#### this is a list of 		
				scan_ids = [int(x) for x in scan_ids if x not in filtered_scans]
						
		if self.tab_jvresults_check_rate_var.get() == True:
			### Get the rate and range		
			scan_rate = float(self.tab_jvresults_para_rate_spinbox.get())
			scan_tol = float(self.tab_jvresults_para_rate_tol_spinbox.get())
			max_scan_rate = scan_rate + (scan_rate*(scan_tol/100))
			min_scan_rate = scan_rate - (scan_rate*(scan_tol/100))
			#### filter the ids by the rate range ####
			
			filtered_scans = []
			for i in scan_ids:
				scan_id = i
				### if the scan id is light it will be returned add to the list of scan_ids
				rate_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_rate BETWEEN ? AND ?', (scan_id, min_scan_rate, max_scan_rate,))
				rate_filter_select_result = rate_filter_select.fetchall()
				
				if not rate_filter_select_result:
					pass
				else:	
					filtered_scans.append(rate_filter_select_result[0])
					
			scan_ids = filtered_scans
			scan_ids = [i[0] for i in scan_ids]
			
		if self.tab_jvresults_check_sun_var.get() == True:
			##### get the light intensity and range
			light_level = float(self.tab_jvresults_para_level_spinbox.get())
			level_tol = float(self.tab_jvresults_para_level_tol_spinbox.get())
			max_level = light_level + (light_level*(level_tol/100))
			min_level = light_level - (light_level*(level_tol/100))
			
			filtered_scans = []
			for i in scan_ids:
				scan_id = i
				### if the scan id is light it will be returned add to the list of scan_ids
				level_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND sun_equiv BETWEEN ? AND ?', (scan_id, min_level, max_level,))
				level_filter_select_result = level_filter_select.fetchall()
				
				if not level_filter_select_result:
					pass
				else:	
					filtered_scans.append(level_filter_select_result[0])
					
			scan_ids = filtered_scans
			scan_ids = [i[0] for i in scan_ids]	
		
		if self.tab_jvresults_check_il_var.get() == True:
			if str(self.tab_jvresults_para_light_box.get()) == 'Light Only':
				dark_light = 1
				##### Filter scan ids by the light dark ######
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					### if the scan id is light it will be returned add to the list of scan_ids
					light_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND dark_light = ?', (scan_id, dark_light,))
					light_filter_select_result = light_filter_select.fetchall()

					if not light_filter_select_result:
						pass
					else:	
						filtered_scans.append(light_filter_select_result[0])
				
				#### this is a list of 		
				scan_ids = filtered_scans
				scan_ids = [i[0] for i in scan_ids]
				
			if str(self.tab_jvresults_para_light_box.get()) == 'Dark Only':
				dark_light = 0
				##### Filter scan ids by the light dark ######
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					### if the scan id is light it will be returned add to the list of scan_ids
					dark_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND dark_light = ?', (scan_id, dark_light,))
					dark_filter_select_result = dark_filter_select.fetchall()
					
					if not dark_filter_select_result:
						pass
					else:	
						filtered_scans.append(dark_filter_select_result[0])
				scan_ids = filtered_scans
				scan_ids = [i[0] for i in scan_ids]
		
		if self.tab_jvresults_check_dir_var.get() == True:	
			if str(self.tab_jvresults_para_direc_box.get()) == 'Forward Only':
				scan_type = 'forward'
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					### if the scan id is light it will be returned add to the list of scan_ids
					forward_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_type = ?', (scan_id, scan_type,))
					forward_filter_select_result = forward_filter_select.fetchall()
					
					if not forward_filter_select_result:
						pass
					else:	
						filtered_scans.append(forward_filter_select_result[0])
				scan_ids = filtered_scans
				scan_ids = [i[0] for i in scan_ids]
				
			elif str(self.tab_jvresults_para_direc_box.get()) == 'Reverse Only':	
				scan_type = 'reverse'
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					### if the scan id is light it will be returned add to the list of scan_ids
					reverse_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_type = ?', (scan_id, scan_type,))
					reverse_filter_select_result = reverse_filter_select.fetchall()
					
					if not reverse_filter_select_result:
						pass
					else:	
						filtered_scans.append(reverse_filter_select_result[0])
				scan_ids = filtered_scans
				scan_ids = [i[0] for i in scan_ids]
				
		if self.tab_jvresults_check_first_last_var.get() == True:
			if str(self.tab_jvresults_para_first_last_box.get()) == 'First Scan Only':
				#For the selection of scans want the ones with the lowest or highest timestamp
				#Need to find which device each scan belongs to and then find the lowest timestamp for both forwards and reverse
				dev_ids_dict = {}
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					dev_ids_select = self.conn.execute('SELECT dev_id, time_stamp, scan_type FROM jv_scan_results WHERE id = ?', (scan_id,))
					dev_ids_result = dev_ids_select.fetchall()
					
					#Add each device id as a dict key with the timestamp and scan type
					if not dev_ids_result:
						pass
					else:
						if dev_ids_result[0][0] in dev_ids_dict:
							dev_ids_dict[dev_ids_result[0][0]].append((scan_id,dev_ids_result[0][1],dev_ids_result[0][2]))
						else:	
							dev_ids_dict[dev_ids_result[0][0]] = []
							dev_ids_dict[dev_ids_result[0][0]].append((scan_id,dev_ids_result[0][1],dev_ids_result[0][2]))
				#The dict contains both the forwards and reverse scans for each device
				#Split into two dicts for each
				forw_dev_ids_dict = {}
				rev_dev_ids_dict = {}
				for key in dev_ids_dict:
					for idx, i in enumerate(dev_ids_dict[key]):
						if dev_ids_dict[key][idx][2] == 'forward':
							if not key in forw_dev_ids_dict:
								forw_dev_ids_dict[key] = [dev_ids_dict[key][idx]]
							else:
								forw_dev_ids_dict[key].append(dev_ids_dict[key][idx])
						elif dev_ids_dict[key][idx][2] == 'reverse':
							if not key in rev_dev_ids_dict:
								rev_dev_ids_dict[key] = [dev_ids_dict[key][idx]]
							else:
								rev_dev_ids_dict[key].append(dev_ids_dict[key][idx])

				for key in rev_dev_ids_dict:
					ordered_scans = sorted(rev_dev_ids_dict[key], key=lambda tup: tup[1])
					first_scan = ordered_scans[0][0]
					filtered_scans.append(first_scan)

				for key in forw_dev_ids_dict:
					ordered_scans = sorted(forw_dev_ids_dict[key], key=lambda tup: tup[1])
					first_scan = ordered_scans[0][0]
					filtered_scans.append(first_scan)
				#### this is a list of 		
				scan_ids = filtered_scans
				
			elif str(self.tab_jvresults_para_first_last_box.get()) == 'Last Scan Only':
				##### Filter scan ids for the lowest scan id for each device######
				#Maybe there is a nicer way to do this, surely...
				#First get the device ids for the scans
				#Make a dictionary of the device ids and put each scan under the device
				#Choose the lowest scan for each dict and return to the scan id list
				filtered_scans = []
				#A set will be only the unique values
				dev_ids_dict = {}
				for i in scan_ids:
					scan_id = i
					dev_ids_select = self.conn.execute('SELECT dev_id, time_stamp, scan_type FROM jv_scan_results WHERE id = ?', (scan_id,))
					dev_ids_result = dev_ids_select.fetchall()

					if not dev_ids_result:
						pass
					else:
						if dev_ids_result[0][0] in dev_ids_dict:
							dev_ids_dict[dev_ids_result[0][0]].append((scan_id,dev_ids_result[0][1],dev_ids_result[0][2]))
						else:	
							dev_ids_dict[dev_ids_result[0][0]] = []
							dev_ids_dict[dev_ids_result[0][0]].append((scan_id,dev_ids_result[0][1],dev_ids_result[0][2]))
				
				forw_dev_ids_dict = {}
				rev_dev_ids_dict = {}
				for key in dev_ids_dict:
					for idx, i in enumerate(dev_ids_dict[key]):
						if dev_ids_dict[key][idx][2] == 'forward':
							if not key in forw_dev_ids_dict:
								forw_dev_ids_dict[key] = [dev_ids_dict[key][idx]]
							else:
								forw_dev_ids_dict[key].append(dev_ids_dict[key][idx])
						elif dev_ids_dict[key][idx][2] == 'reverse':
							if not key in rev_dev_ids_dict:
								rev_dev_ids_dict[key] = [dev_ids_dict[key][idx]]
							else:
								rev_dev_ids_dict[key].append(dev_ids_dict[key][idx])

				for key in rev_dev_ids_dict:
					ordered_scans = sorted(rev_dev_ids_dict[key], key=lambda tup: tup[1])
					first_scan = ordered_scans[-1][0]
					filtered_scans.append(first_scan)

				for key in forw_dev_ids_dict:
					ordered_scans = sorted(forw_dev_ids_dict[key], key=lambda tup: tup[1])
					first_scan = ordered_scans[-1][0]
					filtered_scans.append(first_scan)
				#### this is a list of 		
				scan_ids = filtered_scans
		
		scan_ids = list(scan_ids)
		scan_ids = map(int, scan_ids)
		scan_ids = sorted(scan_ids)		
		for i in scan_ids:
			i = str(i)
			self.tab_jvresults_scan_listbox.insert(END, i)
		self.tab_jvresults_scan_listbox.select_set(0,END)
			
	def tab_jvresults_plot_get_scan_ids(self, *args):
		##### get the scan ids from the list box
		selection = self.tab_jvresults_scan_listbox.curselection()
		scan_ids = []
		for i in selection:
			scan_id = self.tab_jvresults_scan_listbox.get(i)
			scan_ids.append(scan_id)
		##### get the parameters to filter the scans by
		##### at each step filter the scan ids
		
		##### make dictionarys for all the splits devices pixel etc in the scan_ids
		parameters_dict = {}

		 	
		dict_of_search_terms = {}
		if self.tab_jvresults_shunt_var.get() == True:
				##### Filter scan ids by shunt or not ######
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					shunt = 'Shunt'
					### get the shunt scans then remove them from the list
					shunt_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_status = ?', (scan_id, shunt,))
					shunt_filter_select_result = shunt_filter_select.fetchall()

					if not shunt_filter_select_result:
						pass
					else:	
						filtered_scans.append(shunt_filter_select_result[0])
				filtered_scans = [i[0] for i in filtered_scans]
				#### this is a list of 		
				scan_ids = [int(x) for x in scan_ids if x not in filtered_scans]
				
		if self.tab_jvresults_short_var.get() == True:
				##### Filter scan ids by shunt or not ######
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					s = 'Short'
					### get the shunt scans then remove them from the list
					short_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_status = ?', (scan_id, s,))
					short_filter_select_result = short_filter_select.fetchall()

					if not short_filter_select_result:
						pass
					else:	
						filtered_scans.append(short_filter_select_result[0])
				filtered_scans = [i[0] for i in filtered_scans]
				#### this is a list of 		
				scan_ids = [int(x) for x in scan_ids if x not in filtered_scans]
		
		if self.tab_jvresults_under_var.get() == True:
				##### Filter scan ids by shunt or not ######
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					s = 'Area under'
					### get the shunt scans then remove them from the list
					s_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_status = ?', (scan_id, s,))
					s_filter_select_result = s_filter_select.fetchall()

					if not s_filter_select_result:
						pass
					else:	
						filtered_scans.append(s_filter_select_result[0])
				filtered_scans = [i[0] for i in filtered_scans]
				#### this is a list of 		
				scan_ids = [int(x) for x in scan_ids if x not in filtered_scans]
		
		if self.tab_jvresults_over_var.get() == True:
				##### Filter scan ids by shunt or not ######
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					s = 'Area over'
					### get the shunt scans then remove them from the list
					s_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_status = ?', (scan_id, s,))
					s_filter_select_result = s_filter_select.fetchall()

					if not s_filter_select_result:
						pass
					else:	
						filtered_scans.append(s_filter_select_result[0])
				filtered_scans = [i[0] for i in filtered_scans]
				#### this is a list of 		
				scan_ids = [int(x) for x in scan_ids if x not in filtered_scans]
		
		if self.tab_jvresults_cross_var.get() == True:
				##### Filter scan ids by shunt or not ######
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					s = 'Crosstalk'
					### get the shunt scans then remove them from the list
					s_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_status = ?', (scan_id, s,))
					s_filter_select_result = s_filter_select.fetchall()

					if not s_filter_select_result:
						pass
					else:	
						filtered_scans.append(s_filter_select_result[0])
				filtered_scans = [i[0] for i in filtered_scans]
				#### this is a list of 		
				scan_ids = [int(x) for x in scan_ids if x not in filtered_scans]
		
		if self.tab_jvresults_fail_var.get() == True:
				##### Filter scan ids by shunt or not ######
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					s = 'Measurement Failure'
					### get the shunt scans then remove them from the list
					s_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_status = ?', (scan_id, s,))
					s_filter_select_result = s_filter_select.fetchall()

					if not s_filter_select_result:
						pass
					else:	
						filtered_scans.append(s_filter_select_result[0])
				filtered_scans = [i[0] for i in filtered_scans]
				#### this is a list of 		
				scan_ids = [int(x) for x in scan_ids if x not in filtered_scans]
		
		if self.tab_jvresults_ok_var.get() == True:
				##### Filter scan ids by shunt or not ######
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					s = 'ok'
					### get the shunt scans then remove them from the list
					s_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_status = ?', (scan_id, s,))
					s_filter_select_result = s_filter_select.fetchall()

					if not s_filter_select_result:
						pass
					else:	
						filtered_scans.append(s_filter_select_result[0])
				filtered_scans = [i[0] for i in filtered_scans]
				#### this is a list of 		
				scan_ids = [int(x) for x in scan_ids if x not in filtered_scans]
																
		if self.tab_jvresults_check_il_var.get() == True:	
			if str(self.tab_jvresults_para_light_box.get()) == 'Light Only':
				dark_light = 1
				##### Filter scan ids by the light dark ######
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					### if the scan id is light it will be returned add to the list of scan_ids
					light_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND dark_light = ?', (scan_id, dark_light,))
					light_filter_select_result = light_filter_select.fetchall()

					if not light_filter_select_result:
						pass
					else:	
						filtered_scans.append(light_filter_select_result[0])
				
				#### this is a list of 		
				scan_ids = filtered_scans
				scan_ids = [i[0] for i in scan_ids]
				
			if str(self.tab_jvresults_para_light_box.get()) == 'Dark Only':
				dark_light = 0
				##### Filter scan ids by the light dark ######
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					### if the scan id is light it will be returned add to the list of scan_ids
					dark_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND dark_light = ?', (scan_id, dark_light,))
					dark_filter_select_result = dark_filter_select.fetchall()
					
					if not dark_filter_select_result:
						pass
					else:	
						filtered_scans.append(dark_filter_select_result[0])
				scan_ids = filtered_scans
				scan_ids = [i[0] for i in scan_ids]
		
		if self.tab_jvresults_check_dir_var.get() == True:	
			if str(self.tab_jvresults_para_direc_box.get()) == 'Forward Only':
				scan_type = 'forward'
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					### if the scan id is light it will be returned add to the list of scan_ids
					forward_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_type = ?', (scan_id, scan_type,))
					forward_filter_select_result = forward_filter_select.fetchall()
					
					if not forward_filter_select_result:
						pass
					else:	
						filtered_scans.append(forward_filter_select_result[0])
				scan_ids = filtered_scans
				scan_ids = [i[0] for i in scan_ids]
				
			elif str(self.tab_jvresults_para_direc_box.get()) == 'Reverse Only':	
				scan_type = 'reverse'
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					### if the scan id is light it will be returned add to the list of scan_ids
					reverse_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_type = ?', (scan_id, scan_type,))
					reverse_filter_select_result = reverse_filter_select.fetchall()
					
					if not reverse_filter_select_result:
						pass
					else:	
						filtered_scans.append(reverse_filter_select_result[0])
				scan_ids = filtered_scans
				scan_ids = [i[0] for i in scan_ids]
		
		if self.tab_jvresults_check_rate_var.get() == True:
			#### A bunch of filtered ids	
			### Get the rate and range		
			scan_rate = float(self.tab_jvresults_para_rate_spinbox.get())
			scan_tol = float(self.tab_jvresults_para_rate_tol_spinbox.get())
			max_scan_rate = scan_rate + (scan_rate*(scan_tol/100))
			min_scan_rate = scan_rate - (scan_rate*(scan_tol/100))
			#### filter the ids by the rate range ####
			
			filtered_scans = []
			for i in scan_ids:
				scan_id = i
				### if the scan id is light it will be returned add to the list of scan_ids
				rate_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_rate BETWEEN ? AND ?', (scan_id, min_scan_rate, max_scan_rate,))
				rate_filter_select_result = rate_filter_select.fetchall()
				
				if not rate_filter_select_result:
					pass
				else:	
					filtered_scans.append(rate_filter_select_result[0])
					
			scan_ids = filtered_scans
			scan_ids = [i[0] for i in scan_ids]
		
		if self.tab_jvresults_check_sun_var.get() == True:
			##### get the light intensity and range
			light_level = float(self.tab_jvresults_para_level_spinbox.get())
			level_tol = float(self.tab_jvresults_para_level_tol_spinbox.get())
			max_level = light_level + (light_level*(level_tol/100))
			min_level = light_level - (light_level*(level_tol/100))
			
			filtered_scans = []
			for i in scan_ids:
				scan_id = i
				### if the scan id is light it will be returned add to the list of scan_ids
				level_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND sun_equiv BETWEEN ? AND ?', (scan_id, min_level, max_level,))
				level_filter_select_result = level_filter_select.fetchall()
				
				if not level_filter_select_result:
					pass
				else:	
					filtered_scans.append(level_filter_select_result[0])
					
			scan_ids = filtered_scans
			scan_ids = [i[0] for i in scan_ids]
			
		if self.tab_jvresults_check_first_last_var.get() == True:
			if str(self.tab_jvresults_para_first_last_box.get()) == 'First Scan Only':
				#For the selection of scans want the ones with the lowest or highest timestamp
				#Need to find which device each scan belongs to and then find the lowest timestamp for both forwards and reverse
				dev_ids_dict = {}
				filtered_scans = []
				for i in scan_ids:
					scan_id = i
					dev_ids_select = self.conn.execute('SELECT dev_id, time_stamp, scan_type FROM jv_scan_results WHERE id = ?', (scan_id,))
					dev_ids_result = dev_ids_select.fetchall()
					
					#Add each device id as a dict key with the timestamp and scan type
					if not dev_ids_result:
						pass
					else:
						if dev_ids_result[0][0] in dev_ids_dict:
							dev_ids_dict[dev_ids_result[0][0]].append((scan_id,dev_ids_result[0][1],dev_ids_result[0][2]))
						else:	
							dev_ids_dict[dev_ids_result[0][0]] = []
							dev_ids_dict[dev_ids_result[0][0]].append((scan_id,dev_ids_result[0][1],dev_ids_result[0][2]))
				#The dict contains both the forwards and reverse scans for each device
				#Split into two dicts for each
				forw_dev_ids_dict = {}
				rev_dev_ids_dict = {}
				for key in dev_ids_dict:
					for idx, i in enumerate(dev_ids_dict[key]):
						if dev_ids_dict[key][idx][2] == 'forward':
							if not key in forw_dev_ids_dict:
								forw_dev_ids_dict[key] = [dev_ids_dict[key][idx]]
							else:
								forw_dev_ids_dict[key].append(dev_ids_dict[key][idx])
						elif dev_ids_dict[key][idx][2] == 'reverse':
							if not key in rev_dev_ids_dict:
								rev_dev_ids_dict[key] = [dev_ids_dict[key][idx]]
							else:
								rev_dev_ids_dict[key].append(dev_ids_dict[key][idx])

				for key in rev_dev_ids_dict:
					ordered_scans = sorted(rev_dev_ids_dict[key], key=lambda tup: tup[1])
					first_scan = ordered_scans[0][0]
					filtered_scans.append(first_scan)

				for key in forw_dev_ids_dict:
					ordered_scans = sorted(forw_dev_ids_dict[key], key=lambda tup: tup[1])
					first_scan = ordered_scans[0][0]
					filtered_scans.append(first_scan)
				#### this is a list of 		
				scan_ids = filtered_scans
				
			elif str(self.tab_jvresults_para_first_last_box.get()) == 'Last Scan Only':
				##### Filter scan ids for the lowest scan id for each device######
				#Maybe there is a nicer way to do this, surely...
				#First get the device ids for the scans
				#Make a dictionary of the device ids and put each scan under the device
				#Choose the lowest scan for each dict and return to the scan id list
				filtered_scans = []
				#A set will be only the unique values
				dev_ids_dict = {}
				for i in scan_ids:
					scan_id = i
					dev_ids_select = self.conn.execute('SELECT dev_id, time_stamp, scan_type FROM jv_scan_results WHERE id = ?', (scan_id,))
					dev_ids_result = dev_ids_select.fetchall()

					if not dev_ids_result:
						pass
					else:
						if dev_ids_result[0][0] in dev_ids_dict:
							dev_ids_dict[dev_ids_result[0][0]].append((scan_id,dev_ids_result[0][1],dev_ids_result[0][2]))
						else:	
							dev_ids_dict[dev_ids_result[0][0]] = []
							dev_ids_dict[dev_ids_result[0][0]].append((scan_id,dev_ids_result[0][1],dev_ids_result[0][2]))
				
				forw_dev_ids_dict = {}
				rev_dev_ids_dict = {}
				for key in dev_ids_dict:
					for idx, i in enumerate(dev_ids_dict[key]):
						if dev_ids_dict[key][idx][2] == 'forward':
							if not key in forw_dev_ids_dict:
								forw_dev_ids_dict[key] = [dev_ids_dict[key][idx]]
							else:
								forw_dev_ids_dict[key].append(dev_ids_dict[key][idx])
						elif dev_ids_dict[key][idx][2] == 'reverse':
							if not key in rev_dev_ids_dict:
								rev_dev_ids_dict[key] = [dev_ids_dict[key][idx]]
							else:
								rev_dev_ids_dict[key].append(dev_ids_dict[key][idx])

				for key in rev_dev_ids_dict:
					ordered_scans = sorted(rev_dev_ids_dict[key], key=lambda tup: tup[1])
					first_scan = ordered_scans[-1][0]
					filtered_scans.append(first_scan)

				for key in forw_dev_ids_dict:
					ordered_scans = sorted(forw_dev_ids_dict[key], key=lambda tup: tup[1])
					first_scan = ordered_scans[-1][0]
					filtered_scans.append(first_scan)
				#### this is a list of 		
				scan_ids = filtered_scans
				
		##### get the parameter to plot and the range
		parameter = self.tab_jvresults_comp_ypara_box.get()
		parameter_min = float(self.tab_jvresults_comp_ex_yless_spinbox.get())
		parameter_max = float(self.tab_jvresults_comp_ex_ymore_spinbox.get())
		
		if parameter == 'Parameter to Plot':
			pass
		else:	
			filtered_scans = []
			for i in scan_ids:
				scan_id = i
				### if the scan id is light it will be returned add to the list of scan_ids
				level_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND '+parameter+' BETWEEN ? AND ?', (scan_id, parameter_min, parameter_max))
				level_filter_select_result = level_filter_select.fetchall()
				
				if not level_filter_select_result:
					pass
				else:	
					filtered_scans.append(level_filter_select_result[0])
					
			scan_ids = filtered_scans
			scan_ids = [i[0] for i in scan_ids]
			
		all_scans = {}
		##### Now split the ids up depending on the plotting conditions
		if str(self.tab_jvresults_para_direc_box.get()) == 'Separate':
			scan_type = 'forward'
			forward_scans = []
			reverse_scans = []
			for i in scan_ids:
				scan_id = i
				### if the scan id is light it will be returned add to the list of scan_ids
				filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_type = ?', (scan_id, scan_type,))
				filter_select_result = filter_select.fetchall()
				
				if not filter_select_result:
					reverse_scans.append(scan_id)
				else:	
					forward_scans.append(scan_id)
					
			direc_scans = {'forward_scans':forward_scans, 'reverse_scans':reverse_scans}
	
		elif str(self.tab_jvresults_para_direc_box.get()) == 'Reverse Only':		
		#### If its not seperate and its forward only then filter the scan_ids and get forward only then check the light						
			scan_type = 'reverse'
			reverse_scans = []
			for i in scan_ids:
				scan_id = i
				### if the scan id is light it will be returned add to the list of scan_ids
				filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_type = ?', (scan_id, scan_type,))
				filter_select_result = filter_select.fetchall()
				
				if not filter_select_result:
					pass
				else:	
					reverse_scans.append(scan_id)
					
			direc_scans = {'reverse_scans':reverse_scans}
				
		elif str(self.tab_jvresults_para_direc_box.get()) == 'Forward Only':		
		#### If its not seperate and its forward only then filter the scan_ids and get forward only then check the light						
			scan_type = 'forward'
			forward_scans = []
			reverse_scans = []
			for i in scan_ids:
				scan_id = i
				### if the scan id is light it will be returned add to the list of scan_ids
				filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_type = ?', (scan_id, scan_type,))
				filter_select_result = filter_select.fetchall()
				
				if not filter_select_result:
					pass
				else:	
					forward_scans.append(scan_id)
					
			direc_scans = {'forward_scans':forward_scans}
		
		else:
			direc_scans = {'both_scans':scan_ids}

		####### Now filter the direc_scan results by the light
		all_scans = {}
		if str(self.tab_jvresults_para_light_box.get()) == 'Separate':	
			for key in direc_scans:
				scan_type = 1
				light_scans = []
				dark_scans = []
				for i in direc_scans['%s' % key]:
					scan_id = i
					### if the scan id is light it will be returned add to the list of scan_ids
					filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND dark_light = ?', (scan_id, scan_type,))
					filter_select_result = filter_select.fetchall()
					
					if not filter_select_result:
						dark_scans.append(scan_id)
					else:	
						light_scans.append(scan_id)
					
				if key == 'forward_scans':
					all_scans['light_forward'] = light_scans
					all_scans['dark_forward'] = dark_scans
				elif key == 'reverse_scans':		
					all_scans['light_reverse'] = light_scans
					all_scans['dark_reverse'] = dark_scans	
				else: 		
					all_scans['light_both'] = light_scans
					all_scans['dark_both'] = dark_scans		
		
		elif str(self.tab_jvresults_para_light_box.get()) == 'Light Only':
			for key in direc_scans:
				scan_type = 1
				light_scans = []
				for i in direc_scans['%s' % key]:
					scan_id = i
					### if the scan id is light it will be returned add to the list of scan_ids
					filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND dark_light = ?', (scan_id, scan_type,))
					filter_select_result = filter_select.fetchall()
					
					if not filter_select_result:
						pass
					else:	
						light_scans.append(scan_id)
					
				if key == 'forward_scans':
					all_scans['light_forward'] = light_scans
				elif key == 'reverse_scans':		
					all_scans['light_reverse'] = light_scans
				else: 		
					all_scans['light_both'] = light_scans
					
		elif str(self.tab_jvresults_para_light_box.get()) == 'Dark Only':
			for key in direc_scans:
				scan_type = 0
				dark_scans = []
				for i in direc_scans['%s' % key]:
					scan_id = i
					### if the scan id is light it will be returned add to the list of scan_ids
					filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND dark_light = ?', (scan_id, scan_type,))
					filter_select_result = filter_select.fetchall()
					
					if not filter_select_result:
						pass
					else:	
						dark_scans.append(scan_id)
					
				if key == 'forward_scans':
					all_scans['dark_forward'] = dark_scans
				elif key == 'reverse_scans':		
					all_scans['dark_reverse'] = dark_scans	
				else: 		
					all_scans['dark_both'] = dark_scans	
		else:
			for key in direc_scans:
				all_scans['grey_%s' % key] = direc_scans['%s' % key]
				
	
		##### use the all scans dict to plot the parameter	
		#### for each list of scans split the scans up into splits
		
		#### make empty dictionarys for all the variations of splits in the selection etc
		split_names = {}
		for key in all_scans:	
			for i in all_scans['%s' % key]:
				## from scan id get the dev id and from dev id get the split
				dev_id_select = self.conn.execute('SELECT dev_id FROM jv_scan_results WHERE id = ?', (i,))
				dev_id_select_result = dev_id_select.fetchone()[0]
				
				
				#### first the batch the devices are in #####
				batch_select = self.conn.execute('SELECT batch FROM dev_ids WHERE id = ?', (dev_id_select_result,))
				batch_select_result = batch_select.fetchone()[0]

				
				#### make a dictionary for this batch #####
				if '%s_batch_%s' % (key, batch_select_result) in parameters_dict:
					pass
				else:
					parameters_dict['%s_batch_%s' % (key, batch_select_result)] = []
					
				parameters_dict['%s_batch_%s' % (key, batch_select_result)].append(i)
				
				split_select = self.conn.execute('SELECT split FROM dev_ids WHERE id = ?', (dev_id_select_result,))
				split_select_result = split_select.fetchone()[0]
				split_num = str(split_select_result)
				
				#This is a bit more complicated now...
				#Get the split name from the splits table using the spilt_num and the 
				##### Use the batch and split to get the split name for this batch+split
				name_select = self.conn.execute('SELECT split_name FROM splits WHERE batch_id = ? AND split = ?', (batch_select_result,split_num,))
				name_select_result = name_select.fetchone()[0]
				
				split_names['batch_%s_split_%s' % (batch_select_result, split_select_result)] = name_select_result
				
				#### make a dictionary for this split #####
				if '%s_batch_%s_split_%s' % (key, batch_select_result, split_select_result) in parameters_dict:
					pass
				else:
					parameters_dict['%s_batch_%s_split_%s' % (key, batch_select_result, split_select_result)] = []
					
				parameters_dict['%s_batch_%s_split_%s' % (key, batch_select_result, split_select_result)].append(i)
				
				#### Now find the device the scan is in 
				
				device_select = self.conn.execute('SELECT device FROM dev_ids WHERE id = ?', (dev_id_select_result,))
				device_select_result = device_select.fetchone()[0]
			
				#### make a dictionary for this split_device #####
				if '%s_batch_%s_split_%s_device_%s' % (key, batch_select_result, split_select_result, device_select_result) in parameters_dict:
					pass
				else:
					parameters_dict['%s_batch_%s_split_%s_device_%s' % (key, batch_select_result, split_select_result, device_select_result)] = []
					
				parameters_dict['%s_batch_%s_split_%s_device_%s' % (key, batch_select_result, split_select_result, device_select_result)].append(i)
				
				#### And again for the pixel ######## Oh what a waste of space....
				
				pixel_select = self.conn.execute('SELECT pixel FROM dev_ids WHERE id = ?', (dev_id_select_result,))
				pixel_select_result = pixel_select.fetchone()[0]
			
				#### make a dictionary for this split_device_pixel #####
				if '%s_batch_%s_split_%s_device_%s_pixel_%s' % (key, batch_select_result, split_select_result, device_select_result, pixel_select_result) in parameters_dict:
					pass
				else:
					parameters_dict['%s_batch_%s_split_%s_device_%s_pixel_%s' % (key, batch_select_result, split_select_result, device_select_result, pixel_select_result)] = []
					
				parameters_dict['%s_batch_%s_split_%s_device_%s_pixel_%s' % (key, batch_select_result, split_select_result, device_select_result, pixel_select_result)].append(i)
					
		### the lists in parameters dicts now contian the scan_ids for plotting with
		### use these to plot each box 
		if str(self.tab_jvresults_comp_av_box.get()) == 'Split':
			#### plot the scans in the split dicts
			keys_to_plot = []
			for key in parameters_dict:
				if 'pixel' in str(key):
					pass
				elif 'device' in str(key):
					pass
				elif not 'split' in str(key):
					pass	
				else:
					keys_to_plot.append(str(key))	
						
		elif str(self.tab_jvresults_comp_av_box.get()) == 'Device':
			keys_to_plot = []
			for key in parameters_dict:
				if 'pixel' in str(key):
					pass
				elif not 'device' in str(key):
					pass
				else:
					keys_to_plot.append(str(key))	 	
		elif str(self.tab_jvresults_comp_av_box.get()) == 'Pixel':
			keys_to_plot = []
			for key in parameters_dict:
				if not 'pixel' in str(key):
					pass
				else:
					keys_to_plot.append(str(key))	
		else:
			print 'would this not be ugly?'
		
		#### now with the keys_to_plot and the parameters_dict the scans scan be plotted with plot function
		plot_dict = {}
		for key in keys_to_plot:
			if key in parameters_dict:
				plot_dict['%s' % key] = parameters_dict['%s' % key]	
		### order the dict
		
		
		return plot_dict, split_names	
		
	def search_sequence_numpy(self, arr,seq):
		# Store sizes of input array and sequence
		Na, Nseq = arr.size, seq.size

		# Range of sequence
		r_seq = numpy.arange(Nseq)

		# Create 2D array of sliding indices across entire length of input array.
		# Match up with the input sequence & get the matching starting indices.
		M = (arr[numpy.arange(Na-Nseq+1)[:,None] + r_seq] == seq).all(1)

		# Get the range of those indices as final output
		if M.any>0:
			return numpy.where(numpy.convolve(M,numpy.ones((Nseq),dtype=int))>0)[0]
		else:
			return []         # No match found
		
	def on_pick_jv(self, event):
		#First get the x and y data from the pick selection
		#What if two curves over lap? Won't find the data
		thisline = event.artist
		xdata = thisline.get_xdata()
		ydata = thisline.get_ydata()
		ind = int(event.ind)
		seq = ydata[ind-3:ind+3]
		#Then search each JV scan data set for those data points
		#Might clash
		
		## Get the scans selected
		selection = self.tab_jvresults_scan_listbox.curselection()
		scan_ids = []
		returned_scan_ids = []
		for i in selection:
			scan_id = self.tab_jvresults_scan_listbox.get(i)
			scan_ids.append(scan_id)
		### Each scan needs to have the data extracted from the datafile
		for i in scan_ids:	
			data_file_select = self.conn.execute('SELECT datafile FROM jv_scan_results WHERE id = ?', (i,))
			data_file_select_result = data_file_select.fetchone()[0]
			### Append the base file path to the file name 
			## The data structure needs to be BXX/SXX/filename.txt
			if not data_file_select_result:
				pass
			else:
				data_file_select_result = self.base_file_path + str(data_file_select_result)
				#Get the datafile file_type
				file_type_select = self.conn.execute('SELECT file_type FROM jv_scan_results WHERE id = ?', (i,))
				file_type_select_result = file_type_select.fetchone()[0]
				
				#Use the file_type to decide which columns of the datafile to plot	
				if file_type_select_result == 'Oriel':
					all_data = numpy.genfromtxt(data_file_select_result, skip_header=10, delimiter='\t', dtype=float, encoding='latin1')
					voltage_points = all_data[:,0]
					current_points = all_data[:,1]
				elif file_type_select_result == 'Swansea':
					all_data = numpy.genfromtxt(data_file_select_result, skip_header=10, delimiter='\t', dtype=float, encoding='latin1')
					voltage_points = all_data[:,0]
					current_points = all_data[:,2]
					#get to amps...
					current_points = numpy.divide(current_points, 1000)	
				elif file_type_select_result == 'TPV2':
					all_data = numpy.genfromtxt(data_file_select_result, skip_header=1, delimiter='\t', dtype=float, encoding='latin1')
					voltage_points = all_data[:,0]
					current_points = all_data[:,1]		
				#### Get the cell area form file or database
				area_select = self.conn.execute('SELECT cell_area FROM jv_scan_results WHERE id = ?', (i,))
				area_select_result = area_select.fetchone()[0]
				
				current_density_points = numpy.divide(numpy.multiply(current_points, 1000), float(area_select_result))
				 
				### for the semilog plot the current needs to be converted to log
				log_current = numpy.sqrt(numpy.square(current_points))
				log_current_density = numpy.sqrt(numpy.square(current_density_points))
				#print current_points
				if self.tab_jvresults_jv_iv_box.get() == 'Current Density':
					if self.tab_jvresults_jv_log_box.get() == 'Linear':
						arr = current_density_points
					else:
						arr = log_current_density
				else:
					if self.tab_jvresults_jv_log_box.get() == 'Linear':
						arr = current_points
					else:
						arr = log_current
						
				search_result = self.search_sequence_numpy(arr,seq)

				if not search_result.any():
					pass
				else:
					returned_scan_ids.append(i)
		### Find the scan id from the result, but what if two are the same????
		#Return the scan name
		if not returned_scan_ids:
			self.tab_jvresults_comp_selected_id_lab_var.set('Re-check selection')
		else:	
			long_string = "?"
			for i in returned_scan_ids:
				long_string = "%s" % (i)
			self.tab_jvresults_comp_selected_id_lab_var.set(long_string)
	def on_pick(self, event):
		thisline = event.artist
		ydata = thisline.get_ydata()
		ind = event.ind
		
		some_number = float(ydata[ind][0])
		### Find the scan id from the result, but what if two are the same????
		param = str(self.tab_jvresults_comp_ypara_box.get())
		scan_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE '+param+' = ?', (some_number,))
		scan_select_result = scan_select.fetchall()
			
		if not scan_select_result:
			self.tab_jvresults_comp_selected_id_lab_var.set('Check parameter')
		else:	
			for i in scan_select_result:
				self.tab_jvresults_comp_selected_id_lab_var.set('%s' % i[0])
	def tab_jvresults_pretty_box_selection_function(self, *args):
		#Get the scan ids
		plot_dict, split_names = self.tab_jvresults_plot_get_scan_ids()
		new_plot_dict = collections.OrderedDict(sorted(plot_dict.items()))
		
		file_name = "%sexport_selection_%s.txt" % (self.base_file_path, time.strftime("%Y_%m_%d_%H%M%S"))
		self.export_file_name = file_name
		#get the parameters 
		filtered_scans = []
		for key in new_plot_dict:			
			for scan in plot_dict['%s' % key]:
				### if the scan id is light it will be returned add to the list of scan_ids
				filter_select = self.conn.execute('SELECT * FROM jv_scan_results WHERE id = ?', (scan,))
				filter_select_result = filter_select.fetchall()
				
				if not filter_select_result:
					pass
				else:	
					#dev_id is the first in the tuple from filter_select result
					dev_id = int(filter_select_result[0][2])
					dev_select = self.conn.execute('SELECT batch, split, device, pixel FROM dev_ids WHERE id = ?', (dev_id,))
					dev_select_result = dev_select.fetchall()
					result = dev_select_result[0][:] + filter_select_result[0][:]
					filtered_scans.append(result)
		return filtered_scans
	def tab_jvresults_export_selection_function(self, *args):
		#Get the scan ids
		plot_dict, split_names = self.tab_jvresults_plot_get_scan_ids()
		new_plot_dict = collections.OrderedDict(sorted(plot_dict.items()))
		
		file_name = "%sexport_selection_%s.txt" % (self.base_file_path, time.strftime("%Y_%m_%d_%H%M%S"))
		self.export_file_name = file_name
		#get the parameters 
		filtered_scans = []
		for key in new_plot_dict:			
			for scan in plot_dict['%s' % key]:
				### if the scan id is light it will be returned add to the list of scan_ids
				filter_select = self.conn.execute('SELECT * FROM jv_scan_results WHERE id = ?', (scan,))
				filter_select_result = filter_select.fetchall()
				
				if not filter_select_result:
					pass
				else:	
					#dev_id is the first in the tuple from filter_select result
					dev_id = int(filter_select_result[0][2])
					dev_select = self.conn.execute('SELECT batch, split, device, pixel FROM dev_ids WHERE id = ?', (dev_id,))
					dev_select_result = dev_select.fetchall()
					result = dev_select_result[0][:] + filter_select_result[0][:]
					filtered_scans.append(result)
			
		if filtered_scans:			
			with open("%s" % file_name, "w") as text_file:
				text_file.write("Batch\tSplit\tDevice\tPixel\tScan ID\tTime Stamp\tDevice ID\tScan Type\tPCE\tVoc\tIsc\tJsc\tFF\tMPD\tVmax\tImax\tJmax\tPmax\tRs\tRsh\tCell Area\tIrradiance\tPre Sweep Delay\tNumber of Sweep Points\tDwell Time\tMaximum Bias\tMinimum Bias\tScan Rate\tScan Length\tLight Source\tDark or Light Scan\tSun Equivalents\tDatafile\tSoak Time\tSoak Suns\tLux\tTemperature\tFile Type\tMasked Area\tMasked by Full Area\n")
				#i is a tuple
				for tup in filtered_scans:					
					for x in tup:
						text_file.write("{0}\t".format(x))
					text_file.write("\n")	
				text_file.close()		
				
	def tab_jvresults_plot_ab_function(self, *args):
		markers = itertools.cycle(("o","v","^","<",">","s","p","*","h","H","+","x","8","D","d","|","_"))
		linestyles = itertools.cycle(('-', '--', '-.', ':'))
		cols = ('blue',
				'green',
			    'red',
			    'black',
			    'orange',
			    'magenta',
			    'cyan',
			    'yellow',
			   'firebrick',
			   'slategray',
			   'navy',
			   'plum',
			   'rosybrown',
					    )
		colours = itertools.cycle(cols)
		#Get the scan ids to plot
		plot_dict, split_names = self.tab_jvresults_plot_get_scan_ids()
		new_plot_dict = collections.OrderedDict(sorted(plot_dict.items()))
		##### for each key in plot dict change the scan id to the parameter to be plotted instead
		new_plot_list = []
		
		new_key_list = []	
		#now get the parameters to plot against each other
		y_para = str(self.tab_jvresults_comp_ypara_box.get())
		
		x_para = str(self.tab_jvresults_comp_xpara_box.get())
		
		#exclude values not in the range
		self.tab_jvresults_comp_ex_ymore_spinbox_var
		
		
		parameter = self.tab_jvresults_comp_xpara_box.get()
		parameter_min = float(self.tab_jvresults_comp_ex_xless_spinbox.get())
		parameter_max = float(self.tab_jvresults_comp_ex_xmore_spinbox.get())
			
		for key in new_plot_dict:			
			x_para_list = []
			y_para_list = []
			#filter the scans by x value
			filtered_scans = []
			for scan in plot_dict['%s' % key]:
				### if the scan id is light it will be returned add to the list of scan_ids
				level_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND '+parameter+' BETWEEN ? AND ?', (scan, parameter_min, parameter_max))
				level_filter_select_result = level_filter_select.fetchall()
				
				if not level_filter_select_result:
					pass
				else:	
					filtered_scans.append(level_filter_select_result[0])
					
			scan_ids = filtered_scans
			scan_ids = [i[0] for i in scan_ids]
			
			for i in scan_ids:
				para_select = self.conn.execute('SELECT '+x_para+','+y_para+' FROM jv_scan_results WHERE id = ?', (i,))
				para_select_result = para_select.fetchall()
				
				x_para_list.append(para_select_result[0][0])
				y_para_list.append(para_select_result[0][1])
			
			para_array = numpy.array((x_para_list, y_para_list), dtype=float)	
			new_plot_list.append(para_array)
		
			###### get the batch and split from the key and match this to a split name
			batch_num = key.split('batch')
			
			batch_num = batch_num[1].split('_')
			
			split_num = batch_num[3]
			batch_num = batch_num[1]
		
			split_name = split_names['batch_%s_split_%s' % (batch_num, split_num)]
			
			if 'grey' in key:
				if 'both' in key:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Both Light and Dark, Forward and Reverse Scans\n%s' % (new_point, split_name)
				elif 'forward' in key:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Both Light and Dark, Only Forward Scans\n%s' % (new_point, split_name)	
				else:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Both Light and Dark, Only Reverse Scans\n%s' % (new_point, split_name)
			elif 'light' in key:
				if 'both' in key:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Light, Forward and Reverse Scans\n%s' % (new_point, split_name)
				elif 'forward' in key:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Light, Forward Scans\n%s' % (new_point, split_name)	
				else:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Light, Reverse Scans\n%s' % (new_point, split_name)
			else:
				if 'both' in key:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Dark, Forward and Reverse Scans\n%s' % (new_point, split_name)
				elif 'forward' in key:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Dark, Forward Scans\n%s' % (new_point, split_name)
				else:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Dark, Reverse Scans\n%s' % (new_point, split_name)
							
			new_key_list.append(new_key)
		
		#Clear the old plots and make sure it is in the correct form...
		try:
			self.fig.clf()
		except:
			print 'Failed to delete figure'
		self.ax = self.fig.add_subplot(self.gs[0])
		
		xaxis_labels = {'masked_by_full_area':'Masked / Full Cell Active Area','temperature':'Temperature (Kelvin / K)','lux':'Luminous Flux (lx)', 'time_stamp': 'Scan Time','sun_equiv': 'Sun Equivalents (Suns)', 'scan_rate': 'Scan Rate (Volts per Second / Vs$^{-1}$)', 'cell_area': 'Cell Area/ (Centimeters Squared / cm$^{2}$)', 'irradiance': 'Irradiance (Watts per Meter Squared / (Wm-2)','soak_suns': 'Soak Sun Level (Sun Equivalents / Suns)','soak_time': 'Soak Time (Seconds / s)','pce': 'Power Conversion Efficiency (Percentage / %)', 'voc': 'Open Circuit Voltage (Volts / V)', 'isc': 'Short Circuit Current (Current / A)', 'jsc': 'Short Circuit Current Density (Current Density / mAcm$^{-2}$)', 'ff': 'Fill Factor / (%)', 'mpd': 'Maximum Power Density (Power Density / mWcm$^{-2}$)', 'vmax': 'Vmax (Volts / V)', 'imax': 'Imax (Current / A)', 'jmax': 'Jmax (Current Density / mAcm$^{-2}$)', 'pmax': 'Max Power Point (Power / W)', 'rs': 'Series Resistance (Ohms.cm$^2$)', 'rsh': 'Shunt Resistance (Ohms.cm$^2$)'}
		yaxis_labels = {'temperature':'Temperature (Kelvin / K)','lux':'Luminous Flux (lx)', 'sun_equiv': 'Sun Equivalents (Suns)', 'scan_rate': 'Scan Rate (Volts per Second / Vs$^{-1}$)', 'cell_area': 'Cell Area/ (Centimeters Squared / cm$^{2}$)', 'irradiance': 'Irradiance (Watts per Meter Squared / (Wm$^{-2}$)','soak_suns': 'Soak Sun Level (Sun Equivalents / Suns)','soak_time': 'Soak Time (Seconds / s)','pce': 'Power Conversion Efficiency (Percentage / %)', 'voc': 'Open Circuit Voltage (Volts / V)', 'isc': 'Short Circuit Current (Current / A)', 'jsc': 'Short Circuit Current Density (Current Density / mAcm$^{-2}$)', 'ff': 'Fill Factor / (%)', 'mpd': 'Maximum Power Density (Power Density / mWcm$^{-2}$)', 'vmax': 'Vmax (Volts / V)', 'imax': 'Imax (Current / A)', 'jmax': 'Jmax (Current Density / mAcm$^{-2}$)', 'pmax': 'Max Power Point (Power / W)', 'rs': 'Series Resistance (Ohms.cm$^2$)', 'rsh': 'Shunt Resistance (Ohms.cm$^2$)'}
		#Normalised labels
		#xaxis_labels = {'masked_by_full_area':'Normalised Masked / Full Cell Active Area','temperature':'Normalised Temperature (Kelvin / K)','lux':'Normalised Luminous Flux (lx)', 'time_stamp': 'Normalised Scan Time','sun_equiv': 'Normalised Sun Equivalents (Suns)', 'scan_rate': 'Normalised Scan Rate (Volts per Second / Vs$^{-1}$)', 'cell_area': 'Normalised Cell Area/ (Centimeters Squared / cm$^{2}$)', 'irradiance': 'Normalised Irradiance (Watts per Meter Squared / (Wm-2)','soak_suns': 'Normalised Soak Sun Level (Sun Equivalents / Suns)','soak_time': 'Normalised Soak Time (Seconds / s)','pce': 'Normalised Power Conversion Efficiency (Percentage / %)', 'voc': 'Normalised Open Circuit Voltage (Volts / V)', 'isc': 'Normalised Short Circuit Current (Current / A)', 'jsc': 'Normalised Short Circuit Current Density (Current Density / mAcm$^{-2}$)', 'ff': 'Normalised Fill Factor / (%)', 'mpd': 'Normalised Maximum Power Density (Power Density / mWcm$^{-2}$)', 'vmax': 'Normalised Vmax (Volts / V)', 'imax': 'Normalised Imax (Current / A)', 'jmax': 'Normalised Jmax (Current Density / mAcm$^{-2}$)', 'pmax': 'Normalised Max Power Point (Power / W)', 'rs': 'Normalised Series Resistance (Ohms.cm$^2$)', 'rsh': 'Normalised Shunt Resistance (Ohms.cm$^2$)'}
		#yaxis_labels = {'temperature':'Normalised Temperature (Kelvin / K)','lux':'Normalised Luminous Flux (lx)', 'sun_equiv': 'Normalised Sun Equivalents (Suns)', 'scan_rate': 'Normalised Scan Rate (Volts per Second / Vs$^{-1}$)', 'cell_area': 'Normalised Cell Area/ (Centimeters Squared / cm$^{2}$)', 'irradiance': 'Normalised Irradiance (Watts per Meter Squared / (Wm$^{-2}$)','soak_suns': 'Normalised Soak Sun Level (Sun Equivalents / Suns)','soak_time': 'Normalised Soak Time (Seconds / s)','pce': 'Normalised Power Conversion Efficiency (Percentage / %)', 'voc': 'Normalised Open Circuit Voltage (Volts / V)', 'isc': 'Normalised Short Circuit Current (Current / A)', 'jsc': 'Normalised Short Circuit Current Density (Current Density / mAcm$^{-2}$)', 'ff': 'Normalised Fill Factor / (%)', 'mpd': 'Normalised Maximum Power Density (Power Density / mWcm$^{-2}$)', 'vmax': 'Normalised Vmax (Volts / V)', 'imax': 'Normalised Imax (Current / A)', 'jmax': 'Normalised Jmax (Current Density / mAcm$^{-2}$)', 'pmax': 'Normalised Max Power Point (Power / W)', 'rs': 'Normalised Series Resistance (Ohms.cm$^2$)', 'rsh': 'Normalised Shunt Resistance (Ohms.cm$^2$)'}
		the_time = time.strftime("%H:%M:%S:%MS", time.localtime())
		
		xaxis_label = xaxis_labels['%s' % x_para]
		yaxis_label = yaxis_labels['%s' % y_para]
		###
		## set log or linear 
		if self.tab_jvresults_comp_logx_var.get() == 1:
			self.ax.set_xscale('log')
		if self.tab_jvresults_comp_logy_var.get() == 1:	
			self.ax.set_yscale('log')
			
		#colours = itertools.cycle(('red', 'green', 'blue', 'magenta', 'black', 'orange', 'cyan'))
		
		for split, label in itertools.izip(new_plot_list, new_key_list):
			marker = markers.next()
			colour = colours.next()
			linestyle = linestyles.next()
			#Normalised plots
			#replace and nan values with 0
			split[0] = numpy.nan_to_num(split[0])
			time_split = split[0]
			split[1] = numpy.nan_to_num(split[1])
			#normalise each axis data set and set the data range
			if x_para == 'time_stamp':
				#each time stamp should be in unix time
				#find the minimum time and use this as the start time
				start_time = numpy.amin(time_split)
				norm_time = []
				for i in time_split:
					i = i - start_time
					norm_time.append(i)
				split[0] = norm_time	
			
			if self.tab_jvresults_comp_normx_var.get() == 1:
				xmax = numpy.nanmax(split[0])
				split[0] = numpy.divide(split[0], xmax)
				self.ax.set_xlim([0,1.1])
				xaxis_label = "Normalised %s" % (xaxis_label)
			if self.tab_jvresults_comp_normy_var.get() == 1:
				ymax = numpy.nanmax(split[1])
				split[1] = numpy.divide(split[1], ymax)	
				self.ax.set_ylim([0,1.1])
				yaxis_label = "Normalised %s" % (yaxis_label)
			#if its a time plot then bin the values and average
			if x_para == 'time_stamp':
				
				#bin the data
				#find the axis unit
				ax_unit = self.tab_jvresults_comp_xscale_box_var.get()
				
				if self.tab_jvresults_comp_normx_var.get() == 1:
					xaxis_label = "Normalised Time"
				else:
					xaxis_label = "Time (%s)" % ax_unit
				if ax_unit == "seconds":
					pass
				elif ax_unit == "minutes":
					split[0] = numpy.divide(split[0], 60)
				elif ax_unit == "hours":
					split[0] = numpy.divide(split[0], (60*60))
				elif ax_unit == "days":	
					split[0] = numpy.divide(split[0], (60*60*24))		
				#find the max time in the new time set
				end_time = numpy.amax(split[0])
				bin_size = float(self.tab_jvresults_comp_bin_spinbox_var.get())
				num_bins = int(round((end_time / bin_size)+1))
				bin_means, bin_edges, binnumbers = binned_statistic(split[0], split[1], bins=num_bins, range=None, statistic='mean')
				bin_width = (bin_edges[1] - bin_edges[0])
				bin_centers = bin_edges[1:] - bin_width/2
				
				#Get rid of any nan values from the centers without points 
				#So that the line can be plotted
				bin_centers = bin_centers[~numpy.isnan(bin_means)]
				bin_means = bin_means[~numpy.isnan(bin_means)]
				#Calculate the SD		
				bin_sds, bin_sd_edges, binsdnumbers = binned_statistic(split[0], split[1], bins=num_bins, range=None, statistic=self.bin_sd)
				bin_sds = bin_sds[~numpy.isnan(bin_sds)]
				if self.tab_jvresults_comp_sd_var.get() == True:
					self.ax.errorbar(bin_centers, bin_means, bin_sds, linestyle=linestyle, marker=marker, color=colour, label=label)
				else:
					self.ax.plot(bin_centers, bin_means, linestyle=linestyle, marker=marker, color=colour, label=label)
						
				if self.tab_jvresults_comp_sd_shade_var.get() == True:
					self.ax.fill_between(bin_centers, bin_means+bin_sds, bin_means-bin_sds, facecolor=colour, alpha=0.3)
				

			elif self.tab_jvresults_comp_hist_var.get() == True:
				
				end = numpy.amax(split[0])
				bin_size = float(self.tab_jvresults_comp_bin_hist_spinbox_var.get())
				num_bins = int(round((end / bin_size)+1))
				total_count = len(split[0])
				
				if self.tab_jvresults_comp_normy_var.get() == 1:
					yaxis_label = "Normalised Counts"
					self.ax.hist(split[0], bins=num_bins, label=label, normed=1)
						
				else:	
					yaxis_label = "Counts"
					result = self.ax.hist(split[0], bins=num_bins, label="%s. Total count = %s" % (label, total_count))
					self.ax.set_xlim((min(split[0]), max(split[0])))
					mean = numpy.mean(split[0])
					variance = numpy.var(split[0])
					sigma = numpy.sqrt(variance)
					x = numpy.linspace(min(split[0]), max(split[0]),100)
					dx = result[1][1] - result[1][0]
					scale = len(split[0])*dx
					self.ax.plot(x, mlab.normpdf(x,mean,sigma)*scale, label="%s Gaussian fit: Mean = %.4g, Var = %.4g, SD = %.4g" % (label, mean, variance, sigma))
			else:	
				self.ax.plot(split[0], split[1], linestyle='none', marker=marker, color=colour, label=label)
				
		self.ax.set_xlabel('%s' % xaxis_label, fontsize=8)
		self.ax.set_ylabel('%s' % yaxis_label, fontsize=8)
		
		### Sort the lables alphabetically
		handles, labels = self.ax.get_legend_handles_labels()
		hl = sorted(zip(handles, labels), key=operator.itemgetter(1))
		handles2, labels2 = zip(*hl)		
		self.ax.set_position([self.box.x0, self.box.y0, self.box.width * 0.8, self.box.height])
		self.ax.legend(handles2, labels2)
		self.ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=6)
		self.canvas.draw()
		self.toolbar.update()
		
	def bin_sd(self, x):
		x = numpy.std(x)
		return x
							
	def tab_jvresults_plot_jv_plot_function(self, *args):
		if self.tab_jvresults_jv_av_check_var.get() == True:
			self.tab_jvresults_plot_av_jvs_function()
		else:
			## Get the scans selected
			selection = self.tab_jvresults_scan_listbox.curselection()
			scan_ids = []
			for i in selection:
				scan_id = self.tab_jvresults_scan_listbox.get(i)
				scan_ids.append(scan_id)
			### Each scan needs to have the data extracted from the datafile
			### then plotted
			### And given a name IDxx BxxSxxDxxPxx-Light-xSun-xV/s
			self.jv_ax.clear()
			
			markers = itertools.cycle((".",",","o","v","^","<",">","1","2","3","4","8","s","p","*","h","H","+","x","D","d","|","_"))
			if self.tab_jvresults_shunt_var.get() == True:
					##### Filter scan ids by shunt or not ######
					filtered_scans = []
					for i in scan_ids:
						scan_id = i
						shunt = 'Shunt'
						### get the shunt scans then remove them from the list
						shunt_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_status = ?', (scan_id, shunt,))
						shunt_filter_select_result = shunt_filter_select.fetchall()

						if not shunt_filter_select_result:
							pass
						else:	
							filtered_scans.append(shunt_filter_select_result[0])
					filtered_scans = [i[0] for i in filtered_scans]
					#### this is a list of 		
					scan_ids = [int(x) for x in scan_ids if x not in filtered_scans]
					
			if self.tab_jvresults_short_var.get() == True:
					##### Filter scan ids by shunt or not ######
					filtered_scans = []
					for i in scan_ids:
						scan_id = i
						s = 'Short'
						### get the shunt scans then remove them from the list
						short_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_status = ?', (scan_id, s,))
						short_filter_select_result = short_filter_select.fetchall()

						if not short_filter_select_result:
							pass
						else:	
							filtered_scans.append(short_filter_select_result[0])
					filtered_scans = [i[0] for i in filtered_scans]
					#### this is a list of 		
					scan_ids = [int(x) for x in scan_ids if x not in filtered_scans]
			
			if self.tab_jvresults_under_var.get() == True:
					##### Filter scan ids by shunt or not ######
					filtered_scans = []
					for i in scan_ids:
						scan_id = i
						s = 'Area under'
						### get the shunt scans then remove them from the list
						s_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_status = ?', (scan_id, s,))
						s_filter_select_result = s_filter_select.fetchall()

						if not s_filter_select_result:
							pass
						else:	
							filtered_scans.append(s_filter_select_result[0])
					filtered_scans = [i[0] for i in filtered_scans]
					#### this is a list of 		
					scan_ids = [int(x) for x in scan_ids if x not in filtered_scans]
			
			if self.tab_jvresults_over_var.get() == True:
					##### Filter scan ids by shunt or not ######
					filtered_scans = []
					for i in scan_ids:
						scan_id = i
						s = 'Area over'
						### get the shunt scans then remove them from the list
						s_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_status = ?', (scan_id, s,))
						s_filter_select_result = s_filter_select.fetchall()

						if not s_filter_select_result:
							pass
						else:	
							filtered_scans.append(s_filter_select_result[0])
					filtered_scans = [i[0] for i in filtered_scans]
					#### this is a list of 		
					scan_ids = [int(x) for x in scan_ids if x not in filtered_scans]
			
			if self.tab_jvresults_cross_var.get() == True:
					##### Filter scan ids by shunt or not ######
					filtered_scans = []
					for i in scan_ids:
						scan_id = i
						s = 'Crosstalk'
						### get the shunt scans then remove them from the list
						s_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_status = ?', (scan_id, s,))
						s_filter_select_result = s_filter_select.fetchall()

						if not s_filter_select_result:
							pass
						else:	
							filtered_scans.append(s_filter_select_result[0])
					filtered_scans = [i[0] for i in filtered_scans]
					#### this is a list of 		
					scan_ids = [int(x) for x in scan_ids if x not in filtered_scans]
			
			if self.tab_jvresults_fail_var.get() == True:
					##### Filter scan ids by shunt or not ######
					filtered_scans = []
					for i in scan_ids:
						scan_id = i
						s = 'Measurement Failure'
						### get the shunt scans then remove them from the list
						s_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_status = ?', (scan_id, s,))
						s_filter_select_result = s_filter_select.fetchall()

						if not s_filter_select_result:
							pass
						else:	
							filtered_scans.append(s_filter_select_result[0])
					filtered_scans = [i[0] for i in filtered_scans]
					#### this is a list of 		
					scan_ids = [int(x) for x in scan_ids if x not in filtered_scans]
			
			if self.tab_jvresults_ok_var.get() == True:
					##### Filter scan ids by shunt or not ######
					filtered_scans = []
					for i in scan_ids:
						scan_id = i
						s = 'ok'
						### get the shunt scans then remove them from the list
						s_filter_select = self.conn.execute('SELECT id FROM jv_scan_results WHERE id = ? AND scan_status = ?', (scan_id, s,))
						s_filter_select_result = s_filter_select.fetchall()

						if not s_filter_select_result:
							pass
						else:	
							filtered_scans.append(s_filter_select_result[0])
					filtered_scans = [i[0] for i in filtered_scans]
					#### this is a list of 		
					scan_ids = [int(x) for x in scan_ids if x not in filtered_scans]
			
			######
			####Colourmap for the line colour based on light intensity...
			#Get the range of light levels? Or just choose an arbitary max? So 1 sun is near middle?
			#Then get the sun level and find the index closest to that value and use
			#sun_lst = []
			#for i in scan_ids:
				#suns_select = self.conn.execute('SELECT sun_equiv FROM jv_scan_results WHERE id = ?', (i,))
				#suns_select_result = suns_select.fetchone()[0]
				#sun_lst.append(suns_select_result)
			
			#sun_ar = numpy.asarray(sun_lst)
			
			#minima = numpy.amin(sun_ar)
			#maxima = numpy.amax(sun_ar)

			norm = matplotlib.colors.Normalize(vmin=0, vmax=2, clip=True)
			mapper = cm.ScalarMappable(norm=norm, cmap=cm.nipy_spectral)
			
							
			for index, i in enumerate(scan_ids):
				if self.tab_jvresults_jv_marker_check_var.get() == True:
					marker = markers.next()
				else:
					marker = None	
				data_file_select = self.conn.execute('SELECT datafile FROM jv_scan_results WHERE id = ?', (i,))
				data_file_select_result = data_file_select.fetchone()[0]
				### Append the base file path to the file name 
				## The data structure needs to be BXX/SXX/filename.txt
				
				if not data_file_select_result:
					pass
				else:
					####convert the saved path to a windows path if needed...
					if platform.system() == "Windows":
						data_file_select_result =str(data_file_select_result).replace(r"/","\\")
					data_file_select_result = self.base_file_path + str(data_file_select_result)
					#Get the datafile file_type
					file_type_select = self.conn.execute('SELECT file_type FROM jv_scan_results WHERE id = ?', (i,))
					file_type_select_result = file_type_select.fetchone()[0]
					### scan name 
					### Get the scan name parts from the dev_id and the 
					dev_id_select = self.conn.execute('SELECT dev_id FROM jv_scan_results WHERE id = ?', (i,))
					dev_id_select_result = dev_id_select.fetchone()[0]
					
					dev_name_select = self.conn.execute('SELECT batch, split, device, pixel FROM dev_ids WHERE id = ?', (dev_id_select_result,))
					dev_name_select_result = dev_name_select.fetchall()
					
						
					### Find if scan is forward or reverse ###
					direc_select = self.conn.execute('SELECT scan_type FROM jv_scan_results WHERE id = ?', (i,))
					direc_select_result = direc_select.fetchone()[0]
					#### Set the line style depending on if its F or R 
					if direc_select_result == 'forward':
						scan_direc = 'F'
						ls = '-'
					else:
						scan_direc = 'R'
						ls = ':'
					## Find the light level ####
					suns_select = self.conn.execute('SELECT sun_equiv FROM jv_scan_results WHERE id = ?', (i,))
					suns_select_result = suns_select.fetchone()[0]
					
					suns = round(float(suns_select_result), 2)
					
					### Find the scan rate #####
					rate_select = self.conn.execute('SELECT scan_rate FROM jv_scan_results WHERE id = ?', (i,))
					rate_select_result = rate_select.fetchone()[0]
					
					rate = round(float(rate_select_result), 3)
					
					### Find if the scan is light or dark ###
					dark_select = self.conn.execute('SELECT dark_light FROM jv_scan_results WHERE id = ?', (i,))
					dark_select_result = dark_select.fetchone()[0]
					
					### Set the colour of the line depending on if the scan is D or L, and by the Light level and rate
					### L = red, D = black
					### R,G,B values in a tuple
					
					if dark_select_result == 0:
						light_dark = 'D'
						## If its dark scan the light level is not important but rate is
						#c = [round(((math.log(rate)+7)/10),2), round(((math.log(rate)+7)/10),2), round(((math.log(rate)+7)/10),2)] #R,G,B
					else:
						light_dark = 'L'
						#if suns == 0.0:
							#suns = suns + 0.001
						#### hmmmm its tricky.... 
						#### The range of light levels is not known
						### The range of scan rates is not known
						### Something with a log could help, should give better range to values about 1
						### say range was -6 to 3 0.000001 to blinding 1000 suns should be a great enough range which is range of 10
						#c = [1, round(((math.log(rate)+7)/10),2), round(((math.log(suns)+7)/10),2)] #R,G,B
					
					#Colour for the line
					#If plot by status then find the status and select line colour depending on this
					if self.tab_jvresults_jv_stat_check_var.get() == True:
						stat_select = self.conn.execute('SELECT scan_status FROM jv_scan_results WHERE id = ?', (i,))
						stat_select_result = stat_select.fetchone()[0]
						
						if str(stat_select_result) == 'ok':
							c = 'green'
							scan_name = 'ok'
						elif str(stat_select_result) == 'Short':
							c = 'red'
							scan_name = 'Short'
						elif str(stat_select_result) == 'Shunt':
							c = 'blue'
							scan_name = 'Shunt'
						elif str(stat_select_result) == 'Crosstalk':
							c = 'orange'
							scan_name = 'Crosstalk'
						elif str(stat_select_result) == 'Area over':
							c = 'magenta'
							scan_name = 'Area over'
						elif str(stat_select_result) == 'Area under':
							c = 'cyan'
							scan_name = 'Area under'
						elif str(stat_select_result) == 'Measurement Failure':
							c = 'firebrick'
							scan_name = 'Measurement Failure'
							
						else:
							c = 'black'
							scan_name = 'Other'
							
			   	
					else:
						c = mapper.to_rgba(suns_select_result)
						scan_name = 'B%sS%sD%sP%s_%s_%s_%sSuns_%sV/s' % (dev_name_select_result[0][0], dev_name_select_result[0][1], dev_name_select_result[0][2], dev_name_select_result[0][3], light_dark, scan_direc, suns, rate)

					#Use the file_type to decide which columns of the datafile to plot	
					if file_type_select_result == 'Oriel':
						all_data = numpy.genfromtxt(data_file_select_result, skip_header=10, delimiter='\t', dtype=float, encoding='latin1')
						voltage_points = all_data[:,0]
						current_points = all_data[:,1]
					elif file_type_select_result == 'Swansea':
						all_data = numpy.genfromtxt(data_file_select_result, skip_header=10, delimiter='\t', dtype=float, encoding='latin1')
						voltage_points = all_data[:,0]
						current_points = all_data[:,2]
						#get to amps...
						current_points = numpy.divide(current_points, 1000)	
					elif file_type_select_result == 'TPV2':
						all_data = numpy.genfromtxt(data_file_select_result, skip_header=1, delimiter='\t', dtype=float, encoding='latin1')
						voltage_points = all_data[:,0]
						current_points = all_data[:,1]		
					#### Get the cell area form file or database
					area_select = self.conn.execute('SELECT cell_area FROM jv_scan_results WHERE id = ?', (i,))
					area_select_result = area_select.fetchone()[0]
					
					current_density_points = numpy.divide(numpy.multiply(current_points, 1000), float(area_select_result))
					 
					### for the semilog plot the current needs to be converted to log
					log_current = numpy.sqrt(numpy.square(current_points))
					log_current_density = numpy.sqrt(numpy.square(current_density_points))
					
					#Colours for markers
					r, g, b = numpy.random.uniform(0, 1, 3)
					if self.tab_jvresults_jv_light_box.get() == 'Light Only':
						if light_dark == 'D':
							pass
						else:	
							if self.tab_jvresults_jv_iv_box.get() == 'Current Density':
								if self.tab_jvresults_jv_log_box.get() == 'Linear':
									self.jv_ax.plot(voltage_points, current_density_points, label="%s" % (scan_name), color=c, linestyle=ls, marker=marker, mfc=(r, g, b, 1), markeredgecolor=(r, g, b, 1), picker=5)
								else:
									self.jv_ax.semilogy(voltage_points, log_current_density, label="%s" % (scan_name), color=c, linestyle=ls, marker=marker, mfc=(r, g, b, 1), markeredgecolor=(r, g, b, 1), picker=5)
							
							else:
								if self.tab_jvresults_jv_log_box.get() == 'Linear':
									self.jv_ax.plot(voltage_points, current_points, label="%s" % (scan_name), color=c, linestyle=ls, marker=marker,  mfc=(r, g, b, 1), markeredgecolor=(r, g, b, 1), picker=5)
								else:
									self.jv_ax.semilogy(voltage_points, log_current, label="%s" % (scan_name), color=c, linestyle=ls, marker=marker,  mfc=(r, g, b, 1), markeredgecolor=(r, g, b, 1), picker=5)
							
					elif self.tab_jvresults_jv_light_box.get() == 'Dark Only':
						if light_dark == 'L':
							pass
						else:	
							if self.tab_jvresults_jv_iv_box.get() == 'Current Density':
								if self.tab_jvresults_jv_log_box.get() == 'Linear':
									self.jv_ax.plot(voltage_points, current_density_points, label="%s" % (scan_name), color=c, linestyle=ls, marker=marker, mfc=(r, g, b, 1), markeredgecolor=(r, g, b, 1), picker=5)
								else:
									self.jv_ax.semilogy(voltage_points, log_current_density, label="%s" % (scan_name), color=c, linestyle=ls, marker=marker,  mfc=(r, g, b, 1), markeredgecolor=(r, g, b, 1), picker=5)
							else:
								if self.tab_jvresults_jv_log_box.get() == 'Linear':
									self.jv_ax.plot(voltage_points, current_points, label="%s" % (scan_name), color=c, linestyle=ls, marker=marker,  mfc=(r, g, b, 1), markeredgecolor=(r, g, b, 1), picker=5)
								else:
									self.jv_ax.semilogy(voltage_points, log_current, label="%s" % (scan_name), color=c, linestyle=ls, marker=marker,  mfc=(r, g, b, 1), markeredgecolor=(r, g, b, 1), picker=5)
					else:
						if self.tab_jvresults_jv_iv_box.get() == 'Current Density':
							if self.tab_jvresults_jv_log_box.get() == 'Linear':
								self.jv_ax.plot(voltage_points, current_density_points, label="%s" % (scan_name), color=c, linestyle=ls, marker=marker,  mfc=(r, g, b, 1), markeredgecolor=(r, g, b, 1), picker=5)
							else:
								self.jv_ax.semilogy(voltage_points, log_current_density, label="%s" % (scan_name), color=c, linestyle=ls, marker=marker,  mfc=(r, g, b, 1), markeredgecolor=(r, g, b, 1), picker=5)
							
						else:
							if self.tab_jvresults_jv_log_box.get() == 'Linear':
								self.jv_ax.plot(voltage_points, current_points, label="%s" % (scan_name), color=c, linestyle=ls, marker=marker, mfc=(r, g, b, 1), markeredgecolor=(r, g, b, 1), picker=5)
							else:
								self.jv_ax.semilogy(voltage_points, log_current, label="%s" % (scan_name), color=c, linestyle=ls, marker=marker,  mfc=(r, g, b, 1), markeredgecolor=(r, g, b, 1), picker=5)
							
			
			
		if self.tab_jvresults_jv_iv_box.get() == 'Current Density':
			self.jv_ax.set_title('J vs. V')
			self.jv_ax.set_ylabel('Current Density / mA/cm2')
		else:
			self.jv_ax.set_title('I vs. V')
			self.jv_ax.set_ylabel('Current / A')
				
		self.jv_ax.set_xlabel('Voltage / V')
		self.jv_ax.axvline(ls='--', color='k')
		self.jv_ax.axhline(ls='--', color='k')
		### Sort the lables alphabetically
		handles, labels = self.jv_ax.get_legend_handles_labels()
		hl = sorted(zip(handles, labels), key=operator.itemgetter(1))
		handles2, labels2 = zip(*hl)

		self.jv_ax.set_position([self.jv_box.x0, self.jv_box.y0, self.jv_box.width * 0.8, self.jv_box.height])
		self.jv_ax.legend(handles2, labels2)
		self.jv_ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=6)
		self.jv_canvas.draw()
		self.jv_toolbar.update()
	
	def find_nearest_idx(self, array, value):
		array = numpy.asarray(array)
		idx = (numpy.abs(array - value)).argmin()
		return idx
	
	def tab_jvresults_plot_av_jvs_function(self, *args):
		self.jv_ax.clear()
		markers = itertools.cycle(("o","v","^","<",">","s","p","*","h","H","+","x","8","D","d","|","_"))
		linestyles = itertools.cycle(('-', '--'))
		cols = ('blue',
				'green',
			    'red',
			    'black',
			    'orange',
			    'magenta',
			    'cyan',
			    'yellow',
			   'firebrick',
			   'slategray',
			   'navy',
			   'plum',
			   'rosybrown',
					    )
		colours = itertools.cycle(cols)
		
		plot_dict, split_names = self.tab_jvresults_plot_get_scan_ids()
		new_plot_dict = collections.OrderedDict(sorted(plot_dict.items()))
		##### for each key in plot dict change the scan id to the parameter to be plotted instead
		new_plot_list = []
		new_key_list = []
		for key in new_plot_dict:
			
			parameter = 'datafile'
			para_list = []
			for i in plot_dict['%s' % key]:
				para_select = self.conn.execute('SELECT '+parameter+' FROM jv_scan_results WHERE id = ?', (i,))
				data_file_select_result = para_select.fetchone()[0]
				if platform.system() == "Windows":
					data_file_select_result =str(data_file_select_result).replace(r"/","\\")
				data_file_select_result = self.base_file_path + str(data_file_select_result)
				#Get the datafile file_type
				file_type_select = self.conn.execute('SELECT file_type FROM jv_scan_results WHERE id = ?', (i,))
				file_type_select_result = file_type_select.fetchone()[0]
				
				area_select = self.conn.execute('SELECT cell_area FROM jv_scan_results WHERE id = ?', (i,))
				area_select_result = area_select.fetchone()[0]
					
				para_list.append([data_file_select_result,file_type_select_result,area_select_result])
			
				
			new_plot_list.append(para_list)
			
			###### get the batch and split from the key and match this to a split name
			batch_num = key.split('batch')
			
			batch_num = batch_num[1].split('_')
			
			split_num = batch_num[3]
			batch_num = batch_num[1]
		
			split_name = split_names['batch_%s_split_%s' % (batch_num, split_num)]
			
			if 'grey' in key:
				if 'both' in key:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Both Light and Dark, Forward and Reverse Scans\n%s' % (new_point, split_name)
				elif 'forward' in key:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Both Light and Dark, Only Forward Scans\n%s' % (new_point, split_name)	
				else:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Both Light and Dark, Only Reverse Scans\n%s' % (new_point, split_name)
			elif 'light' in key:
				if 'both' in key:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Light, Forward and Reverse Scans\n%s' % (new_point, split_name)
				elif 'forward' in key:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Light, Forward Scans\n%s' % (new_point, split_name)	
				else:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Light, Reverse Scans\n%s' % (new_point, split_name)
			else:
				if 'both' in key:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Dark, Forward and Reverse Scans\n%s' % (new_point, split_name)
				elif 'forward' in key:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Dark, Forward Scans\n%s' % (new_point, split_name)
				else:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Dark, Reverse Scans\n%s' % (new_point, split_name)
							
			new_key_list.append(new_key)
		
		
					
		for split, label in itertools.izip(new_plot_list, new_key_list):

			split_num_list = []
			vs = []
			cs = []
			cds = []
			lcs = []
			lcds = []
			scan_name = label

			for i in split:
				data_file_select_result = i[0]
				file_type_select_result = i[1]
				area_select_result = i[2]

				#i is a list of the datafile, file type	and cell area
					
				#Use the file_type to decide which columns of the datafile to plot	
				if file_type_select_result == 'Oriel':
					all_data = numpy.genfromtxt(data_file_select_result, skip_header=10, delimiter='\t', dtype=float, encoding='latin1')
					voltage_points = all_data[:,0]
					current_points = all_data[:,1]
				elif file_type_select_result == 'Swansea':
					all_data = numpy.genfromtxt(data_file_select_result, skip_header=10, delimiter='\t', dtype=float, encoding='latin1')
					voltage_points = all_data[:,0]
					current_points = all_data[:,2]
					#get to amps...
					current_points = numpy.divide(current_points, 1000)	
				elif file_type_select_result == 'TPV2':
					all_data = numpy.genfromtxt(data_file_select_result, skip_header=1, delimiter='\t', dtype=float, encoding='latin1')
					voltage_points = all_data[:,0]
					current_points = all_data[:,1]
			
				current_density_points = numpy.divide(numpy.multiply(current_points, 1000), float(area_select_result))
					 
				### for the semilog plot the current needs to be converted to log
				log_current = numpy.sqrt(numpy.square(current_points))
				log_current_density = numpy.sqrt(numpy.square(current_density_points))
				
				vs.append(voltage_points)
				
				cs.append(current_points)
				cds.append(current_density_points)
				lcs.append(log_current)
				lcds.append(log_current_density)
			
				
			
			av_vs = numpy.mean(numpy.array(vs),axis=0)
			av_cs = numpy.mean(numpy.array(cs),axis=0)
			av_cds = numpy.mean(numpy.array(cds),axis=0)
			av_lcs = numpy.mean(numpy.array(lcs),axis=0)
			av_lcds = numpy.mean(numpy.array(lcds),axis=0)
			
			std_vs = numpy.std(numpy.array(vs),axis=0)
			std_cs = numpy.std(numpy.array(cs),axis=0)
			std_cds = numpy.std(numpy.array(cds),axis=0)
			std_lcs = numpy.std(numpy.array(lcs),axis=0)
			std_lcds = numpy.std(numpy.array(lcds),axis=0)
			
			r, g, b = numpy.random.uniform(0, 1, 3)
			
			c = colours.next()
			ls = linestyles.next()
			if self.tab_jvresults_jv_marker_check_var.get() == True:
					marker = markers.next()
			else:
				marker = None
			
			if self.tab_jvresults_jv_iv_box.get() == 'Current Density':
				if self.tab_jvresults_jv_log_box.get() == 'Linear':
					self.jv_ax.plot(av_vs, av_cds, label="%s" % (scan_name), color=c, linestyle=ls, marker=marker, mfc=(r, g, b, 1), markeredgecolor=(r, g, b, 1))
					self.jv_ax.fill_between(av_vs, av_cds+std_cds, av_cds-std_cds, facecolor=c, alpha=0.3)
				else:
					self.jv_ax.semilogy(av_vs, av_lcds, label="%s" % (scan_name), color=c, linestyle=ls, marker=marker, mfc=(r, g, b, 1), markeredgecolor=(r, g, b, 1))
					self.jv_ax.fill_between(av_vs, av_lcds+std_lcds, av_lcds-std_lcds, facecolor=c, alpha=0.3)
			else:
				if self.tab_jvresults_jv_log_box.get() == 'Linear':
					self.jv_ax.plot(av_vs, av_cs, label="%s" % (scan_name), color=c, linestyle=ls, marker=marker, mfc=(r, g, b, 1), markeredgecolor=(r, g, b, 1))
					self.jv_ax.fill_between(av_vs, av_cs+std_cs, av_cs-std_cs, facecolor=c, alpha=0.3)
				else:
					self.jv_ax.plot(av_vs, av_cs, label="%s" % (scan_name), color=c, linestyle=ls, marker=marker, mfc=(r, g, b, 1), markeredgecolor=(r, g, b, 1))
					self.jv_ax.fill_between(av_vs, av_lcs+std_lcs, av_lcs-std_lcs, facecolor=c, alpha=0.3)
			
			
	def tab_jvresults_plot_box_plot_function(self, *args):
		plot_dict, split_names = self.tab_jvresults_plot_get_scan_ids()
		new_plot_dict = collections.OrderedDict(sorted(plot_dict.items()))
		##### for each key in plot dict change the scan id to the parameter to be plotted instead
		new_plot_list = []
		new_key_list = []
		for key in new_plot_dict:
			parameter = str(self.tab_jvresults_comp_ypara_box.get())
			para_list = []
			for i in plot_dict['%s' % key]:
				para_select = self.conn.execute('SELECT '+parameter+' FROM jv_scan_results WHERE id = ?', (i,))
				para_select_result = para_select.fetchone()[0]
				
				para_list.append(para_select_result)
			
			para_array = numpy.array(para_list)	
			new_plot_list.append(para_array)
			###### get the batch and split from the key and match this to a split name
			batch_num = key.split('batch')
			
			batch_num = batch_num[1].split('_')
			
			split_num = batch_num[3]
			batch_num = batch_num[1]
		
			split_name = split_names['batch_%s_split_%s' % (batch_num, split_num)]
			
			if 'grey' in key:
				if 'both' in key:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Both Light and Dark, Forward and Reverse Scans\n%s' % (new_point, split_name)
				elif 'forward' in key:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Both Light and Dark, Only Forward Scans\n%s' % (new_point, split_name)	
				else:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Both Light and Dark, Only Reverse Scans\n%s' % (new_point, split_name)
			elif 'light' in key:
				if 'both' in key:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Light, Forward and Reverse Scans\n%s' % (new_point, split_name)
				elif 'forward' in key:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Light, Forward Scans\n%s' % (new_point, split_name)	
				else:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Light, Reverse Scans\n%s' % (new_point, split_name)
			else:
				if 'both' in key:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Dark, Forward and Reverse Scans\n%s' % (new_point, split_name)
				elif 'forward' in key:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Dark, Forward Scans\n%s' % (new_point, split_name)
				else:
					point = key.split('batch')
					new_point = 'Batch%s' % point[1]
					new_key = '%s: Dark, Reverse Scans\n%s' % (new_point, split_name)
							
			new_key_list.append(new_key)
		
		#Clear old plots and make sure new is correct form
		try:
			self.fig.clf()
		except:
			print 'Failed to delete figure'
		
		self.ax = self.fig.add_subplot(self.gs[0])
		
		para = str(self.tab_jvresults_comp_ypara_box.get())
		axis_labels = {'pce': 'Power Conversion Efficiency (Percentage / %)', 'voc': 'Open Circuit Voltage (Volts / V)', 'isc': 'Short Circuit Current (Current / A)', 'jsc': 'Short Circuit Current Density (Current Density / mAcm$^{-2}$)', 'ff': 'Fill Factor / (%)', 'mpd': 'Maximum Power Density (Power Density / mWcm$^{-2}$)', 'vmax': 'Vmax (Volts / V)', 'imax': 'Imax (Current / A)', 'jmax': 'Jmax (Current Density / mAcm$^{-2}$)', 'pmax': 'Max Power Point (Power / W)', 'rs': 'Series Resistance (Ohms.cm$^2$)', 'rsh': 'Shunt Resistance (Ohms.cm$^2$)'}
		the_time = time.strftime("%H:%M:%S:%MS", time.localtime())
		
		bp = self.ax.boxplot(new_plot_list, 0, 'yD', showmeans=True)
		axis_label = axis_labels['%s' % para]
		
		## set log or linear 
		if self.tab_jvresults_comp_logx_var.get() == 1:
			self.ax.set_xscale('log')
		if self.tab_jvresults_comp_logy_var.get() == 1:
			self.ax.set_yscale('log')	
		
		#For use in plotting the splits
		split_num = 1
		#each split is in the data to plot
		#this is a mess as its taking each point and finding which split number it falls into.
		#There is a better faster way, but I can't be bothered
		#find the upper and lower values so as not to plot fliers
		limits = [item.get_ydata()[1] for item in bp['whiskers']]
		lower_lims = limits[::2]
		upper_lims = limits[1::2]
		
		for split in new_plot_list:
			split_num_list = []
			ys = []
			for i in split:	
				#If its not a flier give it some jitter
				if i >= lower_lims[(split_num-1)] and i <= upper_lims[(split_num-1)]:
					split_num_skew = numpy.random.normal(split_num, 0.04)
				#If it is a flier keep it central so the on pick still works but the points still overlap
				else:
					split_num_skew = split_num
				split_num_list.append(split_num_skew)	
				ys.append(i)	
			self.ax.plot(split_num_list, ys, 'r.', alpha=0.6, picker=5)
			split_num = split_num+1  
			
		#Set the x labels for each split
		if self.tab_jvresults_rean_check_var.get() == 1:
			split_labs = []
			for i in new_key_list:

				label = tkSimpleDialog.askstring(title = "Enter New Split Name", prompt = "Enter split %s name for x-axis label" % i, initialvalue="%s:" % i) 
				if label:
					split_labs.append(label)
				else:
					split_labs.append(i)
			xsize = tkSimpleDialog.askinteger(title = "Enter Split Fontsize", prompt = "Enter split fontsize for x-axis label", initialvalue=8) 
			if not xsize:
				print 'not'
				xsize = 8	
			self.ax.set_xticklabels(split_labs, rotation=-45, ha='left', fontsize=xsize)
			xlab = tkSimpleDialog.askstring(title = "Enter X-axis Label", prompt = "Enter X-axis label", initialvalue="Splits") 
			if not xlab:
				xlab = 'Splits'
			xlabelsize = tkSimpleDialog.askinteger(title = "Enter X-Label Fontsize", prompt = "Enter X-label fontsize", initialvalue=6)
			if not xlabelsize:
				xlabelsize = 6
			self.ax.set_xlabel('%s' % xlab, fontsize=xlabelsize)
			ylabelsize = tkSimpleDialog.askinteger(title = "Enter Y-Label Fontsize", prompt = "Enter Y-label fontsize", initialvalue=8)
			if not ylabelsize:
				ylabelsize = 8
			ylab = tkSimpleDialog.askstring(title = "Enter Y-axis Label", prompt = "Enter Y-axis label", initialvalue="%s" % axis_label) 
			if ylab:
				axis_label = ylab	
			self.ax.set_ylabel('%s' % axis_label, fontsize=ylabelsize)
			title = tkSimpleDialog.askstring(title = "Enter Plot Title", prompt = "Enter Plot Title") 
			title_size = tkSimpleDialog.askinteger(title = "Enter Title Fontsize", prompt = "Enter title fontsize", initialvalue=14)
			if not title_size:
				title_size = 14
			self.ax.set_title('%s' % title, fontsize=title_size)
			
		else:	
			self.ax.set_xticklabels(new_key_list, rotation=-45, ha='left', fontsize=8)
			self.ax.set_xlabel('Splits', fontsize=6)
			self.ax.set_ylabel('%s' % axis_label, fontsize=8)
		
		for box in bp['boxes']:
		    # change outline color
		    box.set( color='#7570b3', linewidth=2)
		## change color and linewidth of the whiskers
		for whisker in bp['whiskers']:
			whisker.set(color='#7570b3', linewidth=2)
		## change color and linewidth of the caps
		for cap in bp['caps']:
			cap.set(color='#7570b3', linewidth=2)
		## change color and linewidth of the medians
		for median in bp['medians']:
		    median.set(color='#b2df8a', linewidth=2)
		## change the style of fliers and their fill
		for flier in bp['fliers']:
		    flier.set(marker='o', color='cyan', alpha=0.5)
		 
		self.fig.tight_layout()    
		self.canvas.draw()
		self.toolbar.update()
	
	def tab_jvresults_plot_pretty_box_plot_function(self,*args):
		#Clear the old file name incase
		#self.export_file_name = ''
		#Generate the file to plot from...
		#self.tab_jvresults_export_selection_function()
		#Select the scans parameters
		datafile = self.tab_jvresults_pretty_box_selection_function()
		#And get the file name to plot from self.export_file_name
		#datafile = self.export_file_name
		#print 'This is the datafile %s' % datafile
		#Get the data sorted into splits and split numbers etc..
		forward_splits_dict, reverse_splits_dict, splits = self.sort_data(datafile)
		
		#Use the splits to populate a popout and accept the split names?
		split_names = []
		for index, i in enumerate(splits):
			split_name = tkSimpleDialog.askstring(title = "Enter Split Name", prompt = "Enter split %s name for x-axis label" % i, initialvalue="S%s:" % i) 
			split_names.append(split_name)

		#loc = [2,2,1,4,4,1]

		self.plot_pretty_box_plot(split_names,forward_splits_dict,reverse_splits_dict,splits)
		
		#Remove the file created to save space, making the file slows the plot right down, should avoid this...
	def plot_pretty_box_plot(self,split_names,forward_splits_dict,reverse_splits_dict,splits):
		#Clear old plots and make sure new is correct form

		try:
			self.fig.clf()
		except:
			print 'Failed to delete figure'
		
		
		axis_labels = {'pce': 'Power Conversion Efficiency\n(Percentage / %)', 'voc': 'Open Circuit Voltage\n(Voltage / V)', 'isc': 'Short Circuit Current\n(Current / A)', 'jsc': 'Short Circuit Current Density\n(Current Density / mAcm$^{-2}$)', 'ff': 'Fill Factor\n(Percentage / %)', 'mpd': 'Maximum Power Density\n(Power Density / mWcm$^{-2}$)', 'vmax': 'Vmax\n(Volts / V)', 'imax': 'Imax\n(Current / A)', 'jmax': 'Jmax\n(Current Density / mAcm$^{-2}$)', 'pmax': 'Max Power Point\n(Power / W)', 'rs': 'Series Resistance\n(Ohms.cm$^2$)', 'rsh': 'Shunt Resistance\n(Ohms.cm$^2$)'}

		markers = itertools.cycle(('*', '^', 'o', '<', '8', 'p', 's', 'D'))

		colours = (
					'red',
					'blue',
					'black',
					'orange',
					'magenta',
					'cyan',
				   'firebrick',
				   'slategray',
				   'navy',
				   'plum',
				   'rosybrown',
				   'yellow',
									)
		#colours = (None,None)
		cols = itertools.cycle(colours)
		
		wid = 0.1

		reverse_colour = 'grey'
		forwards_colour = 'white'

		plot_titles = ['PCEs', 'Vocs', 'Rs', 'Jsc' , 'FF', 'Rsh']

		parameters = [axis_labels['pce'], axis_labels['voc'], axis_labels['rs'], axis_labels['jsc'], axis_labels['ff'], axis_labels['rsh']]


		reverse_colour = 'grey'
		forwards_colour = 'white'
		patch = mpatches.Rectangle([0.025, 0.05],0.05, 0.1,facecolor=reverse_colour, edgecolor='black', lw=1, label='Reverse Scans')
		patch2 = mpatches.Rectangle([0.025, 0.05],0.05, 0.1,facecolor=forwards_colour, edgecolor='black', lw=1, label='Forwards Scans')
		offsetx = 0.15
		
		################################################
		

		things_to_plot = [
		['PCEs',8],
		['Vocs',9],
		['Rs',18],
		['Jscs',11],
		['FFs',12],
		['Rsh',19],
		]
		for index, para in enumerate(things_to_plot):
			self.axarr = self.fig.add_subplot(self.gs2[index])	
			
			rev_data_to_plot, for_data_to_plot = self.plot_list(para[0],para[1],splits,reverse_splits_dict,forward_splits_dict,split_names)
			rev_pos, for_pos = self.split_pos(rev_data_to_plot)

			#print rev_data_to_plot
			bppce1 = self.axarr.boxplot(rev_data_to_plot, patch_artist=True, showmeans=True, widths=wid, positions=rev_pos)
			self.bp_cols(bppce1,reverse_colour)

			bppce2 = self.axarr.boxplot(for_data_to_plot, patch_artist=True, showmeans=True, widths=wid, positions=for_pos)
			self.bp_cols(bppce2,forwards_colour)

			cols = itertools.cycle(colours)
			for ind, i in enumerate(rev_data_to_plot):
				col = cols.next()
				pos = rev_pos[ind] -offsetx
				bppce3 = self.axarr.plot(numpy.random.normal(pos, 0.02, size=len(rev_data_to_plot[ind])), rev_data_to_plot[ind],marker=markers.next(),markersize=3,color=col,linestyle='None',alpha=0.6)
				self.axarr.axvline(ind+0.5, linestyle='--', color='k') # vertical lines
				self.axarr.axvspan(ind+0.5, ind+1, facecolor=col, alpha=0.2)

			cols = itertools.cycle(colours)
			for ind, i in enumerate(for_data_to_plot):
				col = cols.next()
				pos = for_pos[ind] +offsetx
				bppce4 = self.axarr.plot(numpy.random.normal(pos, 0.02, size=len(for_data_to_plot[ind])),for_data_to_plot[ind], marker=markers.next(),markersize=3,color=col,linestyle='None',alpha=0.8)
				self.axarr.axvspan(ind+1, ind+1.5, facecolor=col, alpha=0.2)
				
			#self.axarr.legend(fontsize=6,loc=loc[index],handles=[patch,patch2])
			self.axarr.get_xaxis().tick_bottom()
			self.axarr.set_xticklabels(split_names,  ha='left', fontsize=6, rotation=-45)
			self.axarr.get_yaxis().tick_left()
			#self.axarr.set_xlabel("Splits", fontsize=25)
			self.axarr.set_ylabel(parameters[index], fontsize=6)
			#self.axarr.set_title(parameters[0], fontsize=25)
			#self.axarr.tick_params(axis='y', labelsize=6, length=10, width=5)
			#self.axarr.tick_params(axis='x', length=6, width=5)
			startx, endx = self.axarr.get_xlim()
			self.axarr.set_xlim(right=endx-0.1)
			self.axarr.yaxis.grid(True, which='both')
			if index < 2 or index > 2 and index < 5:
				self.axarr.set_ylim(bottom=0)
			if index == 2 or index == 5:
				self.axarr.set_yscale('log')
		
			if index == 0:
				start, end = self.axarr.get_ylim()
				self.axarr.yaxis.set_ticks(numpy.arange(numpy.floor(start), numpy.ceil(end), 1.))
				self.axarr.yaxis.set_major_formatter(ticker.FormatStrFormatter('%1.f'))
		
		self.fig.tight_layout()    
		self.canvas.draw()
		self.toolbar.update()
		
	def on_key_event(self, event):
		key_press_handler(event, self.canvas, self.toolbar)
	def on_key_event_jv(self, event):
		key_press_handler(event, self.jv_canvas, self.jv_toolbar)
		
	def tab_jvresults_time_all_selction(self, *args):
		self.tab_jvresults_time_listbox.select_set(0,END)
		self.tab_jvresults_scan_listbox_update()
	def tab_jvresults_lux_all_selction(self, *args):
		self.tab_jvresults_lux_listbox.select_set(0,END)
		self.tab_jvresults_time_listbox_update()
	def tab_jvresults_rate_all_selction(self, *args):
		self.tab_jvresults_rate_listbox.select_set(0,END)
		self.tab_jvresults_soak_time_listbox_update()
	def tab_jvresults_soak_time_all_selction(self, *args):
		self.tab_jvresults_soak_time_listbox.select_set(0,END)
		self.tab_jvresults_soak_suns_listbox_update()
	def tab_jvresults_soak_suns_all_selction(self, *args):
		self.tab_jvresults_soak_suns_listbox.select_set(0,END)
		self.tab_jvresults_lux_listbox_update()		
	def tab_jvresults_suns_all_selction(self, *args):
		self.tab_jvresults_suns_listbox.select_set(0,END)
		self.tab_jvresults_rate_listbox_update()		
	def tab_jvresults_source_all_selction(self, *args):
		self.tab_jvresults_source_listbox.select_set(0,END)
		self.tab_jvresults_suns_listbox_update()
	def tab_jvresults_scan_all_selction(self, *args):
		self.tab_jvresults_scan_listbox.select_set(0,END)
	def tab_jvresults_area_all_selction(self, *args):
		self.tab_jvresults_area_listbox.select_set(0,END)
		self.tab_jvresults_light_source_listbox_update()
	def tab_jvresults_pixel_all_selction(self, *args):
		self.tab_jvresults_pixel_listbox.select_set(0,END)
		self.tab_jvresults_area_listbox_update()
	def tab_jvresults_device_all_selction(self, *args):
		self.tab_jvresults_device_listbox.select_set(0,END)
		self.tab_jvresults_populate_pixel_listbox()
	def tab_jvresults_split_all_selction(self, *args):
		self.tab_jvresults_split_listbox.select_set(0,END)
		self.tab_jvresults_populate_device_listbox()
	def tab_jvresults_bat_all_selction(self, *args):
		self.tab_jvresults_batch_listbox.select_set(0,END)
		self.tab_jvresults_populate_split_listbox()
	def tab_jvresults_scan_everything_selction(self,*args):
		self.tab_jvresults_split_all_selction()
		self.tab_jvresults_device_all_selction()
		self.tab_jvresults_pixel_all_selction()
		self.tab_jvresults_area_all_selction()
		self.tab_jvresults_source_all_selction()
		self.tab_jvresults_suns_all_selction()
		self.tab_jvresults_rate_all_selction()
		self.tab_jvresults_soak_time_all_selction()
		self.tab_jvresults_soak_suns_all_selction()
		self.tab_jvresults_lux_all_selction()
		self.tab_jvresults_time_all_selction()
		self.tab_jvresults_scan_all_selction()
	def tab_jvresults_scan_listbox_update(self, *args):
		self.tab_jvresults_scan_listbox.delete(0,END)
		self.time_ids = None
		self.time_ids = self.tab_jv_results_listbox_get_device_ids_time(self.lux_ids)
		#scan_ids = self.tab_jv_results_listbox_get_device_ids_soak_time(lux_ids)
		
		col = 'id'
		ids = self.tab_jv_results_listbox_sql(col, self.time_ids)
		for i in ids:
			self.tab_jvresults_scan_listbox.insert(END, i)	
	
	def tab_jvresults_time_listbox_update(self, *args):
		self.tab_jvresults_time_listbox.delete(0,END)
		self.tab_jvresults_scan_listbox.delete(0,END)
		self.lux_ids = None
		self.lux_ids = self.tab_jv_results_listbox_get_device_ids_lux(self.soak_sun_ids)
		
		col = 'time_stamp'
		ids = self.tab_jv_results_listbox_sql(col, self.lux_ids)

		for i in ids:
			
			#change the time stamp to a YYYYMMDDHHMMSS
			i = datetime.datetime.fromtimestamp(i).strftime('%Y/%m/%d %H:%M:%S')
			self.tab_jvresults_time_listbox.insert(END, i)
			
	def tab_jvresults_lux_listbox_update(self, *args):
		self.tab_jvresults_lux_listbox.delete(0,END)
		self.tab_jvresults_time_listbox.delete(0,END)
		self.tab_jvresults_scan_listbox.delete(0,END)
		self.soak_sun_ids = None
		self.soak_sun_ids = self.tab_jv_results_listbox_get_device_ids_soak_suns(self.soak_ids)
		col = 'lux'
		ids = self.tab_jv_results_listbox_sql(col, self.soak_sun_ids)
		for i in ids:
			self.tab_jvresults_lux_listbox.insert(END, i)
			
	def tab_jvresults_soak_suns_listbox_update(self, *args):
		self.tab_jvresults_soak_suns_listbox.delete(0,END)
		self.tab_jvresults_lux_listbox.delete(0,END)
		self.tab_jvresults_time_listbox.delete(0,END)
		self.tab_jvresults_scan_listbox.delete(0,END)
		
		self.soak_ids = self.tab_jv_results_listbox_get_device_ids_soak_time(self.rate_ids)

		col = 'soak_suns'
		ids = self.tab_jv_results_listbox_sql(col, self.soak_ids)
		for i in ids:
			self.tab_jvresults_soak_suns_listbox.insert(END, i)
		###### Find the cell areas for those devices #####
		#### for each id search the jv_scan_results for scans with a dev_id matching and get the cell area
	def tab_jv_results_listbox_sql(self, col, thing_ids):		
		col = col
		scans = thing_ids
		
		some_ids = []
		for scan_id in scans:
			scan_id = scan_id[0]
			exists = self.conn.execute('SELECT DISTINCT '+col+' FROM jv_scan_results WHERE id = ? ORDER BY '+col+' ASC', (scan_id,))
			exists_result = exists.fetchall()	
			
			if exists_result:
				for i in exists_result:
					some_ids.append(i[0])
					
						
		some_ids = list(set(some_ids))
		some_ids.sort()
		return some_ids
		
			
	def tab_jvresults_soak_time_listbox_update(self, *args):
		self.tab_jvresults_soak_time_listbox.delete(0,END)
		self.tab_jvresults_soak_suns_listbox.delete(0,END)
		self.tab_jvresults_lux_listbox.delete(0,END)
		self.tab_jvresults_time_listbox.delete(0,END)
		self.tab_jvresults_scan_listbox.delete(0,END)
		
		self.rate_ids = None
		self.rate_ids = self.tab_jv_results_listbox_get_device_ids_rate(self.sun_ids)
		
		col = 'soak_time'
		ids = self.tab_jv_results_listbox_sql(col, self.rate_ids)
		for i in ids:
			self.tab_jvresults_soak_time_listbox.insert(END, i)
					
	def tab_jvresults_rate_listbox_update(self, *args):
		self.tab_jvresults_rate_listbox.delete(0,END)
		self.tab_jvresults_soak_time_listbox.delete(0,END)
		self.tab_jvresults_soak_suns_listbox.delete(0,END)
		self.tab_jvresults_lux_listbox.delete(0,END)
		self.tab_jvresults_time_listbox.delete(0,END)
		self.tab_jvresults_scan_listbox.delete(0,END)
		
		self.sun_ids = None
		self.sun_ids = self.tab_jv_results_listbox_get_device_ids_suns(self.source_ids)
		
		col = 'scan_rate'
		ids = self.tab_jv_results_listbox_sql(col, self.sun_ids)
		for i in ids:
			self.tab_jvresults_rate_listbox.insert(END, i)
	def tab_jvresults_suns_listbox_update(self, *args):	
		self.tab_jvresults_suns_listbox.delete(0,END)
		self.tab_jvresults_rate_listbox.delete(0,END)
		self.tab_jvresults_soak_time_listbox.delete(0,END)
		self.tab_jvresults_soak_suns_listbox.delete(0,END)
		self.tab_jvresults_lux_listbox.delete(0,END)
		self.tab_jvresults_time_listbox.delete(0,END)
		self.tab_jvresults_scan_listbox.delete(0,END)
		self.source_ids = None
		self.source_ids = self.tab_jv_results_listbox_get_device_ids_sources(self.area_ids)
		col = 'sun_equiv'
		ids = self.tab_jv_results_listbox_sql(col, self.source_ids)
		for i in ids:
			self.tab_jvresults_suns_listbox.insert(END, i)
	def tab_jvresults_light_source_listbox_update(self, *args):
		self.tab_jvresults_source_listbox.delete(0,END)
		self.tab_jvresults_suns_listbox.delete(0,END)
		self.tab_jvresults_rate_listbox.delete(0,END)
		self.tab_jvresults_soak_time_listbox.delete(0,END)
		self.tab_jvresults_soak_suns_listbox.delete(0,END)
		self.tab_jvresults_lux_listbox.delete(0,END)
		self.tab_jvresults_time_listbox.delete(0,END)
		self.tab_jvresults_scan_listbox.delete(0,END)
		self.area_ids = None
		self.area_ids = self.tab_jv_results_listbox_get_device_ids_areas(self.device_ids)
		col = 'light_source'
		ids = self.tab_jv_results_listbox_sql(col, self.area_ids)
		for i in ids:
			self.tab_jvresults_source_listbox.insert(END, i)
	
	def tab_jv_results_listbox_get_device_ids_scans(self, device_list):
		device_ids = device_list
		selection = self.tab_jvresults_soak_time_listbox.curselection()
		scans = []
		
		for i in selection:
			scan = self.tab_jvresults_scan_listbox.get(i)
			scans.append(scan)
			
		results = []
			
		for device in device_ids:
			device = device[0]
			
			results_list =  []
			for scan in scans:
				start = "SELECT id FROM jv_scan_results WHERE "
				end = "ORDER BY id ASC"
				search_statement_list = []
				
				search_statement_list.append(scan)
				search_statement_list.append(device)
				middle = 'scan_id = ? AND id = ? '
				search_statement = start + middle + end
				
			
				search_statement_list =  tuple(search_statement_list)
				search = self.conn.execute(search_statement, search_statement_list);
				search_results = search.fetchall()
				
				results_list = results_list + search_results
				#### results list is a list of tuples
			results = results + results_list	
		#### get the unique sources from the ones returned ####### 	
		search_results_unique = set(i for i in results)
		search_results_unique = list(search_results_unique)
		
		return search_results_unique
	
	def tab_jv_results_listbox_get_device_ids_soak_suns(self, device_list):
		device_ids = device_list
		selection = self.tab_jvresults_soak_suns_listbox.curselection()
		
		scans = []
		
		for i in selection:
			scan = self.tab_jvresults_soak_suns_listbox.get(i)
			scans.append(scan)
			
		results = []
			
		for device in device_ids:
			device = device[0]
			
			results_list =  []
			for scan in scans:
				start = "SELECT id FROM jv_scan_results WHERE "
				end = "ORDER BY id ASC"
				search_statement_list = []
				
				search_statement_list.append(scan)
				search_statement_list.append(device)
				middle = 'soak_suns = ? AND id = ? '
				search_statement = start + middle + end
				
			
				search_statement_list =  tuple(search_statement_list)
				search = self.conn.execute(search_statement, search_statement_list);
				search_results = search.fetchall()
				
				results_list = results_list + search_results
				#### results list is a list of tuples
			results = results + results_list	
		#### get the unique sources from the ones returned ####### 	
		search_results_unique = set(i for i in results)
		search_results_unique = list(search_results_unique)
		
		return search_results_unique
		
	def tab_jv_results_listbox_get_device_ids_time(self, device_list):
		device_ids = device_list
		selection = self.tab_jvresults_time_listbox.curselection()
		scans = []
		
		for i in selection:
			scan = str(self.tab_jvresults_time_listbox.get(i))
			#convert the datetime to a unix time stamp
			scan = time.mktime(datetime.datetime.strptime(scan,'%Y/%m/%d %H:%M:%S').timetuple())
			scans.append(scan)
			
		results = []
			
		for device in device_ids:
			device = device[0]
			
			results_list =  []
			for scan in scans:
				start = "SELECT id FROM jv_scan_results WHERE "
				end = "ORDER BY id ASC"
				search_statement_list = []
				
				search_statement_list.append(scan)
				search_statement_list.append(device)
				middle = 'time_stamp = ? AND id = ? '
				search_statement = start + middle + end
				
			
				search_statement_list =  tuple(search_statement_list)
				search = self.conn.execute(search_statement, search_statement_list);
				search_results = search.fetchall()
				
				results_list = results_list + search_results
				#### results list is a list of tuples
			results = results + results_list	
		#### get the unique sources from the ones returned ####### 	
		search_results_unique = set(i for i in results)
		search_results_unique = list(search_results_unique)
		
		return search_results_unique
			
	def tab_jv_results_listbox_get_device_ids_lux(self, device_list):
		device_ids = device_list
		selection = self.tab_jvresults_lux_listbox.curselection()
		scans = []
		
		for i in selection:
			scan = self.tab_jvresults_lux_listbox.get(i)
			scans.append(scan)
			
		results = []
			
		for device in device_ids:
			device = device[0]
			
			results_list =  []
			for scan in scans:
				start = "SELECT id FROM jv_scan_results WHERE "
				end = "ORDER BY id ASC"
				search_statement_list = []
				
				search_statement_list.append(scan)
				search_statement_list.append(device)
				middle = 'lux = ? AND id = ? '
				search_statement = start + middle + end
				
			
				search_statement_list =  tuple(search_statement_list)
				search = self.conn.execute(search_statement, search_statement_list);
				search_results = search.fetchall()
				
				results_list = results_list + search_results
				#### results list is a list of tuples
			results = results + results_list	
		#### get the unique sources from the ones returned ####### 	
		search_results_unique = set(i for i in results)
		search_results_unique = list(search_results_unique)
		
		return search_results_unique
						
	def tab_jv_results_listbox_get_device_ids_soak_time(self, device_list):
		device_ids = device_list
		selection = self.tab_jvresults_soak_time_listbox.curselection()
		
		scans = []
		
		for i in selection:
			scan = self.tab_jvresults_soak_time_listbox.get(i)
			scans.append(scan)
			
		results = []
			
		for device in device_ids:
			device = device[0]
			
			results_list =  []
			for scan in scans:
				start = "SELECT id FROM jv_scan_results WHERE "
				end = "ORDER BY id ASC"
				search_statement_list = []
				
				search_statement_list.append(scan)
				search_statement_list.append(device)
				middle = 'soak_time = ? AND id = ? '
				search_statement = start + middle + end
				
			
				search_statement_list =  tuple(search_statement_list)
				search = self.conn.execute(search_statement, search_statement_list);
				search_results = search.fetchall()
				
				results_list = results_list + search_results
				#### results list is a list of tuples
			results = results + results_list	
		#### get the unique sources from the ones returned ####### 	
		search_results_unique = set(i for i in results)
		search_results_unique = list(search_results_unique)
		
		return search_results_unique
		
	def tab_jv_results_listbox_get_device_ids_rate(self, device_list):
		device_ids = device_list
		selection = self.tab_jvresults_rate_listbox.curselection()
		scans = []
		
		for i in selection:
			scan = self.tab_jvresults_rate_listbox.get(i)
			scans.append(scan)
			
		results = []
			
		for device in device_ids:
			device = device[0]
			
			results_list =  []
			for scan in scans:
				start = "SELECT id FROM jv_scan_results WHERE "
				end = "ORDER BY id ASC"
				search_statement_list = []
				
				search_statement_list.append(scan)
				search_statement_list.append(device)
				middle = 'scan_rate = ? AND id = ? '
				search_statement = start + middle + end
				
			
				search_statement_list =  tuple(search_statement_list)
				search = self.conn.execute(search_statement, search_statement_list);
				search_results = search.fetchall()
				
				results_list = results_list + search_results
				#### results list is a list of tuples
			results = results + results_list	
		#### get the unique sources from the ones returned ####### 	
		search_results_unique = set(i for i in results)
		search_results_unique = list(search_results_unique)
		
		return search_results_unique
		
	def tab_jv_results_listbox_get_device_ids_suns(self, device_list):
		device_ids = device_list
		selection = self.tab_jvresults_suns_listbox.curselection()
		suns = []
		
		for i in selection:
			sun = self.tab_jvresults_suns_listbox.get(i)
			suns.append(sun)
			
		results = []
			
		for device in device_ids:
			device = device[0]
			
			results_list =  []
			for sun in suns:
				start = "SELECT id FROM jv_scan_results WHERE "
				end = "ORDER BY id ASC"
				search_statement_list = []
				
				search_statement_list.append(sun)
				search_statement_list.append(device)
				middle = 'sun_equiv = ? AND id = ? '
				search_statement = start + middle + end
				
			
				search_statement_list =  tuple(search_statement_list)
				search = self.conn.execute(search_statement, search_statement_list);
				search_results = search.fetchall()
				
				results_list = results_list + search_results
				#### results list is a list of tuples
			results = results + results_list	
		#### get the unique sources from the ones returned ####### 	
		search_results_unique = set(i for i in results)
		search_results_unique = list(search_results_unique)
		
		return search_results_unique
		
	def tab_jv_results_listbox_get_device_ids_sources(self, device_list):
		device_ids = device_list
		selection = self.tab_jvresults_source_listbox.curselection()
		sources = []
		
		for i in selection:
			source = self.tab_jvresults_source_listbox.get(i)
			sources.append(source)
			
		results = []
			
		for device in device_ids:
			device = device[0]
			
			results_list =  []
			for source in sources:
				start = "SELECT id FROM jv_scan_results WHERE "
				end = "ORDER BY id ASC"
				search_statement_list = []
				
				search_statement_list.append(source)
				search_statement_list.append(device)
				middle = 'light_source = ? AND id = ? '
				search_statement = start + middle + end
				
			
				search_statement_list =  tuple(search_statement_list)
				search = self.conn.execute(search_statement, search_statement_list);
				search_results = search.fetchall()
				
				results_list = results_list + search_results
				#### results list is a list of tuples
			results = results + results_list	
		#### get the unique sources from the ones returned ####### 	
		search_results_unique = set(i for i in results)
		search_results_unique = list(search_results_unique)
		
		return search_results_unique
				
	def tab_jv_results_listbox_get_device_ids_areas(self, device_list):
		device_ids = device_list
		selection = self.tab_jvresults_area_listbox.curselection()
		cell_areas = []
		
		for i in selection:
			area = self.tab_jvresults_area_listbox.get(i)
			cell_areas.append(area)
			
		results = []
			
		for device in device_ids:
			results_list =  []
			for area in cell_areas:
				start = "SELECT id FROM jv_scan_results WHERE "
				end = "ORDER BY id ASC"
				search_statement_list = []
				
				search_statement_list.append(area)
				search_statement_list.append(device)
				middle = 'cell_area = ? AND id = ? '
				search_statement = start + middle + end
				
			
				search_statement_list =  tuple(search_statement_list)
				search = self.conn.execute(search_statement, search_statement_list);
				search_results = search.fetchall()
				
				results_list = results_list + search_results
				#### results list is a list of tuples
			results = results + results_list	
		#### get the unique sources from the ones returned ####### 	
		search_results_unique = set(i for i in results)
		search_results_unique = list(search_results_unique)
		
		return search_results_unique
	
	def tab_jv_results_listbox_get_device_ids_ids(self, device_list):
		device_ids = device_list
		search_results_unique = []
		
		for dev_id in device_ids:
			dev_id = dev_id[0]
			dev_id_id = self.conn.execute('SELECT id FROM jv_scan_results WHERE dev_id = ? ORDER BY id ASC', (dev_id,))
			dev_id_ids = dev_id_id.fetchall()	
			
			if dev_id_ids:
				for i in dev_id_ids:
					search_results_unique.append(i[0])
					
		return search_results_unique
						
	def tab_jvresults_listbox_get_device_ids(self, *args):	
		batches, splits, devices, pixels = self.tab_jvresults_listbox_bat_split_dev_pix_updates(self.tab_jvresults_pixel_listbox)
		bat_split_dev_pix_tup = zip(batches, splits, devices, pixels)
		#### build an sql statement #########
		results_list = []
		for i in bat_split_dev_pix_tup:
			batch = i[0]
			split = i[1]
			device = i[2]
			pixel = i[3]
			start = "SELECT id FROM dev_ids WHERE "
			end = "ORDER BY id ASC"
			search_statement_list = []
			
			search_statement_list.append(batch)
			search_statement_list.append(split)
			search_statement_list.append(device)
			search_statement_list.append(pixel)
			middle = 'batch = ? AND split = ? AND device = ? AND pixel = ? '
			search_statement = start + middle + end
			
		
			search_statement_list =  tuple(search_statement_list)
			search = self.conn.execute(search_statement, search_statement_list);
			search_results = search.fetchall()
			results_list = results_list + search_results
			
			#### get the unique ids from the ones returned #######
			##### should all be unique really.... ################ 	
			search_results_unique = set(i for i in results_list)
		
		##### all the results will be added here, its a set though, so change it back to a list
		all_device_ids = list(search_results_unique)
		self.device_ids = None
		self.device_ids = all_device_ids
		return self.device_ids
		
	def tab_jvresults_area_listbox_update(self, *args):
		##### clear the areas list first
		self.tab_jvresults_area_listbox.delete(0,END)
		self.tab_jvresults_source_listbox.delete(0,END)
		self.tab_jvresults_suns_listbox.delete(0,END)
		self.tab_jvresults_rate_listbox.delete(0,END)
		self.tab_jvresults_soak_time_listbox.delete(0,END)
		self.tab_jvresults_soak_suns_listbox.delete(0,END)
		self.tab_jvresults_lux_listbox.delete(0,END)
		self.tab_jvresults_time_listbox.delete(0,END)
		self.tab_jvresults_scan_listbox.delete(0,END)
		
		self.device_list = self.tab_jvresults_listbox_get_device_ids()
		
		self.device_ids = None
		self.device_ids = self.tab_jv_results_listbox_get_device_ids_ids(self.device_list)
		#make a list of each value as a tuple to the handling in function...
		new_device_ids = []
		
		for i in self.device_ids:
			new_device_ids.append((i,))
		
		col = 'cell_area'
		ids = self.tab_jv_results_listbox_sql(col, new_device_ids)
		
		for i in ids:
			self.tab_jvresults_area_listbox.insert(END, i)
			
	def tab_jvresults_listbox_bat_split_dev_pix_updates(self, listbox):
		listbox = listbox
		selected = listbox.curselection()
		batches = []
		splits = []
		devices = []
		pixels = []
		for i in selected:
			batch_split_dev_pixel = listbox.get(i)
			batch, split_dev_pixel = batch_split_dev_pixel.split('S')
			batch = batch[1:]
			batches.append(batch)
			split, dev_pixel = split_dev_pixel.split('D')
			splits.append(split)
			device, pixel = dev_pixel.split('P')
			devices.append(device)
			pixels.append(pixel)
		return batches, splits, devices, pixels		
	def tab_jvresults_populate_batch_listbox(self, *args):
		self.tab_jvresults_batch_listbox.delete(0,END)
		##### get the distinct batch numbers form the dev_ids ####
		batch_exists = self.conn.execute('SELECT DISTINCT batch FROM dev_ids ORDER BY batch ASC')
		batch_exists_result = batch_exists.fetchall()	
		
		if batch_exists_result:
			for i in batch_exists_result:
				self.tab_jvresults_batch_listbox.insert(END, i)
	
	def tab_jvresults_listbox_updates(self, listbox):
		listbox = listbox
		selected = listbox.curselection()
		items = []
		for i in selected:
			items.append(listbox.get(i))
		return items	
	def tab_jvresults_listbox_bat_split_dev_updates(self, listbox):
		listbox = listbox
		selected = listbox.curselection()
		batches = []
		splits = []
		devices = []
		for i in selected:
			batch_split_dev = listbox.get(i)
			batch, split_dev = batch_split_dev.split('S')
			batch = batch[1:]
			batches.append(batch)
			split, device = split_dev.split('D')
			splits.append(split)
			devices.append(device)
		return batches, splits, devices
		
	def tab_jvresults_populate_pixel_listbox(self, *args):
		##### clear the pixels list first
		self.tab_jvresults_pixel_listbox.delete(0,END)
		self.tab_jvresults_area_listbox.delete(0,END)
		self.tab_jvresults_source_listbox.delete(0,END)
		self.tab_jvresults_scan_listbox.delete(0,END)
		self.tab_jvresults_suns_listbox.delete(0,END)
		self.tab_jvresults_soak_time_listbox.delete(0,END)
		self.tab_jvresults_soak_suns_listbox.delete(0,END)
		self.tab_jvresults_lux_listbox.delete(0,END)
		self.tab_jvresults_time_listbox.delete(0,END)
		self.tab_jvresults_rate_listbox.delete(0,END)
		
		### using the batch and split and device numbers from the device names ####
		### get the pixels available for these batch+splits+pixels ####
		batches, splits, devices = self.tab_jvresults_listbox_bat_split_dev_updates(self.tab_jvresults_device_listbox)
		### combine the two lists into a list of tuples, easier for handling later on
		bat_split_dev_tup = zip(batches, splits, devices)
		#### build an sql statement #########
		batch_split_device_pixel = []
		for i in bat_split_dev_tup:
			search_results = []
			batch = i[0]
			split = i[1]
			device = i[2]
			start = "SELECT pixel FROM dev_ids WHERE "
			end = "ORDER BY pixel ASC"
			search_statement_list = []
			
			search_statement_list.append(batch)
			search_statement_list.append(split)
			search_statement_list.append(device)
			middle = 'batch = ? AND split = ? AND device = ? '
			search_statement = start + middle + end
			
		
			search_statement_list =  tuple(search_statement_list)
			search = self.conn.execute(search_statement, search_statement_list);
			search_results = search.fetchall()
			
			#### get the unique devices from the ones returned ####### 	
			search_results_unique = set(i for i in search_results)
			for t in search_results_unique:
				t = ((i[0],)+(i[1],)+(i[2],)+t)
				batch_split_device_pixel.append(t)
				
		names_list = []	
		for i in batch_split_device_pixel:
			batch = i[0]
			split = i[1]
			device = i[2]
			pixel = i[3]
			name = 'B%sS%sD%sP%s' % (batch, split, device, pixel)
			names_list.append(name)
		names_list.sort()
		for name in names_list:	
			self.tab_jvresults_pixel_listbox.insert(END, name)
			
	def tab_jvresults_listbox_bat_split_updates(self, listbox):
		listbox = listbox
		selected = listbox.curselection()
		batches = []
		splits = []
		for i in selected:
			batch_split = listbox.get(i)
			batch, split = batch_split.split('S')
			batch = batch[1:]
			batches.append(batch)
			splits.append(split)
		return batches, splits
	def tab_jvresults_populate_device_listbox(self, *args):
		##### clear the devices list first
		self.tab_jvresults_device_listbox.delete(0,END)
		self.tab_jvresults_pixel_listbox.delete(0,END)
		self.tab_jvresults_area_listbox.delete(0,END)
		self.tab_jvresults_source_listbox.delete(0,END)
		self.tab_jvresults_scan_listbox.delete(0,END)
		self.tab_jvresults_suns_listbox.delete(0,END)
		self.tab_jvresults_soak_time_listbox.delete(0,END)
		self.tab_jvresults_soak_suns_listbox.delete(0,END)
		self.tab_jvresults_lux_listbox.delete(0,END)
		self.tab_jvresults_time_listbox.delete(0,END)
		self.tab_jvresults_rate_listbox.delete(0,END)
		### using the batch and split numbers from the split names ####
		### get the devices available for these batch+splits ####
		batches, splits = self.tab_jvresults_listbox_bat_split_updates(self.tab_jvresults_split_listbox)
		### combine the two lists into a list of tuples, easier for handling later on
		bat_split_tup = zip(batches, splits)
		#### build an sql statement #########
		
		batch_split_device = []
		for i in bat_split_tup:
			search_results = []
			batch = i[0]
			split = i[1]
			start = "SELECT device FROM dev_ids WHERE "
			end = "ORDER BY device ASC"
			search_statement_list = []
			
			search_statement_list.append(batch)
			search_statement_list.append(split)
			middle = 'batch = ? AND split = ? '
			search_statement = start + middle + end
			
		
			search_statement_list =  tuple(search_statement_list)
			search = self.conn.execute(search_statement, search_statement_list);
			search_results = search.fetchall()
			
			#### get the unique devices from the ones returned ####### 	
			search_results_unique = set(i for i in search_results)
			for t in search_results_unique:
				t = ((i[0],)+(i[1],)+t)
				batch_split_device.append(t)
				
		names_list = []	
		for i in batch_split_device:
			batch = i[0]
			split = i[1]
			device = i[2]
			name = 'B%sS%sD%s' % (batch, split, device)
			names_list.append(name)
		names_list.sort()
		for name in names_list:	
			self.tab_jvresults_device_listbox.insert(END, name)
			
	def tab_jvresults_populate_split_listbox(self, *args):
		##### clear the splits list first
		self.tab_jvresults_split_listbox.delete(0,END)
		self.tab_jvresults_device_listbox.delete(0,END)
		self.tab_jvresults_pixel_listbox.delete(0,END)
		self.tab_jvresults_area_listbox.delete(0,END)
		self.tab_jvresults_source_listbox.delete(0,END)
		self.tab_jvresults_scan_listbox.delete(0,END)
		self.tab_jvresults_suns_listbox.delete(0,END)
		self.tab_jvresults_soak_time_listbox.delete(0,END)
		self.tab_jvresults_soak_suns_listbox.delete(0,END)
		self.tab_jvresults_lux_listbox.delete(0,END)
		self.tab_jvresults_time_listbox.delete(0,END)
		self.tab_jvresults_rate_listbox.delete(0,END)
		##### Using the batches selected get the split numbers for these batches ######
		batches = self.tab_jvresults_listbox_updates(self.tab_jvresults_batch_listbox)
		##### a list of tuples with each batch as first item in tuple #####
		##### build a sql statement using the batches selected #####
		#### search for the splits in each batch #######
		
		batch_split = []
		for i in batches:
			search_results = []
			start = "SELECT split FROM dev_ids WHERE "
			end = "ORDER BY split ASC"
			search_statement_list = []
			
			batch = i[0]
			search_statement_list.append(batch)
			middle = 'batch = ? '
			search_statement = start + middle + end
			
		
			search_statement_list =  tuple(search_statement_list)
			search = self.conn.execute(search_statement, search_statement_list);
			search_results = search.fetchall()
			
			
			#### get the unique splits from the ones returned ####### 	
			search_results_unique = set(i for i in search_results)
			for t in search_results_unique:
				t = (i+t)
				batch_split.append(t)
		#### batch_split is a list of tuples, the first item in each tuple is the batch number and the second the split #######
		names_list = []
		for i in batch_split:
			batch = i[0]
			split = i[1]
			name = 'B%sS%s' % (batch, split)
			names_list.append(name)
		names_list.sort()
		for name in names_list:
			self.tab_jvresults_split_listbox.insert(END, name)
	def tab_jvresults_time_listbox_vsb_yview(self, *args):
		self.tab_jvresults_time_listbox.yview(*args)
	def tab_jvresults_lux_listbox_vsb_yview(self, *args):
		self.tab_jvresults_lux_listbox.yview(*args)		
	def tab_jvresults_soak_suns_listbox_vsb_yview(self, *args):
		self.tab_jvresults_soak_suns_listbox.yview(*args)		
	def tab_jvresults_soak_time_listbox_vsb_yview(self, *args):
		self.tab_jvresults_soak_time_listbox.yview(*args)		
	def tab_jvresults_suns_listbox_vsb_yview(self, *args):
		self.tab_jvresults_suns_listbox.yview(*args)		
	def tab_jvresults_rate_listbox_vsb_yview(self, *args):
		self.tab_jvresults_rate_listbox.yview(*args)			
	def tab_jvresults_source_listbox_vsb_yview(self, *args):
		self.tab_jvresults_source_listbox.yview(*args)	
	def tab_jvresults_scan_listbox_vsb_yview(self, *args):
		self.tab_jvresults_scan_listbox.yview(*args)		
	def tab_jvresults_pixel_listbox_vsb_yview(self, *args):
		self.tab_jvresults_pixel_listbox.yview(*args)		
	def tab_jvresults_device_listbox_vsb_yview(self, *args):
		self.tab_jvresults_device_listbox.yview(*args)			
	def tab_jvresults_area_listbox_vsb_yview(self, *args):
		self.tab_jvresults_area_listbox.yview(*args)	
	def tab_jvresults_split_listbox_vsb_yview(self, *args):
		self.tab_jvresults_split_listbox.yview(*args)	
	def tab_jvresults_batch_listbox_vsb_yview(self, *args):
		self.tab_jvresults_batch_listbox.yview(*args)
	def update_jvresults_canvas_scroll(self, *args):
		self.tab_jvresults_canvas.config(scrollregion=self.tab_jvresults_canvas.bbox(ALL))	
	def batches_tk(self, *args):
		##### A canvas in the frame ######
		self.tab_batches_canvas = Canvas(self.tab_batches, width=1300, height=600)
		self.tab_batches_canvas.grid(row=0, column=0)
		
		#A frame in canvas to hold all the other widgets
		self.tab_batches_frame = Frame(self.tab_batches_canvas, width=1300, height=600)
		self.tab_batches_frame.grid(row=1, column=0, sticky=W)
		
		#A scroll bar in the tab that controls the canvas position
		self.tab_batches_scroll = Scrollbar(self.tab_batches, orient='vertical', command=self.tab_batches_canvas.yview)
		
		self.tab_batches_canvas.configure(yscrollcommand=self.tab_batches_scroll.set)
		
		self.tab_batches_scroll.grid(row=0, column=1, sticky=N+S)
		#A window for the canvas
		self.tab_batches_canvas.create_window((4,4), window=self.tab_batches_frame, anchor="nw")
		
		self.tab_batches_frame.bind("<Configure>", self.update_batches_canvas_scroll)
		
		#Another frame in the first frame
		self.tab_batches_info_frame = Frame(self.tab_batches_frame, width=1000, height=600)
		self.tab_batches_info_frame.grid(row=0, column=0, sticky=W)
		
		self.tab_batches_num_label = Label(self.tab_batches_info_frame, text='Batch Number:')
		self.tab_batches_num_label.grid(row=0, column=0, sticky=E)	
		
		###### combo box with the batch numbers #######
		self.tab_batches_num_box_var = StringVar()
		self.tab_batches_num_list = []
		self.tab_batches_num_box = Combobox(self.tab_batches_info_frame, textvariable=self.tab_batches_num_box_var, width=15)
		#### first box so no need for a command #####
		self.tab_batches_num_box.bind('<<ComboboxSelected>>', self.update_batches_info)
		self.tab_batches_num_box['values'] = self.tab_batches_num_list
		self.tab_batches_num_box.grid(row=0, column=1, sticky=W)
		self.tab_batches_num_box.state(['readonly'])
		#### populate the list ###########
		self.update_tab_batches_number_combo()
		
		self.tab_batches_add_new_but = Button(self.tab_batches_info_frame, command=self.tab_batches_add_new_batch_num, text='Add New Batch Number', width=30)
		self.tab_batches_add_new_but.grid(row=0, column=2, sticky=E, columnspan=4)
		
		#For the user
		self.tab_batches_user_label = Label(self.tab_batches_info_frame, text='Owner:')
		self.tab_batches_user_label.grid(row=1, column=0, sticky=E)
		
		self.tab_batches_user_box_var = StringVar()
		self.tab_batches_user_list = []
		self.tab_batches_user_box = Combobox(self.tab_batches_info_frame, textvariable=self.tab_batches_user_box_var, width=25)
		#### first box so no need for a command #####
		self.tab_batches_user_box['values'] = self.tab_batches_user_list
		self.tab_batches_user_box.grid(row=1, column=1, sticky=W)
		self.tab_batches_user_box.state(['readonly'])
		self.update_tab_batches_user_combo()
		
		self.tab_batches_name_label = Label(self.tab_batches_info_frame, text='Batch Name:')
		self.tab_batches_name_label.grid(row=2, column=0, sticky=E)
		
		self.tab_batches_name_var = StringVar()
		self.tab_batches_name = Entry(self.tab_batches_info_frame, textvariable=self.tab_batches_name_var, width=50)
		self.tab_batches_name.grid(row=2, column=1, sticky=W, columnspan=10)
	
		self.tab_batches_desc_label = Label(self.tab_batches_info_frame, text='Batch Description:')
		self.tab_batches_desc_label.grid(row=3, column=0, sticky=E)
		
		self.tab_batches_desc_text = Text(self.tab_batches_info_frame, width=60, height=5)
		self.tab_batches_desc_text.grid(row=3, column=1, sticky=W, columnspan=10)
	
		self.tab_batches_split_frame = Frame(self.tab_batches_frame)
		self.tab_batches_split_frame.grid(row=1, column=0, sticky=W)
		
		self.tab_batches_split_label = Label(self.tab_batches_split_frame, text='Split:')
		self.tab_batches_split_label.grid(row=1, column=0, sticky=W)
		
		self.tab_batches_split_spin_var = StringVar()
		self.tab_batches_split_spin = Spinbox(self.tab_batches_split_frame, from_=00, to=99, increment=1, textvariable=self.tab_batches_split_spin_var, width=5)
		self.tab_batches_split_spin.grid(row=2, column=0, sticky=NW)
		self.tab_batches_split_spin_var.set(0)
		
		self.tab_batches_split_name_label = Label(self.tab_batches_split_frame, text='Split Name:')
		self.tab_batches_split_name_label.grid(row=1, column=1, sticky=W)
		
		self.tab_batches_split_name_entry_var = StringVar()
		self.tab_batches_split_name_entry = Entry(self.tab_batches_split_frame, textvariable=self.tab_batches_split_name_entry_var, width=40)
		self.tab_batches_split_name_entry.grid(row=2, column=1, sticky=NW)	
		
		self.tab_batches_device_label = Label(self.tab_batches_split_frame, text='Devices:')
		self.tab_batches_device_label.grid(row=1, column=2, sticky=W)
		
		self.tab_batches_device_spin_var = StringVar()
		self.tab_batches_device_spin = Spinbox(self.tab_batches_split_frame, from_=00, to=99, increment=1, textvariable=self.tab_batches_device_spin_var, width=5)
		self.tab_batches_device_spin.grid(row=2, column=2, sticky=NW)
		self.tab_batches_device_spin_var.set(False)
		
		self.tab_batches_split_desc_label = Label(self.tab_batches_split_frame, text='Description:')
		self.tab_batches_split_desc_label.grid(row=1, column=3, sticky=W)
		
		self.tab_batches_split_desc_text = Text(self.tab_batches_split_frame, width=30, height=4)
		self.tab_batches_split_desc_text.grid(row=2, column=3, sticky=W)
		
		self.tab_batches_split_stack_label = Label(self.tab_batches_split_frame, text='Device Stack:')
		self.tab_batches_split_stack_label.grid(row=1, column=4, sticky=W)
		
		self.tab_batches_stack_box_var = StringVar()
		self.tab_batches_stack_list = []
		self.tab_batches_stack_box = Combobox(self.tab_batches_split_frame, textvariable=self.tab_batches_stack_box_var, width=20)
		#### first box so no need for a command #####
		self.tab_batches_stack_box.bind('<<ComboboxSelected>>')
		self.tab_batches_stack_box['values'] = self.tab_batches_stack_list
		self.tab_batches_stack_box.grid(row=2, column=4, sticky=NW)
		self.tab_batches_stack_box.state(['readonly'])
		#### populate the list ###########
		self.update_tab_batches_split_stack_combo()
		
		self.tab_batches_split_add_but = Button(self.tab_batches_split_frame, text='Add Split', command=self.tab_batches_add_split_list)
		self.tab_batches_split_add_but.grid(row=2, column=5, sticky=NW,columnspan=25)
		
		
		############ list frame #################
		#########################################
		self.tab_batches_split_list_frame = Frame(self.tab_batches_split_frame)
		self.tab_batches_split_list_frame.grid(row=0, column=0, sticky=W, columnspan=25)
		
		self.tab_batches_listbox_vsb = Scrollbar(self.tab_batches_split_list_frame)
		self.tab_batches_listbox_vsb.grid(row=1, column=7, sticky=N+S)
		
		self.tab_batches_split_list_label = Label(self.tab_batches_split_list_frame, text='Split')
		self.tab_batches_split_list_label.grid(row=0, column=0,sticky=W)
		
		self.tab_batches_split_name_list_label = Label(self.tab_batches_split_list_frame, text='Split Name')
		self.tab_batches_split_name_list_label.grid(row=0, column=1,sticky=W)
		
		self.tab_batches_device_list_label = Label(self.tab_batches_split_list_frame, text='Devices')
		self.tab_batches_device_list_label.grid(row=0, column=2,sticky=W)
		
		self.tab_batches_pixel_list_label = Label(self.tab_batches_split_list_frame, text='Pixels')
		self.tab_batches_pixel_list_label.grid(row=0, column=3,sticky=W)
		
		self.tab_batches_yield_list_label = Label(self.tab_batches_split_list_frame, text='Yield')
		self.tab_batches_yield_list_label.grid(row=0, column=4,sticky=W)
		
		self.tab_batches_desc_list_label = Label(self.tab_batches_split_list_frame, text='Description')
		self.tab_batches_desc_list_label.grid(row=0, column=5,sticky=W)
		
		self.tab_batches_stack_list_label = Label(self.tab_batches_split_list_frame, text='Device Stack')
		self.tab_batches_stack_list_label.grid(row=0, column=6,sticky=W)
		
		self.tab_batches_split_listbox = Listbox(self.tab_batches_split_list_frame, yscrollcommand=self.tab_batches_listbox_vsb.set, exportselection=False, width=5)
		self.tab_batches_split_listbox.grid(row=1, column=0, sticky=W)
		self.tab_batches_split_listbox.bind('<<ListboxSelect>>', self.tab_batches_split_listbox_selection)
		
		self.tab_batches_split_name_listbox = Listbox(self.tab_batches_split_list_frame, yscrollcommand=self.tab_batches_listbox_vsb.set, exportselection=False, width=40)
		self.tab_batches_split_name_listbox.grid(row=1, column=1, sticky=W)
		self.tab_batches_split_name_listbox.bind('<<ListboxSelect>>', self.tab_batches_split_name_listbox_selection)
		
		self.tab_batches_device_listbox = Listbox(self.tab_batches_split_list_frame, yscrollcommand=self.tab_batches_listbox_vsb.set, exportselection=False, width=6)
		self.tab_batches_device_listbox.grid(row=1, column=2, sticky=W)
		self.tab_batches_device_listbox.bind('<<ListboxSelect>>', self.tab_batches_device_listbox_selection)
		
		self.tab_batches_pixel_listbox = Listbox(self.tab_batches_split_list_frame, yscrollcommand=self.tab_batches_listbox_vsb.set, exportselection=False, width=5)
		self.tab_batches_pixel_listbox.grid(row=1, column=3, sticky=W)
		self.tab_batches_pixel_listbox.bind('<<ListboxSelect>>', self.tab_batches_pixel_listbox_selection)
		
		self.tab_batches_yield_listbox = Listbox(self.tab_batches_split_list_frame, yscrollcommand=self.tab_batches_listbox_vsb.set, exportselection=False, width=5)
		self.tab_batches_yield_listbox.grid(row=1, column=4, sticky=W)
		self.tab_batches_yield_listbox.bind('<<ListboxSelect>>', self.tab_batches_yield_listbox_selection)

		self.tab_batches_split_desc_listbox = Listbox(self.tab_batches_split_list_frame, yscrollcommand=self.tab_batches_listbox_vsb.set, exportselection=False, width=20)
		self.tab_batches_split_desc_listbox.grid(row=1, column=5, sticky=W)
		self.tab_batches_split_desc_listbox.bind('<<ListboxSelect>>', self.tab_batches_split_desc_listbox_selection)
		
		self.tab_batches_split_stack_listbox = Listbox(self.tab_batches_split_list_frame, yscrollcommand=self.tab_batches_listbox_vsb.set, exportselection=False, width=25)
		self.tab_batches_split_stack_listbox.grid(row=1, column=6, sticky=W)
		self.tab_batches_split_stack_listbox.bind('<<ListboxSelect>>', self.tab_batches_split_stack_listbox_selection)
		
		self.tab_batches_listbox_vsb.config(command=self.tab_batches_list_vsb)
		
		#############Picture frame#########################
		####################################################################
		self.tab_batches_picture_frame = LabelFrame(self.tab_batches_frame, text='Device Stack Picture')
		self.tab_batches_picture_frame.grid(row=0, column=8, sticky=NW, columnspan=1, rowspan=20)
		
		self.tab_batches_picture_canvas = Canvas(self.tab_batches_picture_frame, width=350, height=500)
		self.tab_batches_picture_canvas.grid(row=0, column=0)
		self.tab_batches_picture_canvas.config(scrollregion=(0,0,350,1000))
		
		
		#A scroll bar in the tab that controls the canvas position
		self.tab_batches_picture_scroll = Scrollbar(self.tab_batches_picture_frame, orient='vertical', command=self.tab_batches_picture_canvas.yview)
		self.tab_batches_picture_scroll.grid(row=0, column=1, sticky=N+S)
		
		self.tab_batches_picture_canvas.configure(yscrollcommand=self.tab_batches_picture_scroll.set,scrollregion=self.tab_batches_picture_canvas.bbox("all"))
		self.tab_batches_picture_canvas.yview_moveto(1)
		
		
		##################################################
		
		self.tab_batches_split_remove_but = Button(self.tab_batches_split_list_frame, text='Remove Split', command=self.tab_batches_remove_split)
		self.tab_batches_split_remove_but.grid(row=2, column=0, sticky=W, columnspan=25)
		
		self.tab_batches_commit_frame = Frame(self.tab_batches_frame)
		self.tab_batches_commit_frame.grid(row=2, column=0, sticky=W, columnspan=25)
		
		self.tab_batches_commit_batch_but = Button(self.tab_batches_commit_frame, text='Commit Batch to Database', command=self.tab_batches_commit)
		self.tab_batches_commit_batch_but.grid(row=3, column=0, sticky=W)
		
		self.tab_batches_update_batch_but = Button(self.tab_batches_commit_frame, text='Update Batch Details', command=self.tab_batches_update)
		self.tab_batches_update_batch_but.grid(row=3, column=1, sticky=W)
		
		self.tab_batches_status_lab_var = StringVar()
		self.tab_batches_status_lab = Label(self.tab_batches_commit_frame, textvariable=self.tab_batches_status_lab_var)
		self.tab_batches_status_lab.grid(row=4, column=0, sticky=W, columnspan=10)
		self.tab_batches_status_lab_var.set('Status:')
	
		self.tab_batches_import_but = Button(self.tab_batches_commit_frame, text='Import batch JV data', command=self.tab_batches_jv_import)
		self.tab_batches_import_but.grid(row=5, column=0, sticky=W, columnspan=25)
		
		self.tab_batches_print_but = Button(self.tab_batches_commit_frame, text='Print Device Labels', command=self.tab_batches_print_label)
		self.tab_batches_print_but.grid(row=5, column=1, sticky=E, columnspan=25)
		###########################################################
		###########################################################
		self.tab_batches_notes_frame = Frame(self.tab_batches_frame)
		self.tab_batches_notes_frame.grid(row=3, column=0, sticky=W)
		
		self.tab_batches_notes_label = Label(self.tab_batches_notes_frame, text='Batch Notes:')
		self.tab_batches_notes_label.grid(row=0, column=0, sticky=W)
		
		self.tab_batches_notes_text = Text(self.tab_batches_notes_frame, width=100, height=10)
		self.tab_batches_notes_text.grid(row=1, column=0, sticky=W, columnspan=25)
		
		self.tab_batches_notes_but = Button(self.tab_batches_notes_frame, text='Update Batch Notes', command=self.tab_batches_note_update)
		self.tab_batches_notes_but.grid(row=2, column=0, columnspan=25,sticky=W)
			
			
	def tab_batches_update(self, *args):
		#pass
		#Need to update the batch data and also the split data 
		#Batch data update is easy enough just update each field
		#The splits are a bit more tricky...
		#If more or less splits have been added need to delete the splits table ids that correspond to this batch number
		
		#First get the batch number
		####Get the batch id#####
		batch_num = self.tab_batches_num_box.get()
		#### check the batch num exists in database #######
		id_select = self.conn.execute('SELECT id FROM device_batches WHERE batch_num = ?', (batch_num,))
		id_select_result = id_select.fetchall()

		if not id_select_result:
			self.tab_batches_status_lab_var.set('Status: No batch number selected...')
		else:	
			#Update the batch records
			batch_id = id_select_result[0][0]
			#CREATE TABLE device_batches (id INTEGER PRIMARY KEY, batch_num INTEGER, batch_name TEXT, batch_desc TEXT, batch_notes TEXT, owner TEXT DEFAULT 'Anon');
			###Get the notes and description#####
			batch_desc = self.tab_batches_desc_text.get(1.0,END)
			batch_desc = batch_desc[:-1]
			
			batch_notes = self.tab_batches_notes_text.get(1.0,END)
			batch_notes = batch_notes[:-1]
			
			batch_dict = {
						'batch_name':self.tab_batches_name.get(),
						'batch_desc':batch_desc,
						'batch_notes':batch_notes,
						'owner':str(self.tab_batches_user_box.get()),
						}
			
			for key, value in batch_dict.iteritems():
				print key
				print value
				self.conn.execute('UPDATE device_batches SET '+key+' = ? WHERE id = ?',(value,batch_id,));
				self.conn.commit()	
			
			#Now remove the splits associated with the batch and then recommit...
			self.conn.execute('DELETE FROM splits WHERE batch_id = ?',(batch_id,));
			self.conn.commit()
			
			splits_lst = []			
			for index, i in enumerate(self.tab_batches_split_listbox.get(0, END)):
				splits_dict = {}
				splits_dict['split'] = i
				splits_dict['split_name'] = self.tab_batches_split_name_listbox.get(index)
				splits_dict['split_desc'] = self.tab_batches_split_desc_listbox.get(index)
				splits_dict['num_devs'] = self.tab_batches_device_listbox.get(index)
				splits_dict['num_pix'] = self.tab_batches_pixel_listbox.get(index)
				splits_dict['yield'] = self.tab_batches_yield_listbox.get(index)
				#Get stack name as id
				stack_id_exists = self.conn.execute('SELECT id FROM device_stacks WHERE stack_name = ?', (self.tab_batches_split_stack_listbox.get(index),))
				stack_id_exists_result = stack_id_exists.fetchone()[0]
	
				splits_dict['split_stack'] = stack_id_exists_result
			
				splits_lst.append(splits_dict)
			
			#Make an entry for the batch and use its id as the batch_id	
			splits_inserted = self.batch_update_function(self, self.conn, batch_id, splits_lst)
	
			self.tab_batches_status_lab_var.set(splits_inserted[1])
				
	def update_tab_batches_user_combo(self,*args):
		select = self.conn.execute('SELECT name FROM users')
		select_results = select.fetchall()
		if select_results:	
			for i in select_results:
				if str(i[0]):
					self.tab_batches_user_list.append(i[0])
		self.tab_batches_user_list = list(self.tab_batches_user_list)			
		self.tab_batches_user_box['values'] = self.tab_batches_user_list
		
	def tab_batches_print_label(self, *args):
		#Get the current batch
		batch_num = self.tab_batches_num_box.get()
		#### check the batch num exists in database #######
		id_select = self.conn.execute('SELECT id FROM device_batches WHERE batch_num = ?', (batch_num,))
		id_select_result = id_select.fetchall()
		
		if not id_select_result:
			self.tab_batches_status_lab_var.set('Status: No batch number selected.')
		else:
			#Get the splits
			splits = []
			for index, i in enumerate(self.tab_batches_split_stack_listbox.get(0, END)):
				##Get the bot and top elec patterns from the stack name
				stack_name_exists = self.conn.execute('SELECT id FROM device_stacks WHERE stack_name = ?', (i,))
				stack_name_exists_result = stack_name_exists.fetchone()[0]
				
				if str(stack_name_exists_result) == 'None':
					pass
				else:
					bot_elec_exists = self.conn.execute('SELECT bot_elec_pat FROM device_stacks WHERE id = ?', (stack_name_exists_result,))
					bot_elec_exists_result = bot_elec_exists.fetchone()[0]
					
					top_elec_exists = self.conn.execute('SELECT top_elec_pat FROM device_stacks WHERE id = ?', (stack_name_exists_result,))
					top_elec_exists_result = top_elec_exists.fetchone()[0]
					
				splits.append((int(self.tab_batches_split_listbox.get(index)),int(self.tab_batches_device_listbox.get(index)),self.tab_batches_split_desc_listbox.get(index),self.tab_batches_split_stack_listbox.get(index),top_elec_exists_result,bot_elec_exists_result))
			#Now print the labels...
			for i in splits:
				for ii in range(i[1]):
					qr = """^XA^FO50,50^BQ,2,2^FDQA,""" + 'B%03dS%02dD%02d,%s,%s' % (int(id_select_result[0][0]),i[0],ii,i[4],i[5])+ """^FS"""

					line0 = """^FO40,20^FD"""+'ID: B%03dS%02dD%02d' % (int(id_select_result[0][0]),i[0],ii)+"""^FS"""
					line1 = """^FO40,30^FD"""+"%s" % (str(i[2])[0:25])+"""^FS"""
					line2 = """^FO40,40^FD"""+"%s" % (str(i[2])[25:50])+"""^FS"""
					line3 = """^FO120,55^FD"""+"%s" % (i[3][0:15])+"""^FS"""
					line4 = """^FO120,65^FD"""+"%s" % (i[3][15:30])+"""^FS"""
					line5 = """^FO120,75^FD"""+"%s" % (i[3][30:45])+"""^FS"""
					line6 = """^FO120,95^FD"""+"TE: %s" % (i[4])+"""^FS"""
					line7 = """^FO120,105^FD"""+"BE: %s" % (i[5])+"""^FS"""
					line8 = """^FO120,115^FD"""+"Date: %s%s%s" % (time.strftime("%Y"),time.strftime("%m"),time.strftime("%d"))+"""^FS"""
					time.strftime("%d")
					lab_end = """^XZ"""
					
					label = qr+line0+line1+line2+line3+line4+line5+line6+line7+line8+lab_end
					self.print_lab(label,self.printer)
	def tab_batches_note_update(self, *args):
		####Get the batch id#####
		batch_num = self.tab_batches_num_box.get()
		#### check the batch num exists in database #######
		id_select = self.conn.execute('SELECT id FROM device_batches WHERE batch_num = ?', (batch_num,))
		id_select_result = id_select.fetchall()

		if not id_select_result:
			self.tab_batches_status_lab_var.set('Status: No batch number selected- check notes and update batch number.')
		else:	
			###Get the notes #####
			notes = str(self.tab_batches_notes_text.get(1.0,END))
			batch_id = id_select_result[0][0]
			self.conn.execute('UPDATE device_batches SET batch_notes = ? WHERE id = ?',(notes, batch_id,));
			self.conn.commit()	
			
	def tab_batches_set_picture(self, stack):	
		####Clear the picture#####
		self.tab_batches_picture_canvas.delete(ALL)
		### check for the device stack name in table ####
		select = self.conn.execute('SELECT id FROM device_stacks WHERE stack_name = ?', (stack,))
		select_result =select.fetchone()[0]
		select_result = str(select_result)
		#### for the id get the values and add to the listboxes ######
		if select_result:
			q = 0
			lq = 0
			#Use the device_stacks id to find the parts rows that have that device_stack_id
			rows = self.conn.execute('SELECT id FROM device_stack_parts WHERE device_stack_id = ?', (select_result,))
			rows_result =rows.fetchall() 

			for i in rows_result:
				i = i[0]
				#use the part type to select a layer or treatment
				part_type = self.conn.execute('SELECT type_id FROM device_stack_parts WHERE id = ?', (i,))
				part_type_result = part_type.fetchone()[0]
				
				part_id = self.conn.execute('SELECT part_id FROM device_stack_parts WHERE id = ?', (i,))
				part_id_result = part_id.fetchone()[0]
				
				#if the type is layer use the layers table or if treatments use treatments table...
				if part_type_result == 0:
					#This is for layers (only layers in the picture?)
					#### get the layer name from the layer id ######
					layer_name = self.conn.execute('SELECT layer_name FROM layers WHERE id = ?', (part_id_result,))
					layer_name_results = layer_name.fetchone()[0]
					layer_name_results = str(layer_name_results)
					
					layer_colour = self.conn.execute('SELECT layer_colour FROM layers WHERE id = ?', (part_id_result,))
					layer_colour_results = layer_colour.fetchone()[0]
					if layer_colour_results == None:
						layer_colour_result = "#ffffff"
					else:
						layer_colour_result = str(layer_colour_results)
					
					#print layer_colour_result
					###Add to the picture####
					if lq == 0:
						qy = 500
						qyy = 500-60
						qx = 20
						qxx = 320
					else:
						qy = qy-61
						qyy = qy-60
						qx = 40
						qxx = 300
					
					self.tab_batches_picture_canvas.create_rectangle(qx, qy, qxx, qyy, fill=layer_colour_result)
					self.tab_batches_picture_canvas.create_text(45, qy-55, text=str(layer_name_results),width=250,anchor=NW)
					
					lq = lq+1
					q = q+1
				
			self.tab_batches_picture_canvas.config(scrollregion=self.tab_batches_picture_canvas.bbox(ALL))							
	
	def tab_batches_jv_import(self, *args):
		batch_num = int(self.tab_batches_num_box.get())
		if isinstance(batch_num, int ):
			self.import_batch_data(self, self.conn, batch_num, self.base_file_path)	
			self.tab_jvresults_populate_batch_listbox()
		else:	
			print 'Batch number not as expected'	
	def update_tab_batches_split_stack_combo(self, *args):
		###### get all the names of the device stacks ######
		self.tab_batches_stack_list = []
		self.tab_batches_stack_box['values'] = self.tab_batches_stack_list
		batches_stack_exists = self.conn.execute('SELECT stack_name FROM device_stacks')
		batches_stack_exists_result = batches_stack_exists.fetchall()	
		
		if batches_stack_exists_result:
			for i in batches_stack_exists_result:
				self.tab_batches_stack_list.append(i[0])
			self.tab_batches_stack_box['values'] = list(reversed(self.tab_batches_stack_list))	
	def tab_batches_commit(self, *args):
		####
		#Needs to be updated to check the batch number doesn't already have a batch committed to it
		#if the name is changed then the batch can be recommitted with the same number. 
		###### check if the batch name already exists #######	
		batch_name_exists_select = self.conn.execute('SELECT id FROM device_batches WHERE batch_name = ?', (self.tab_batches_name.get(),))
		batch_name_exists_select_result = batch_name_exists_select.fetchall()
		
		batch_id_exists_select = self.conn.execute('SELECT id FROM device_batches WHERE batch_num = ?', (self.tab_batches_name.get(),))
		batch_id_exists_select_result = batch_id_exists_select.fetchall()
		
		if batch_name_exists_select_result:
			self.tab_batches_status_lab_var.set('Status: Batch name already exists, update and try again.')
		elif batch_id_exists_select_result:
			self.tab_batches_status_lab_var.set('Status: Batch number already exists, update and try again.')
		else:
			batch_desc = self.tab_batches_desc_text.get(1.0,END)
			batch_desc = batch_desc[:-1]
			batch_notes = self.tab_batches_notes_text.get(1.0,END)
			batch_notes = batch_notes[:-1]
			
			batch_dict = {
						'batch_name':self.tab_batches_name.get(),
						'batch_num':self.tab_batches_num_box.get(),
						'batch_desc':batch_desc,
						'batch_notes':batch_notes,
						'owner':str(self.tab_batches_user_box.get()),
						}
						
						
			splits_lst = []			
			for index, i in enumerate(self.tab_batches_split_listbox.get(0, END)):
				splits_dict = {}
				splits_dict['split'] = i
				splits_dict['split_name'] = self.tab_batches_split_name_listbox.get(index)
				splits_dict['split_desc'] = self.tab_batches_split_desc_listbox.get(index)
				splits_dict['num_devs'] = self.tab_batches_device_listbox.get(index)
				splits_dict['num_pix'] = self.tab_batches_pixel_listbox.get(index)
				splits_dict['yield'] = self.tab_batches_yield_listbox.get(index)
				#Get stack name as id
				stack_id_exists = self.conn.execute('SELECT id FROM device_stacks WHERE stack_name = ?', (self.tab_batches_split_stack_listbox.get(index),))
				stack_id_exists_result = stack_id_exists.fetchone()[0]
	
				splits_dict['split_stack'] = stack_id_exists_result
			
				splits_lst.append(splits_dict)
			
			#Make an entry for the batch and use its id as the batch_id	
			batches_inputs_inserted = self.batch_commit_function(self, self.conn, splits_lst, batch_dict)
	
			self.tab_batches_status_lab_var.set(batches_inputs_inserted[1])
			self.update_tab_batches_number_combo()	
												
	def tab_batches_remove_split(self, *args):
		self.tab_batches_picture_canvas.delete(ALL)
		items = map(int, self.tab_batches_split_listbox.curselection())
		for i in items:
			self.tab_batches_yield_listbox.delete(i)
			self.tab_batches_pixel_listbox.delete(i)
			self.tab_batches_device_listbox.delete(i)
			self.tab_batches_split_name_listbox.delete(i)
			self.tab_batches_split_listbox.delete(i)
			self.tab_batches_split_desc_listbox.delete(i)
			self.tab_batches_split_stack_listbox.delete(i)
			
	def tab_batches_split_stack_listbox_selection(self, *args):
		selc = self.tab_batches_split_stack_listbox.curselection()
		stack = self.tab_batches_split_stack_listbox.get(selc)
		self.tab_batches_set_picture(stack)		
		
		items = map(int, self.tab_batches_split_stack_listbox.curselection())
		self.tab_batches_split_listbox.selection_clear(first=0, last=END)
		self.tab_batches_split_name_listbox.selection_clear(first=0, last=END)
		self.tab_batches_device_listbox.selection_clear(first=0, last=END)
		self.tab_batches_pixel_listbox.selection_clear(first=0, last=END)
		self.tab_batches_yield_listbox.selection_clear(first=0, last=END)
		self.tab_batches_split_desc_listbox.selection_clear(first=0, last=END)
		for i in items:
			self.tab_batches_split_listbox.select_set(i)
			self.tab_batches_split_name_listbox.select_set(i)
			self.tab_batches_device_listbox.select_set(i)
			self.tab_batches_split_desc_listbox.select_set(i)
			self.tab_batches_pixel_listbox.select_set(i)
			self.tab_batches_yield_listbox.select_set(i)
		
	def tab_batches_split_listbox_selection(self, *args):
		selc = self.tab_batches_split_listbox.curselection()
		stack = self.tab_batches_split_stack_listbox.get(selc)
		self.tab_batches_set_picture(stack)
		
		items = map(int, self.tab_batches_split_listbox.curselection())
		self.tab_batches_split_name_listbox.selection_clear(first=0, last=END)
		self.tab_batches_device_listbox.selection_clear(first=0, last=END)
		self.tab_batches_pixel_listbox.selection_clear(first=0, last=END)
		self.tab_batches_yield_listbox.selection_clear(first=0, last=END)
		self.tab_batches_split_desc_listbox.selection_clear(first=0, last=END)
		self.tab_batches_split_stack_listbox.selection_clear(first=0, last=END)
		for i in items:
			self.tab_batches_split_name_listbox.select_set(i)
			self.tab_batches_device_listbox.select_set(i)
			self.tab_batches_pixel_listbox.select_set(i)
			self.tab_batches_yield_listbox.select_set(i)
			self.tab_batches_split_desc_listbox.select_set(i)
			self.tab_batches_split_stack_listbox.select_set(i)
			
	def tab_batches_split_name_listbox_selection(self, *args):
		selc = self.tab_batches_split_name_listbox.curselection()
		stack = self.tab_batches_split_stack_listbox.get(selc)
		self.tab_batches_set_picture(stack)
		
		items = map(int, self.tab_batches_split_name_listbox.curselection())
		self.tab_batches_split_listbox.selection_clear(first=0, last=END)
		self.tab_batches_device_listbox.selection_clear(first=0, last=END)
		self.tab_batches_pixel_listbox.selection_clear(first=0, last=END)
		self.tab_batches_yield_listbox.selection_clear(first=0, last=END)
		self.tab_batches_split_desc_listbox.selection_clear(first=0, last=END)
		self.tab_batches_split_stack_listbox.selection_clear(first=0, last=END)
		
		for i in items:
			self.tab_batches_split_listbox.select_set(i)
			self.tab_batches_device_listbox.select_set(i)
			self.tab_batches_pixel_listbox.select_set(i)
			self.tab_batches_yield_listbox.select_set(i)
			self.tab_batches_split_desc_listbox.select_set(i)
			self.tab_batches_split_stack_listbox.select_set(i)
	
	def tab_batches_device_listbox_selection(self, *args):
		selc = self.tab_batches_device_listbox.curselection()
		stack = self.tab_batches_split_stack_listbox.get(selc)
		self.tab_batches_set_picture(stack)
		
		items = map(int, self.tab_batches_device_listbox.curselection())
		self.tab_batches_split_name_listbox.selection_clear(first=0, last=END)
		self.tab_batches_split_listbox.selection_clear(first=0, last=END)
		self.tab_batches_pixel_listbox.selection_clear(first=0, last=END)
		self.tab_batches_yield_listbox.selection_clear(first=0, last=END)
		self.tab_batches_split_desc_listbox.selection_clear(first=0, last=END)
		self.tab_batches_split_stack_listbox.selection_clear(first=0, last=END)
		for i in items:
			self.tab_batches_split_name_listbox.select_set(i)
			self.tab_batches_split_listbox.select_set(i)
			self.tab_batches_pixel_listbox.select_set(i)
			self.tab_batches_yield_listbox.select_set(i)
			self.tab_batches_split_desc_listbox.select_set(i)
			self.tab_batches_split_stack_listbox.select_set(i)
	
	def tab_batches_pixel_listbox_selection(self, *args):
		selc = self.tab_batches_pixel_listbox.curselection()
		stack = self.tab_batches_split_stack_listbox.get(selc)
		self.tab_batches_set_picture(stack)
		
		items = map(int, self.tab_batches_pixel_listbox.curselection())
		self.tab_batches_split_name_listbox.selection_clear(first=0, last=END)
		self.tab_batches_split_listbox.selection_clear(first=0, last=END)
		self.tab_batches_device_listbox.selection_clear(first=0, last=END)
		self.tab_batches_yield_listbox.selection_clear(first=0, last=END)
		self.tab_batches_split_desc_listbox.selection_clear(first=0, last=END)
		self.tab_batches_split_stack_listbox.selection_clear(first=0, last=END)
		for i in items:
			self.tab_batches_split_name_listbox.select_set(i)
			self.tab_batches_split_listbox.select_set(i)
			self.tab_batches_device_listbox.select_set(i)
			self.tab_batches_split_desc_listbox.select_set(i)
			self.tab_batches_split_stack_listbox.select_set(i)
			self.tab_batches_yield_listbox.select_set(i)
			
	def tab_batches_yield_listbox_selection(self, *args):
		selc = self.tab_batches_yield_listbox.curselection()
		stack = self.tab_batches_split_stack_listbox.get(selc)
		self.tab_batches_set_picture(stack)
		
		items = map(int, self.tab_batches_yield_listbox.curselection())
		self.tab_batches_split_name_listbox.selection_clear(first=0, last=END)
		self.tab_batches_split_listbox.selection_clear(first=0, last=END)
		self.tab_batches_device_listbox.selection_clear(first=0, last=END)
		self.tab_batches_pixel_listbox.selection_clear(first=0, last=END)
		self.tab_batches_split_desc_listbox.selection_clear(first=0, last=END)
		self.tab_batches_split_stack_listbox.selection_clear(first=0, last=END)
		for i in items:
			self.tab_batches_split_name_listbox.select_set(i)
			self.tab_batches_split_listbox.select_set(i)
			self.tab_batches_device_listbox.select_set(i)
			self.tab_batches_split_desc_listbox.select_set(i)
			self.tab_batches_split_stack_listbox.select_set(i)
			self.tab_batches_pixel_listbox.select_set(i)
			
	def tab_batches_split_desc_listbox_selection(self, *args):
		selc = self.tab_batches_split_desc_listbox.curselection()
		stack = self.tab_batches_split_stack_listbox.get(selc)
		self.tab_batches_set_picture(stack)
		
		items = map(int, self.tab_batches_split_desc_listbox.curselection())
		self.tab_batches_split_name_listbox.selection_clear(first=0, last=END)
		self.tab_batches_split_listbox.selection_clear(first=0, last=END)
		self.tab_batches_device_listbox.selection_clear(first=0, last=END)
		self.tab_batches_pixel_listbox.selection_clear(first=0, last=END)
		self.tab_batches_yield_listbox.selection_clear(first=0, last=END)
		self.tab_batches_split_stack_listbox.selection_clear(first=0, last=END)
		for i in items:
			self.tab_batches_split_name_listbox.select_set(i)
			self.tab_batches_split_listbox.select_set(i)
			self.tab_batches_device_listbox.select_set(i)
			self.tab_batches_split_stack_listbox.select_set(i)
			self.tab_batches_pixel_listbox.select_set(i)
			self.tab_batches_yield_listbox.select_set(i)
												
	def tab_batches_list_vsb(self, *args):
		self.tab_batches_device_listbox.yview(*args)
		self.tab_batches_split_name_listbox.yview(*args)
		self.tab_batches_split_listbox.yview(*args)
		self.tab_batches_split_desc_listbox.yview(*args)
		self.tab_batches_split_stack_listbox.yview(*args)
		self.tab_batches_yield_listbox.yview(*args)
		self.tab_batches_pixel_listbox.yview(*args)
		
	def tab_batches_add_split_list(self, *args):
		split_input = self.tab_batches_split_spin.get()
		split_name_input = self.tab_batches_split_name_entry.get()
		device_input = self.tab_batches_device_spin.get()
		desc_input = self.tab_batches_split_desc_text.get(1.0,END)
		stack_input = self.tab_batches_stack_box.get()
		#### remove the carriage return from the end #####
		desc_input = desc_input[:-1]
		##### probably want to calculate the number of pixels here ######
		if split_input and split_name_input and device_input and desc_input and stack_input:
			self.tab_batches_split_listbox.insert(END, split_input)
			self.tab_batches_split_name_listbox.insert(END, split_name_input)
			self.tab_batches_device_listbox.insert(END, device_input)
			self.tab_batches_split_desc_listbox.insert(END, desc_input)
			self.tab_batches_split_stack_listbox.insert(END, stack_input)
			next_split = int(split_input)+1
			self.tab_batches_split_spin_var.set(next_split)
	def tab_batches_add_new_batch_num(self, *args):
		self.tab_batches_num_list = []
		self.tab_batches_num_box['values'] = self.tab_batches_num_list
		##### find the greatest batch number #####
		batch_num_max = self.conn.execute('SELECT max(batch_num) FROM device_batches')
		batch_num_max_result = batch_num_max.fetchone()[0]

		if str(batch_num_max_result) == 'None':
			batch_num = 0	
		else:	
			#### increment the batch number by 1
			batch_num = int(batch_num_max_result)+1
	
		
		##### update the batch number list 
		batch_nums = self.conn.execute('SELECT batch_num FROM device_batches')
		batch_nums_result = batch_nums.fetchall()
		
		self.tab_batches_num_list.append(batch_num)
		if not batch_nums_result:
			self.tab_batches_num_list = self.tab_batches_num_list
		
			self.tab_batches_num_box['values'] = self.tab_batches_num_list
		else:	
			for i in batch_nums_result:
				
				self.tab_batches_num_list.append(i[0])
			self.tab_batches_num_list = list(reversed(self.tab_batches_num_list))	
			self.tab_batches_num_box['values'] = self.tab_batches_num_list
		self.tab_batches_num_box.set(batch_num)
	def update_batches_info(self, *args):
		self.tab_batches_desc_text.delete(1.0,END)
		self.tab_batches_pixel_listbox.delete(0,END)
		self.tab_batches_yield_listbox.delete(0,END)
		self.tab_batches_device_listbox.delete(0,END)
		self.tab_batches_split_listbox.delete(0,END)
		self.tab_batches_split_desc_listbox.delete(0,END)
		self.tab_batches_split_name_listbox.delete(0,END)
		self.tab_batches_split_stack_listbox.delete(0,END)
		self.tab_batches_notes_text.delete(1.0,END)
		##### from the batch number selected update the parameters
		batch_num = self.tab_batches_num_box.get()
		#### check the batch num exists in database #######
		id_select = self.conn.execute('SELECT id FROM device_batches WHERE batch_num = ?', (batch_num,))
		id_select_result = id_select.fetchall()
		
		
		if not id_select_result:
			pass
		else:	
			batch_id_select = self.conn.execute('SELECT id FROM device_batches WHERE batch_num = ?', (batch_num,))
			batch_id_select_result = batch_id_select.fetchone()[0]	
			
			batch_id_select_result = str(batch_id_select_result)
			
			if batch_id_select_result:
				##### get the batch name ####
				batch_name_select = self.conn.execute('SELECT batch_name FROM device_batches WHERE id = ?', (batch_id_select_result,))
				batch_name_select_result = batch_name_select.fetchone()[0]
				if batch_name_select_result:
					self.tab_batches_name_var.set(batch_name_select_result)
				else:
					self.tab_batches_name_var.set('No batch name available.')
						
				batch_desc_select = self.conn.execute('SELECT batch_desc FROM device_batches WHERE id = ?', (batch_id_select_result,))
				batch_desc_select_result = batch_desc_select.fetchone()[0]
				if batch_desc_select_result:
					self.tab_batches_desc_text.insert(INSERT, batch_desc_select_result)
				else:
					self.tab_batches_desc_text.insert(INSERT, 'No batch description available.')
				
				batch_notes_select = self.conn.execute('SELECT batch_notes FROM device_batches WHERE id = ?', (batch_id_select_result,))
				batch_notes_select_result = batch_notes_select.fetchone()[0]
				if batch_notes_select_result:
					self.tab_batches_notes_text.insert(END, batch_notes_select_result)
				else:
					self.tab_batches_notes_text.insert(END, 'No batch notes available.')
				
				
				batch_user_select = self.conn.execute('SELECT owner FROM device_batches WHERE id = ?', (batch_id_select_result,))
				batch_user_select_result = batch_user_select.fetchone()[0]
				if batch_user_select_result:
					self.tab_batches_user_box.set(batch_user_select_result)
				else:
					pass
				
				print batch_id_select_result
				#Get the batch_id and go through the splits with this id
				splits_select = self.conn.execute('SELECT id FROM splits WHERE batch_id = ?', (batch_id_select_result,))
				splits_select_result = splits_select.fetchall()	
				print splits_select_result
				for index, i in enumerate(splits_select_result):
					i = i[0]
					split_exists = self.conn.execute('SELECT split FROM splits WHERE id = ?', (i,))
					split_exists_results = split_exists.fetchone()[0]	
					split_exists_results = str(split_exists_results)
					
					if split_exists_results == 'None':
						pass
					else:	
						self.tab_batches_split_listbox.insert(index, split_exists_results)
						
					split_name_exists = self.conn.execute('SELECT split_name FROM splits WHERE id = ?', (i,))
					split_name_exists_results = split_name_exists.fetchone()[0]	
					split_name_exists_results = str(split_name_exists_results)
					
					if split_name_exists_results == 'None':
						pass
					else:	
						self.tab_batches_split_name_listbox.insert(index, split_name_exists_results)	
						
					device_exists = self.conn.execute('SELECT num_devs  FROM splits WHERE id = ?', (i,))
					device_exists_results = device_exists.fetchone()[0]	
					device_exists_results = str(device_exists_results)
					
					if device_exists_results == 'None':
						pass
					else:	
						self.tab_batches_device_listbox.insert(index, device_exists_results)	
						
					pixel_exists = self.conn.execute('SELECT num_pix FROM splits WHERE id = ?', (i,))
					pixel_exists_results = pixel_exists.fetchone()[0]	
					pixel_exists_results = str(pixel_exists_results)
					
					if pixel_exists_results == 'None':
						pass
					else:	
						self.tab_batches_pixel_listbox.insert(index, pixel_exists_results)	
						
					yield_exists = self.conn.execute('SELECT yield FROM splits WHERE id = ?', (i,))
					yield_exists_results = yield_exists.fetchone()[0]	
					yield_exists_results = str(yield_exists_results)
					
					if yield_exists_results == 'None':
						pass
					else:	
						self.tab_batches_yield_listbox.insert(index, yield_exists_results)
						
					desc_exists = self.conn.execute('SELECT split_desc FROM splits WHERE id = ?', (i,))
					desc_exists_results = desc_exists.fetchone()[0]	
					desc_exists_results = str(desc_exists_results)
					
					if desc_exists_results == 'None':
						pass
					else:	
						self.tab_batches_split_desc_listbox.insert(index, desc_exists_results)
						
					split_stack_exists = self.conn.execute('SELECT split_stack FROM splits WHERE id = ?', (i,))
					split_stack_exists_results = split_stack_exists.fetchone()[0]	
					split_stack_exists_results = str(split_stack_exists_results)
					
					if split_stack_exists_results == 'None':
						pass
					else:	
						##### convert the split stack id to a name
						split_stack_name_exists = self.conn.execute('SELECT stack_name FROM device_stacks WHERE id = ?', (split_stack_exists_results,))
						split_stack_name_exists_results = split_stack_name_exists.fetchone()[0]
						
						if str(split_stack_name_exists_results) == 'None':
							pass
						else:	
							self.tab_batches_split_stack_listbox.insert(index, split_stack_name_exists_results)		
								
	def update_tab_batches_number_combo(self, *args):
		self.tab_batches_num_list = []
		self.tab_batches_num_box.set('')
		## get the name of the device stacks ###
		tab_batch_num_select = self.conn.execute('SELECT batch_num FROM device_batches')
		tab_batch_num_select_results = tab_batch_num_select.fetchall()
		if tab_batch_num_select_results:	
			for i in tab_batch_num_select_results:
				if str(i[0]):
					self.tab_batches_num_list.append(i[0])
		self.tab_batches_num_list = list(reversed(self.tab_batches_num_list))			
		self.tab_batches_num_box['values'] = self.tab_batches_num_list
			
	def update_batches_canvas_scroll(self, *args):
		self.tab_batches_canvas.config(scrollregion=self.tab_batches_canvas.bbox(ALL))
	def stacks_tk(self, *args):
		#A frame in tab to hold all the other widgets
		self.tab_stack_frame = Frame(self.tab_stacks, width=1300, height=200)
		self.tab_stack_frame.grid(row=0, column=0)
		
		self.tab_stack_name_label = Label(self.tab_stack_frame, text='Device Stack Name:')
		self.tab_stack_name_label.grid(row=0, column=0, sticky=E)
		
		self.tab_stack_name_box_var = StringVar()
		self.tab_stack_name_list = []
		self.tab_stack_name_box = Combobox(self.tab_stack_frame, textvariable=self.tab_stack_name_box_var, width=80)
		#### first box so no need for a command #####
		self.tab_stack_name_box.bind('<<ComboboxSelected>>', self.update_previous_device_stacks)
		self.tab_stack_name_box['values'] = self.tab_stack_name_list
		self.tab_stack_name_box.grid(row=0, column=1, sticky=W, columnspan=10)
		#### populate the list ###########
		self.update_tab_stack_name_combo()
		
		##### The layers type combo box #########
		self.tab_stack_type_label = Label(self.tab_stack_frame, text='Layer Type Filter:')
		self.tab_stack_type_label.grid(row=1, column=0, sticky=E)
		
		self.tab_stack_layers_type_list = []
		self.tab_stack_type_box_var = StringVar()
		self.tab_stack_type_box = Combobox(self.tab_stack_frame, textvariable=self.tab_stack_type_box_var, width=40)
		#### first box so no need for a command #####
		self.tab_stack_type_box.bind('<<ComboboxSelected>>', self.update_stacks_layer_combo_box)
		self.tab_stack_type_box['values'] = self.tab_layers_type_list
		self.tab_stack_type_box.grid(row=1, column=1, sticky=W, columnspan=10)
		self.tab_stack_layers_get_type_list()
		
		##### The layers combo box #########
		self.tab_stack_layer_label = Label(self.tab_stack_frame, text='Layer:')
		self.tab_stack_layer_label.grid(row=2, column=0, sticky=E)
		
		self.tab_stack_layer_box_var = StringVar()
		self.tab_stack_layer_list = []
		self.tab_stack_layer_box = Combobox(self.tab_stack_frame, textvariable=self.tab_stack_layer_box_var, width=80)
		#### first box so no need for a command #####
		self.tab_stack_layer_box.bind('<<ComboboxSelected>>')
		self.tab_stack_layer_box['values'] = self.tab_stack_layer_list
		self.tab_stack_layer_box.grid(row=2, column=1, sticky=W)
		#### populate the list ###########

		self.tab_stack_check_var_complete = IntVar()
		self.tab_stack_check_complete = Checkbutton(self.tab_stack_frame, text="Show Used", variable=self.tab_stack_check_var_complete,command=self.update_stacks_layer_combo_box)
		self.tab_stack_check_complete.grid(row=2, column=2, sticky=W)

		
		self.tab_stack_layer_add_but = Button(self.tab_stack_frame, text='Add Layer to Stack', command=self.tab_stack_add_layer)
		self.tab_stack_layer_add_but.grid(row=3, column=1, columnspan=10, sticky=W)
		
		##### The treatments type combo box #########
		self.tab_stack_treat_label = Label(self.tab_stack_frame, text='Treatment Type Filter:')
		self.tab_stack_treat_label.grid(row=4, column=0, sticky=E)
		
		self.tab_stack_treat_box_var = StringVar()
		self.tab_stack_treat_box_list = ['Plasma', 'Drying','Cleaning','Light']
		self.tab_stack_treat_box = Combobox(self.tab_stack_frame, textvariable=self.tab_stack_treat_box_var, width=40)
		#### first box so no need for a command #####
		self.tab_stack_treat_box.bind('<<ComboboxSelected>>', self.update_tab_stack_treat_combo)
		self.tab_stack_treat_box['values'] = self.tab_stack_treat_box_list
		self.tab_stack_treat_box.grid(row=4, column=1, sticky=W, columnspan=10)
		
		##### The treatments combo box #########
		self.tab_stack_treat_conds_label = Label(self.tab_stack_frame, text='Treatment Conditions:')
		self.tab_stack_treat_conds_label.grid(row=5, column=0, sticky=E)
		
		self.tab_stack_treat_conds_box_var = StringVar()
		self.tab_stack_treat_conds_list = []
		self.tab_stack_treat_conds_box = Combobox(self.tab_stack_frame, textvariable=self.tab_stack_treat_conds_box_var, width=80)
		#### first box so no need for a command #####
		self.tab_stack_treat_conds_box.bind('<<ComboboxSelected>>')
		self.tab_stack_treat_conds_box['values'] = self.tab_stack_treat_conds_list
		self.tab_stack_treat_conds_box.grid(row=5, column=1, sticky=W, columnspan=10)
		#### populate the list ###########
		#self.update_tab_stack_treat_combo()
		
		self.tab_stack_treat_add_but = Button(self.tab_stack_frame, text='Add Treatment to Stack', command=self.tab_stack_add_treat)
		self.tab_stack_treat_add_but.grid(row=6, column=1, columnspan=10, sticky=W)
		
		##### A frame for the listbox ########
		self.tab_stack_listbox_frame = Frame(self.tab_stack_frame)
		self.tab_stack_listbox_frame.grid(row=7, column=0, sticky=NW, columnspan=10)
		
		self.tab_stack_type_list_lab = Label(self.tab_stack_listbox_frame, text='Type')
		self.tab_stack_type_list_lab.grid(row=0, column=0, sticky=W)
		
		self.tab_stack_list_lab = Label(self.tab_stack_listbox_frame, text='Device Stack')
		self.tab_stack_list_lab.grid(row=0, column=1, sticky=W)
		
		self.tab_stack_listbox_vsb = Scrollbar(self.tab_stack_listbox_frame)
		self.tab_stack_listbox_vsb.grid(row=1, column=2, sticky=N+S)
		
		self.tab_stack_type_listbox = Listbox(self.tab_stack_listbox_frame, yscrollcommand=self.tab_stack_listbox_vsb.set, exportselection=False, width=10)
		self.tab_stack_type_listbox.grid(row=1, column=0, sticky=W)
		self.tab_stack_type_listbox.bind('<<ListboxSelect>>', self.tab_stack_type_listbox_selection)
		
		self.tab_stack_listbox = Listbox(self.tab_stack_listbox_frame, yscrollcommand=self.tab_stack_listbox_vsb.set, exportselection=False, width=100)
		self.tab_stack_listbox.grid(row=1, column=1, sticky=W)
		self.tab_stack_listbox.bind('<<ListboxSelect>>', self.tab_stack_listbox_selection)
		
		self.tab_stack_listbox_vsb.config(command=self.tab_stack_list_vsb)
		
		self.tab_stack_remove_but = Button(self.tab_stack_frame, text='Remove From Stack', command=self.tab_stack_remove)
		self.tab_stack_remove_but.grid(row=8, column=0, sticky=NW, columnspan=1)

		self.tab_stack_top_elec_lab = Label(self.tab_stack_frame, text="Top Electrode Pattern")
		self.tab_stack_top_elec_lab.grid(row=9, column=0, sticky=NW)
		
		#Make the list items be from the .dat file 
		self.tab_stack_top_elec_box_var = StringVar()
		#top_elecs_data = numpy.genfromtxt(self.top_elec_pat_file, skip_header=1, delimiter='\t', dtype=None, invalid_raise=False, encoding='latin1')
		#top_elecs = [i[0] for i in top_elecs_data]
		self.tab_stack_top_elec_list = []
		self.tab_stack_top_elec_box = Combobox(self.tab_stack_frame, textvariable=self.tab_stack_top_elec_box_var, width=20)
		#### first box so no need for a command #####
		self.tab_stack_top_elec_box.bind('<<ComboboxSelected>>')
		self.tab_stack_top_elec_box['values'] = self.tab_stack_top_elec_list
		self.tab_stack_top_elec_box.grid(row=9, column=1, sticky=W)
		self.tab_stack_update_top_elec_drop_down()
		
		self.tab_stack_bot_elec_lab = Label(self.tab_stack_frame, text="Bottom Electrode Pattern")
		self.tab_stack_bot_elec_lab.grid(row=10, column=0, sticky=NW)
		
		#Make the list items be from the .dat file 
		self.tab_stack_bot_elec_box_var = StringVar()
		#bot_elecs_data = numpy.genfromtxt(self.bot_elec_pat_file, skip_header=1, delimiter='\t', dtype=None, invalid_raise=False, encoding='latin1')
		#bot_elecs = [i[0] for i in bot_elecs_data]
		self.tab_stack_bot_elec_list = []
		self.tab_stack_bot_elec_box = Combobox(self.tab_stack_frame, textvariable=self.tab_stack_bot_elec_box_var, width=20)
		#### first box so no need for a command #####
		self.tab_stack_bot_elec_box.bind('<<ComboboxSelected>>')
		self.tab_stack_bot_elec_box['values'] = self.tab_stack_bot_elec_list
		self.tab_stack_bot_elec_box.grid(row=10, column=1, sticky=W)
		self.tab_stack_update_bot_elec_drop_down()
		
		self.tab_stack_commit_but = Button(self.tab_stack_frame, text='Commit Stack to Database', command=self.commit_stack)
		self.tab_stack_commit_but.grid(row=11, column=0, sticky=NW, columnspan=1)
		
		self.tab_stack_status_lab_var = StringVar()
		self.tab_stack_status_lab = Label(self.tab_stack_frame, textvar=self.tab_stack_status_lab_var)
		self.tab_stack_status_lab.grid(row=12, column=0, sticky=NW, columnspan=1)
		self.tab_stack_status_lab_var.set('Status:')
		
		self.tab_stack_update_but = Button(self.tab_stack_frame, text='Update Stack', command=self.tab_stack_update)
		self.tab_stack_update_but.grid(row=13, column=0, sticky=NW, columnspan=1)
		#############Picture frame#########################
		####################################################################
		self.tab_stack_picture_frame = LabelFrame(self.tab_stack_frame, text='Device Stack Picture')
		self.tab_stack_picture_frame.grid(row=7, column=10, sticky=NW, columnspan=1, rowspan=20)
		
		self.tab_stack_picture_canvas = Canvas(self.tab_stack_picture_frame, width=650, height=500)
		self.tab_stack_picture_canvas.grid(row=0, column=0)
		self.tab_stack_picture_canvas.config(scrollregion=(0,0,650,1000))
		
		
		#A scroll bar in the tab that controls the canvas position
		self.tab_stack_picture_scroll = Scrollbar(self.tab_stack_picture_frame, orient='vertical', command=self.tab_stack_picture_canvas.yview)
		self.tab_stack_picture_scroll.grid(row=0, column=1, sticky=N+S)
		
		self.tab_stack_picture_canvas.configure(yscrollcommand=self.tab_stack_picture_scroll.set,scrollregion=self.tab_stack_picture_canvas.bbox("all"))
		self.tab_stack_picture_canvas.yview_moveto(1)
	
	def tab_stack_update_top_elec_drop_down(self,*args):
		result = self.select_many_things_where('elec_name', 'electrode_patterns', 'elec_type', 'top')
		if result:
			self.tab_stack_top_elec_list = []
			for i in result:
				self.tab_stack_top_elec_list.append(i[0])
			self.tab_stack_top_elec_box['values'] = list(sorted(self.tab_stack_top_elec_list))
	def tab_stack_update_bot_elec_drop_down(self,*args):
		result = self.select_many_things_where('elec_name', 'electrode_patterns', 'elec_type', 'bottom')
		if result:
			self.tab_stack_bot_elec_list = []
			for i in result:
				self.tab_stack_bot_elec_list.append(i[0])
			self.tab_stack_bot_elec_box['values'] = list(sorted(self.tab_stack_bot_elec_list))
	def tab_stack_update(self, *args):
		result = tkMessageBox.askyesno("Update Device Stack?", 'Do you want to update "%s" device stack in the database?\nRecords will be deleted and replaced.' % (self.tab_stack_name_box.get()), icon='warning')

		if result == True:
			#Get the device stack id
			select = self.conn.execute('SELECT id FROM device_stacks WHERE stack_name = ?', (self.tab_stack_name_box.get(),))
			device_stack_id =select.fetchone()[0]
			if str(device_stack_id) == 'None':
				pass
			else:
				print 'devie stack id %s' % device_stack_id
			
				#Delete the device stack parts with this id
				select_ids = self.conn.execute('DELETE FROM device_stack_parts WHERE device_stack_id = ?', (device_stack_id,))
				
				#Now update the stack
				#For each row in the stack_listbox get the type and select the id and get the name and select the id
				#TABLE device_stacks (id INTEGER PRIMARY KEY, stack_name TEXT, bot_elec_pat INTEGER, top_elec_pat INTEGER)
				#TABLE device_stack_parts (id INTEGER PRIMARY KEY, device_stack_id INTEGER, stack_name TEXT, type_id INTEGER, part_id INTEGER)
				dsp_lst = []
				
				#build a dict with the parts to go in the device_stack_parts table
				#this has common device_stack_parts in different rows
				#get the top and bot electrode patterns as ids 
				top_elec_id = self.select_one_thing('id', 'electrode_patterns', 'elec_name', self.tab_stack_top_elec_box.get())
				bot_elec_id = self.select_one_thing('id', 'electrode_patterns', 'elec_name', self.tab_stack_bot_elec_box.get())
		
				stack_dict = {'dev_stack_name':self.tab_stack_name_box.get(),
				'top_elec_pat':top_elec_id,
				'bot_elec_pat':bot_elec_id,
				}
				for index, i in enumerate(self.tab_stack_type_listbox.get(0, END)):
					
					#Get the type_id and part_id from the names in the table
					if i == 'Layer':

						z = 0
						part_id = self.select_one_thing('id', 'layers', 'layer_name', self.tab_stack_listbox.get(index))
					else:
						z = 1
						part_id = self.select_one_thing('id', 'treatments', 'name', self.tab_stack_listbox.get(index))
					
					
					
					parts_dict = {'stack_name':self.tab_stack_name_box.get(),
					'type_id':z,
					'part_id':part_id,
					}
					
					dsp_lst.append(parts_dict)
				
				stack_inputs_inserted = stack_update_function(self, self.conn, dsp_lst, stack_dict,device_stack_id)
				self.tab_stack_status_lab_var.set(stack_inputs_inserted[1])
				self.update_tab_stack_name_combo()	
				self.update_tab_batches_split_stack_combo()
		else:
			pass
	def tab_stack_layers_get_type_list(self, *args):
		self.tab_stack_layers_type_list = []
		## get the names of the deposition methods ###
		type_select = self.conn.execute('SELECT layer_type FROM layer_types')
		type_select_results = type_select.fetchall()
		
		if type_select_results:
			for i in type_select_results:
				if i[0]:
					self.tab_stack_layers_type_list.append(i[0])
		self.tab_stack_type_box['values'] = list(sorted(self.tab_stack_layers_type_list))
		
	def commit_stack(self, *args):
		###### Check if the stack name exists already #######
		stack_name_exists_select = self.conn.execute('SELECT id FROM device_stacks WHERE stack_name = ?', (self.tab_stack_name_box.get(),))
		stack_name_exists_select_result = stack_name_exists_select.fetchall()
		
		
		if stack_name_exists_select_result:
			self.tab_stack_status_lab_var.set('Status: Device stack name already exists, update and try again.')
		else:
			#For each row in the stack_listbox get the type and select the id and get the name and select the id
			#TABLE device_stacks (id INTEGER PRIMARY KEY, stack_name TEXT, bot_elec_pat INTEGER, top_elec_pat INTEGER)
			#TABLE device_stack_parts (id INTEGER PRIMARY KEY, device_stack_id INTEGER, stack_name TEXT, type_id INTEGER, part_id INTEGER)
			dsp_lst = []
			
			#build a dict with the parts to go in the device_stack_parts table
			#this has common device_stack_parts in different rows
			#get the top and bot electrode patterns as ids 
			top_elec_id = self.select_one_thing('id', 'electrode_patterns', 'elec_name', self.tab_stack_top_elec_box.get())
			bot_elec_id = self.select_one_thing('id', 'electrode_patterns', 'elec_name', self.tab_stack_bot_elec_box.get())
	
			stack_dict = {'dev_stack_name':self.tab_stack_name_box.get(),
			'top_elec_pat':top_elec_id,
			'bot_elec_pat':bot_elec_id,
			}
			for index, i in enumerate(self.tab_stack_type_listbox.get(0, END)):
				
				#Get the type_id and part_id from the names in the table
				if i == 'Layer':

					z = 0
					part_id = self.select_one_thing('id', 'layers', 'layer_name', self.tab_stack_listbox.get(index))
				else:
					z = 1
					part_id = self.select_one_thing('id', 'treatments', 'name', self.tab_stack_listbox.get(index))
				
				
				
				parts_dict = {'stack_name':self.tab_stack_name_box.get(),
				'type_id':z,
				'part_id':part_id,
				}
				
				dsp_lst.append(parts_dict)
			
			stack_inputs_inserted = stack_commit_function(self, self.conn, dsp_lst, stack_dict)
			self.tab_stack_status_lab_var.set(stack_inputs_inserted[1])
			self.update_tab_stack_name_combo()	
			self.update_tab_batches_split_stack_combo()	
			
			
			
	def tab_stack_remove(self, *args):
		items = map(int, self.tab_stack_listbox.curselection())
		for i in items:
			self.tab_stack_listbox.delete(i)
			self.tab_stack_type_listbox.delete(i)
	def tab_stack_add_treat(self, *args):
		treat_input = self.tab_stack_treat_conds_box.get()
		type_input = self.tab_stack_treat_box.get()
		position = self.tab_stack_listbox.curselection()
		if position:
			position = int(position[0]) + 1
			if treat_input and type_input:
				self.tab_stack_listbox.insert(position, treat_input)	
				self.tab_stack_type_listbox.insert(position, type_input)
		else:
			if treat_input and type_input:
				self.tab_stack_listbox.insert(END, treat_input)	
				self.tab_stack_type_listbox.insert(END, type_input)
				
	def tab_stack_add_layer(self, *args):
		layer_input = self.tab_stack_layer_box.get()
		#find the position of the cursor and insert there or at end
		position = self.tab_stack_listbox.curselection()
		if position:
			position = int(position[0]) + 1
			if layer_input:
				self.tab_stack_listbox.insert(position, layer_input)
				self.tab_stack_type_listbox.insert(position, 'Layer')
		else:
			if layer_input:
				self.tab_stack_listbox.insert(END, layer_input)
				self.tab_stack_type_listbox.insert(END, 'Layer')	
	
	def tab_stack_type_listbox_selection(self, *args):
		items = map(int, self.tab_stack_type_listbox.curselection())
		self.tab_stack_listbox.selection_clear(first=0, last=END)
		for i in items:
			self.tab_stack_listbox.select_set(i)
	def tab_stack_listbox_selection(self, *args):
		items = map(int, self.tab_stack_listbox.curselection())
		self.tab_stack_type_listbox.selection_clear(first=0, last=END)
		for i in items:
			self.tab_stack_type_listbox.select_set(i)				
	def tab_stack_list_vsb(self, *args):
		self.tab_stack_listbox.yview(*args)
		self.tab_stack_type_listbox.yview(*args)
	def update_tab_stack_treat_combo(self, *args):	
		self.tab_stack_treat_conds_list = []
		self.tab_stack_treat_conds_box['values'] = self.tab_stack_treat_conds_list
		self.tab_stack_treat_conds_box.set('')
		## get the id of the material ###

		if self.tab_stack_type_box.get() == "Any":
			tab_stack_treat_select_results = self.select_many_things('name', 'treatments')

		else:	
			#Convert the name to an id...
			type_id_result = self.select_one_thing('id', 'treatment_methods', 'name', self.tab_stack_treat_box.get())
			print type_id_result
			tab_stack_treat_select_results = self.select_many_things_where('name', 'treatments', 'treatment_method_id', type_id_result)
				
		if tab_stack_treat_select_results:	
			for i in tab_stack_treat_select_results:
				if i[0]:
					self.tab_stack_treat_conds_list.append(i[0])
			self.tab_stack_treat_conds_box['values'] = list(reversed(self.tab_stack_treat_conds_list))
	
	def update_stacks_layer_combo_box(self, *args):
		self.tab_stack_layer_list = []
		self.tab_stack_layer_box['values'] = self.tab_stack_layer_list
		self.tab_stack_layer_box.set('')
		
		#Get the state of used/unused
		if self.tab_stack_check_var_complete.get() == True:
			state = 1
		else:
			state = 0
		## get the id of the material ###
		if self.tab_stack_type_box.get() == "Any":
			tab_stacks_layer_type_name_select_results = self.select_many_things_where('layer_name', 'layers', 'state', state)

		else:	
			#Convert the name to an id...
			type_id_result = self.select_one_thing('id', 'layer_types', 'layer_type', self.tab_stack_type_box.get())

			tab_stacks_layer_type_name_select_results = self.select_many_things_where_two('layer_name', 'layers', 'layer_type', 'state', type_id_result, state)
				
		if tab_stacks_layer_type_name_select_results:
			for i in tab_stacks_layer_type_name_select_results:
				if i[0]:
					self.tab_stack_layer_list.append(i[0])
		self.tab_stack_layer_box['values'] = list(reversed(self.tab_stack_layer_list))
		
	def update_tab_stack_name_combo(self, *args):
		self.tab_stack_name_list = []
		self.tab_stack_name_box['values'] = self.tab_stack_name_list
		self.tab_stack_name_box.set('')
		## get the name of the device stacks ###
		tab_stack_name_select = self.conn.execute('SELECT stack_name FROM device_stacks')
		tab_stack_name_select_results = tab_stack_name_select.fetchall()
		
		if tab_stack_name_select_results:
			for i in tab_stack_name_select_results:
				if i[0]:
					self.tab_stack_name_list.append(i[0])
		self.tab_stack_name_box['values'] = list(reversed(self.tab_stack_name_list))
	def update_previous_device_stacks(self, *args):	
		#### clear the listboxes ######
		self.tab_stack_listbox.delete(0,END)
		self.tab_stack_type_listbox.delete(0,END)
		####Clear the picture#####
		self.tab_stack_picture_canvas.delete(ALL)
		### check for the device stack name in table ####
		select = self.conn.execute('SELECT id FROM device_stacks WHERE stack_name = ?', (self.tab_stack_name_box.get(),))
		select_result =select.fetchone()[0]
		select_result = str(select_result)
		#### for the id get the values and add to the listboxes ######
		if select_result:
			#Get the top and bot elec patterns 
			top_exists = self.conn.execute('SELECT top_elec_pat FROM device_stacks WHERE id = ?', (select_result,))
			top_exists_result = top_exists.fetchone()[0]
			
			bot_exists = self.conn.execute('SELECT bot_elec_pat FROM device_stacks WHERE id = ?', (select_result,))
			bot_exists_result = bot_exists.fetchone()[0]
			
			#Use these indexes to get the names of the patterns and set these in the combos
			top_name = self.conn.execute('SELECT elec_name FROM electrode_patterns WHERE id = ?', (top_exists_result,))
			top_name_results = top_name.fetchone()[0]
			
			bot_name = self.conn.execute('SELECT elec_name FROM electrode_patterns WHERE id = ?', (bot_exists_result,))
			bot_name_results = bot_name.fetchone()[0]
			
			#update the combos with the elec patterns
			#Could loop through and find the index that matches the name to select this correctly
			self.tab_stack_bot_elec_box_var.set(str(bot_name_results))
			self.tab_stack_top_elec_box_var.set(str(top_name_results))
			
			q = 0
			lq = 0
			#Use the device_stacks id to find the parts rows that have that device_stack_id
			rows = self.conn.execute('SELECT id FROM device_stack_parts WHERE device_stack_id = ?', (select_result,))
			rows_result =rows.fetchall() 

			for i in rows_result:
				i = i[0]
				#use the part type to select a layer or treatment
				part_type = self.conn.execute('SELECT type_id FROM device_stack_parts WHERE id = ?', (i,))
				part_type_result = part_type.fetchone()[0]
				
				part_id = self.conn.execute('SELECT part_id FROM device_stack_parts WHERE id = ?', (i,))
				part_id_result = part_id.fetchone()[0]
				
				#if the type is layer use the layers table or if treatments use treatments table...
				if part_type_result == 0:
					#This is for layers (only layers in the picture?)
					#### get the layer name from the layer id ######
					layer_name = self.conn.execute('SELECT layer_name FROM layers WHERE id = ?', (part_id_result,))
					layer_name_results = layer_name.fetchone()[0]
					layer_name_results = str(layer_name_results)
					
					self.tab_stack_listbox.insert(q, layer_name_results)
					self.tab_stack_type_listbox.insert(q, 'Layer')
					
					layer_colour = self.conn.execute('SELECT layer_colour FROM layers WHERE id = ?', (part_id_result,))
					layer_colour_results = layer_colour.fetchone()[0]
					if layer_colour_results == None:
						layer_colour_result = "#ffffff"
					else:
						layer_colour_result = str(layer_colour_results)
					
					#print layer_colour_result
					###Add to the picture####
					if lq == 0:
						qy = 500
						qyy = 500-40
						qx = 80
						qxx = 520
					else:
						qy = qy-41
						qyy = qy-40
						qx = 100
						qxx = 500
					
					self.tab_stack_picture_canvas.create_rectangle(qx, qy, qxx, qyy, fill=layer_colour_result)
					self.tab_stack_picture_canvas.create_text(120, qy-30, text=str(layer_name_results),width=360,anchor=NW)
					lq = lq+1
					q = q+1
				elif part_type_result == 1:
					#### get the treatment_method_id and set the name in listbox
					tre_met_id = self.conn.execute('SELECT treatment_method_id FROM treatments WHERE id = ?', (part_id_result,))
					tre_met_id_result = tre_met_id.fetchone()[0]	
					#Use this to look up the treatment method name...
					tre_met_name = self.conn.execute('SELECT name FROM treatment_methods WHERE id = ?', (tre_met_id_result,))
					tre_met_name_result = tre_met_name.fetchone()[0]
							
					if tre_met_name_result == 'None':
						pass
					else:
						self.tab_stack_type_listbox.insert(q, tre_met_name_result)
					
					#Now get the treatment name and insert that
					tre_name = self.conn.execute('SELECT name FROM treatments WHERE id = ?', (part_id_result,))
					tre_name_result = tre_name.fetchone()[0]	
						
						
					##### set the list box with this name ####
					if tre_name_result == 'None':
						pass
					else: 
						self.tab_stack_listbox.insert(q, tre_name_result)
						if q == 0:
							qy = 500
							qyy = 500-40
						else:
							qy = qy-41
							qyy = qy-40
						
						self.tab_stack_picture_canvas.create_rectangle(100, qy, 500, qyy, fill="Red")
						self.tab_stack_picture_canvas.create_text(120, qy-30, text=str(tre_name_result),width=360,anchor=NW)
						q = q+1	
			self.tab_stack_picture_canvas.config(scrollregion=self.tab_stack_picture_canvas.bbox(ALL))		
	def treatments_tk(self, *args):
		##### A canvas in the frame ######
		self.tab_treat_canvas = Canvas(self.tab_treat, width=1300, height=600)
		self.tab_treat_canvas.grid(row=0, column=0)
		
		#A frame in canvas to hold all the other widgets
		self.tab_treat_frame = Frame(self.tab_treat_canvas, width=1300, height=600)
		self.tab_treat_frame.grid(row=1, column=0)
		
		#A scroll bar in the tab that controls the canvas position
		self.tab_treat_scroll = Scrollbar(self.tab_treat, orient='vertical', command=self.tab_treat_canvas.yview)
		
		self.tab_treat_canvas.configure(yscrollcommand=self.tab_treat_scroll.set)
		
		self.tab_treat_scroll.grid(row=0, column=1, sticky=N+S)
		#A window for the canvas
		self.tab_treat_canvas.create_window((4,4), window=self.tab_treat_frame, anchor="nw")
		
		self.tab_treat_frame.bind("<Configure>", self.update_treat_canvas_scroll)
		
		self.tab_treat_label_frame = Labelframe(self.tab_treat_frame, width=1000, height=600, text='Treatments')
		self.tab_treat_label_frame.grid(row=0, column=0, sticky=W)
		
		self.tab_treat_type_label = Label(self.tab_treat_label_frame, text='Treatment Type:')
		self.tab_treat_type_label.grid(row=0, column=0, sticky=W)
		
		self.tab_treat_type_name_box_var = StringVar()
		self.tab_treat_type_name_list = []
		self.tab_treat_type_name_box = Combobox(self.tab_treat_label_frame, textvariable=self.tab_treat_type_name_box_var, width=80)
		#### first box so no need for a command #####
		self.tab_treat_type_name_box.bind('<<ComboboxSelected>>', self.tab_treat_name_name_update_box)
		self.tab_treat_type_name_box['values'] = self.tab_treat_type_name_list
		self.tab_treat_type_name_box.grid(row=0, column=1, sticky=W, columnspan=10)
		self.tab_treat_type_name_box.state(['readonly'])
		self.tab_treat_type_name_update_box()
		
		self.tab_treat_name_label = Label(self.tab_treat_label_frame, text='Treatment Name:')
		self.tab_treat_name_label.grid(row=1, column=0, sticky=W)
		
		self.tab_treat_name_name_box_var = StringVar()
		self.tab_treat_name_name_list = []
		self.tab_treat_name_name_box = Combobox(self.tab_treat_label_frame, textvariable=self.tab_treat_name_name_box_var, width=80)
		#### first box so no need for a command #####
		self.tab_treat_name_name_box.bind('<<ComboboxSelected>>', self.update_treat_conds_main)
		self.tab_treat_name_name_box['values'] = self.tab_treat_name_name_list
		self.tab_treat_name_name_box.grid(row=1, column=1, sticky=W, columnspan=10)
		self.tab_treat_name_name_box.state(['readonly'])
		

		####Plasma#########
		############
		#Another frame in the first frame
		self.tab_treat_plasma_label_frame = Labelframe(self.tab_treat_frame, width=1000, height=600, text='Plasma Treatments')
		self.tab_treat_plasma_label_frame.grid(row=1, column=0)
		
		self.tab_treat_plasma_label = Label(self.tab_treat_plasma_label_frame, text='Plasma Treatment Name:')
		self.tab_treat_plasma_label.grid(row=0, column=0, sticky=E)
		
		self.tab_treat_plasma_name_box_var = StringVar()
		self.tab_treat_plasma_name_list = []
		self.tab_treat_plasma_name_box = Combobox(self.tab_treat_plasma_label_frame, textvariable=self.tab_treat_plasma_name_box_var, width=80)
		#### first box so no need for a command #####
		self.tab_treat_plasma_name_box.bind('<<ComboboxSelected>>', self.tab_treat_plasma_update_name_combo)
		self.tab_treat_plasma_name_box['values'] = self.tab_treat_plasma_name_list
		self.tab_treat_plasma_name_box.grid(row=0, column=1, sticky=W, columnspan=10)
		#### populate the list ###########
		
		
		
		##### the plasma cleaner unit #####
		self.tab_treat_plasma_cleaner_label = Label(self.tab_treat_plasma_label_frame, text='Plasma Cleaner:')
		self.tab_treat_plasma_cleaner_label.grid(row=1, column=0, sticky=E)
		
		self.tab_treat_plasma_cleaner_label_var = StringVar()
		self.tab_treat_plasma_cleaner_list = ['None','PV-Lab Diener', 'SPCR-Diener']
		self.tab_treat_plasma_cleaner_box = Combobox(self.tab_treat_plasma_label_frame, textvariable=self.tab_treat_plasma_cleaner_label_var, width=30)
		self.tab_treat_plasma_cleaner_box.bind('<<ComboboxSelected>>')
		self.tab_treat_plasma_cleaner_box['values'] = self.tab_treat_plasma_cleaner_list 
		self.tab_treat_plasma_cleaner_box.grid(row=1, column=1, sticky=W)
		self.tab_treat_plasma_cleaner_box.state(['readonly'])
		
		##### label for the gases and the flows #######
		self.tab_treat_plasma_gas_label = Label(self.tab_treat_plasma_label_frame, text='Gas Type')
		self.tab_treat_plasma_gas_label.grid(row=2, column=1)
		
		self.tab_treat_plasma_flow_label = Label(self.tab_treat_plasma_label_frame, text='Flow (nl/h)')
		self.tab_treat_plasma_flow_label.grid(row=2, column=2)
		
		##### Gas 1 type #####
		self.tab_treat_plasma_gas1_label = Label(self.tab_treat_plasma_label_frame, text='Gas 1:')
		self.tab_treat_plasma_gas1_label.grid(row=3, column=0, sticky=E)
		
		self.tab_treat_plasma_gas1_label_var = StringVar()
		self.tab_treat_plasma_gas_list = ['', 'Oxygen', 'Nitrogen', 'Air', 'Helium']
		self.tab_treat_plasma_gas1_box = Combobox(self.tab_treat_plasma_label_frame, textvariable=self.tab_treat_plasma_gas1_label_var, width=30)
		self.tab_treat_plasma_gas1_box.bind('<<ComboboxSelected>>')
		self.tab_treat_plasma_gas1_box['values'] = self.tab_treat_plasma_gas_list 
		self.tab_treat_plasma_gas1_box.grid(row=3, column=1, sticky=W)
		self.tab_treat_plasma_gas1_box.state(['readonly'])
		
		##### Gas 2 type #####
		self.tab_treat_plasma_gas2_label = Label(self.tab_treat_plasma_label_frame, text='Gas 2:')
		self.tab_treat_plasma_gas2_label.grid(row=4, column=0, sticky=E)
		
		self.tab_treat_plasma_gas2_label_var = StringVar()
		self.tab_treat_plasma_gas2_box = Combobox(self.tab_treat_plasma_label_frame, textvariable=self.tab_treat_plasma_gas2_label_var, width=30)
		self.tab_treat_plasma_gas2_box.bind('<<ComboboxSelected>>')
		self.tab_treat_plasma_gas2_box['values'] = self.tab_treat_plasma_gas_list 
		self.tab_treat_plasma_gas2_box.grid(row=4, column=1, sticky=W)
		self.tab_treat_plasma_gas2_box.state(['readonly'])
		
		##### Gas 1 flow #####
		self.tab_plasma_spin_flow1_var = StringVar()
		self.tab_plasma_spin_flow1_spin = Spinbox(self.tab_treat_plasma_label_frame, from_=0, to=99999999, format="%.2f", increment=0.01, textvariable=self.tab_plasma_spin_flow1_var, width=20)
		self.tab_plasma_spin_flow1_spin.grid(row=3, column=2, sticky=W)
		self.tab_plasma_spin_flow1_var.set(False)
		##### Gas 2 flow #####
		self.tab_plasma_spin_flow2_var = StringVar()
		self.tab_plasma_spin_flow2_spin = Spinbox(self.tab_treat_plasma_label_frame, from_=0, to=99999999, format="%.2f", increment=0.01, textvariable=self.tab_plasma_spin_flow2_var, width=20)
		self.tab_plasma_spin_flow2_spin.grid(row=4, column=2, sticky=W)
		self.tab_plasma_spin_flow2_var.set(False)
		
		##### Plasma vacuum #####
		self.tab_treat_plasma_vac_label = Label(self.tab_treat_plasma_label_frame, text='Vacuum (mbar):')
		self.tab_treat_plasma_vac_label.grid(row=5, column=0, sticky=E)
		
		self.tab_plasma_spin_vac_var = StringVar()
		self.tab_plasma_spin_vac_spin = Spinbox(self.tab_treat_plasma_label_frame, from_=0, to=99999999, format="%.2f", increment=0.01, textvariable=self.tab_plasma_spin_vac_var, width=20)
		self.tab_plasma_spin_vac_spin.grid(row=5, column=1, sticky=W)
		self.tab_plasma_spin_vac_var.set(False)
		
		##### Plasma power #####
		self.tab_treat_plasma_power_label = Label(self.tab_treat_plasma_label_frame, text='Plasma Power (Percentage):')
		self.tab_treat_plasma_power_label.grid(row=6, column=0, sticky=E)
		
		self.tab_plasma_spin_power_var = StringVar()
		self.tab_plasma_spin_power_spin = Spinbox(self.tab_treat_plasma_label_frame, from_=0, to=100, format="%.2f", increment=0.01, textvariable=self.tab_plasma_spin_power_var, width=20)
		self.tab_plasma_spin_power_spin.grid(row=6, column=1, sticky=W)
		self.tab_plasma_spin_power_var.set(False)
		
		##### Plasma time #####
		self.tab_treat_plasma_time_label = Label(self.tab_treat_plasma_label_frame, text='Plasma Time (min):')
		self.tab_treat_plasma_time_label.grid(row=7, column=0, sticky=E)
		
		self.tab_plasma_spin_time_var = StringVar()
		self.tab_plasma_spin_time_spin = Spinbox(self.tab_treat_plasma_label_frame, from_=0, to=99999, format="%.2f", increment=0.01, textvariable=self.tab_plasma_spin_time_var, width=20)
		self.tab_plasma_spin_time_spin.grid(row=7, column=1, sticky=W)
		self.tab_plasma_spin_time_var.set(False)
		
		#### commit plasma conds button #####
		self.tab_palsma_commit_but = Button(self.tab_treat_plasma_label_frame,command=self.commit_plasma_to_database, text='Commit Plasma Treatment to Database')
		self.tab_palsma_commit_but.grid(row=8, column=0, sticky=W)
	
		self.tab_plasma_status_label_var = StringVar()
		self.tab_plasma_status_label= Label(self.tab_treat_plasma_label_frame, textvariable=self.tab_plasma_status_label_var)
		self.tab_plasma_status_label.grid(row=8, column=1, sticky=W, columnspan=10)
		self.tab_plasma_status_label_var.set('Status:')
		
		#####
		###Update the plasma combo
		self.update_treat_plasma_combo_box()
		
		
		######
		#########
		################ Drying conditions ##########################
		self.tab_treat_dry_label_frame = Labelframe(self.tab_treat_frame, width=800, height=200, text='Drying Treatments')
		self.tab_treat_dry_label_frame.grid(row=2, column=0, sticky=W)
		
		self.tab_treat_dry_prop_frame = Frame(self.tab_treat_dry_label_frame)
		self.tab_treat_dry_prop_frame.grid(row=0, column=0, sticky=W)
		
		self.tab_treat_dry_label = Label(self.tab_treat_dry_prop_frame, text='Drying Treatment Name:')
		self.tab_treat_dry_label.grid(row=0, column=0, sticky=E)
		
		self.tab_treat_dry_name_box_var = StringVar()
		self.tab_treat_dry_name_list = []
		self.tab_treat_dry_name_box = Combobox(self.tab_treat_dry_prop_frame, textvariable=self.tab_treat_dry_name_box_var, width=80)
		#### first box so no need for a command #####
		self.tab_treat_dry_name_box.bind('<<ComboboxSelected>>', self.tab_treat_dry_update_name_combo)
		self.tab_treat_dry_name_box['values'] = self.tab_treat_dry_name_list
		self.tab_treat_dry_name_box.grid(row=0, column=1, sticky=W, columnspan=10)
		##
		#
	
		##### Drying atmosphere #####
		self.tab_treat_dry_met_label = Label(self.tab_treat_dry_prop_frame, text='Drying Method:')
		self.tab_treat_dry_met_label.grid(row=1, column=0, sticky=E)
		
		self.tab_treat_dry_met_box_label_var = StringVar()
		self.tab_treat_dry_met_box = Combobox(self.tab_treat_dry_prop_frame, textvariable=self.tab_treat_dry_met_box_label_var, width=30)
		self.tab_treat_dry_met_box.bind('<<ComboboxSelected>>')
		self.tab_treat_dry_met_box['values'] = self.tab_treat_dry_met_list 
		self.tab_treat_dry_met_box.grid(row=1, column=1, sticky=W)
		self.tab_treat_dry_met_box.state(['readonly'])
		
		##### Drying atmosphere #####
		self.tab_treat_dry_atm_label = Label(self.tab_treat_dry_prop_frame, text='Drying Atmosphere:')
		self.tab_treat_dry_atm_label.grid(row=2, column=0, sticky=E)
		
		self.tab_treat_dry_atm_box_label_var = StringVar()
		self.tab_treat_dry_atm_list = ['', 'Air', 'Nitrogen', 'Vacuum']
		self.tab_treat_dry_atm_box = Combobox(self.tab_treat_dry_prop_frame, textvariable=self.tab_treat_dry_atm_box_label_var, width=30)
		self.tab_treat_dry_atm_box.bind('<<ComboboxSelected>>')
		self.tab_treat_dry_atm_box['values'] = self.tab_treat_dry_atm_list 
		self.tab_treat_dry_atm_box.grid(row=2, column=1, sticky=W)
		self.tab_treat_dry_atm_box.state(['readonly'])
		
		self.tab_treat_dry_hum_label = Label(self.tab_treat_dry_prop_frame, text='Humidity (RH%):')
		self.tab_treat_dry_hum_label.grid(row=3, column=0, sticky=E)
		
		self.tab_treat_dry_hum_var = StringVar()
		self.tab_treat_dry_hum_spin = Spinbox(self.tab_treat_dry_prop_frame, from_=0, to=100, format="%.2f", increment=0.01, textvariable=self.tab_treat_dry_hum_var, width=5)
		self.tab_treat_dry_hum_spin.grid(row=3, column=1, sticky=W)
		self.tab_treat_dry_hum_var.set(False)
		
		####Smart coater oven settings:
		self.tab_treat_dry_sc_frame = LabelFrame(self.tab_treat_dry_label_frame,text='Smartcoater Drying:')
		self.tab_treat_dry_sc_frame.grid(row=2, column=0, sticky=W)
		
		self.tab_treat_dry_sc_speed_label = Label(self.tab_treat_dry_sc_frame, text='Web Speed (m/min):')
		self.tab_treat_dry_sc_speed_label.grid(row=0, column=0, sticky=E)
		
		self.tab_treat_dry_sc_speed_var = StringVar()
		self.tab_treat_dry_sc_speed_spin = Spinbox(self.tab_treat_dry_sc_frame, from_=0, to=100, format="%.2f", increment=0.01, textvariable=self.tab_treat_dry_sc_speed_var, width=5)
		self.tab_treat_dry_sc_speed_spin.grid(row=0, column=1, sticky=W)
		self.tab_treat_dry_sc_speed_var.set(False)

		self.tab_treat_dry_sc_flow_1_label = Label(self.tab_treat_dry_sc_frame, text='Oven 1 Flow (%):')
		self.tab_treat_dry_sc_flow_1_label.grid(row=1, column=0, sticky=E)
				
		self.tab_treat_dry_sc_flow_1_var = StringVar()
		self.tab_treat_dry_sc_flow_1_spin = Spinbox(self.tab_treat_dry_sc_frame, from_=0, to=100, format="%.2f", increment=0.01, textvariable=self.tab_treat_dry_sc_flow_1_var, width=5)
		self.tab_treat_dry_sc_flow_1_spin.grid(row=1, column=1, sticky=W)
		self.tab_treat_dry_sc_flow_1_var.set(False)

		self.tab_treat_dry_sc_flow_2_label = Label(self.tab_treat_dry_sc_frame, text='Oven 2 Flow (%):')
		self.tab_treat_dry_sc_flow_2_label.grid(row=1, column=2, sticky=E)
		
		self.tab_treat_dry_sc_flow_2_var = StringVar()
		self.tab_treat_dry_sc_flow_2_spin = Spinbox(self.tab_treat_dry_sc_frame, from_=0, to=100, format="%.2f", increment=0.01, textvariable=self.tab_treat_dry_sc_flow_2_var, width=5)
		self.tab_treat_dry_sc_flow_2_spin.grid(row=1, column=3, sticky=W)
		self.tab_treat_dry_sc_flow_2_var.set(False)
		
		self.tab_treat_dry_sc_temp_1_label = Label(self.tab_treat_dry_sc_frame, text='Oven 1 Temperature:')
		self.tab_treat_dry_sc_temp_1_label.grid(row=2, column=0, sticky=E)
				
		self.tab_treat_dry_sc_temp_1_var = StringVar()
		self.tab_treat_dry_sc_temp_1_spin = Spinbox(self.tab_treat_dry_sc_frame, from_=0, to=100, format="%.2f", increment=0.01, textvariable=self.tab_treat_dry_sc_temp_1_var, width=5)
		self.tab_treat_dry_sc_temp_1_spin.grid(row=2, column=1, sticky=W)
		self.tab_treat_dry_sc_temp_1_var.set(False)

		self.tab_treat_dry_sc_temp_2_label = Label(self.tab_treat_dry_sc_frame, text='Oven 2 Temperature:')
		self.tab_treat_dry_sc_temp_2_label.grid(row=2, column=2, sticky=E)
		
		self.tab_treat_dry_sc_temp_2_var = StringVar()
		self.tab_treat_dry_sc_temp_2_spin = Spinbox(self.tab_treat_dry_sc_frame, from_=0, to=100, format="%.2f", increment=0.01, textvariable=self.tab_treat_dry_sc_temp_2_var, width=5)
		self.tab_treat_dry_sc_temp_2_spin.grid(row=2, column=3, sticky=W)
		self.tab_treat_dry_sc_temp_2_var.set(False)
		
		####### Frame for the settings #########
		######################################
		self.tab_treat_dry_set_frame = Frame(self.tab_treat_dry_label_frame)
		self.tab_treat_dry_set_frame.grid(row=3, column=0, sticky=W)
		
		self.tab_treat_dry_set_initial_label = Label(self.tab_treat_dry_set_frame, text='Initial Temperature (degC):')
		self.tab_treat_dry_set_initial_label.grid(row=0, column=0, sticky=W)
		
		self.tab_treat_dry_set_final_label = Label(self.tab_treat_dry_set_frame, text='Final Temperature (degC):')
		self.tab_treat_dry_set_final_label.grid(row=0, column=1, sticky=W)
		
		self.tab_treat_dry_set_ramp_label = Label(self.tab_treat_dry_set_frame, text='Ramp Time (min):')
		self.tab_treat_dry_set_ramp_label.grid(row=0, column=2, sticky=W)
		
		self.tab_treat_dry_set_time_label = Label(self.tab_treat_dry_set_frame, text='Dry Time (min):')
		self.tab_treat_dry_set_time_label.grid(row=0, column=3, sticky=W)
		
		self.tab_treat_dry_set_initial_var = StringVar()
		self.tab_treat_dry_set_initial_spin = Spinbox(self.tab_treat_dry_set_frame, from_=-999999999, to=99999999, format="%.2f", increment=0.01, textvariable=self.tab_treat_dry_set_initial_var, width=20)
		self.tab_treat_dry_set_initial_spin.grid(row=1, column=0, sticky=W)
		self.tab_treat_dry_set_initial_var.set(False)
		
		self.tab_treat_dry_set_final_var = StringVar()
		self.tab_treat_dry_set_final_spin = Spinbox(self.tab_treat_dry_set_frame, from_=-999999999, to=99999999, format="%.2f", increment=0.01, textvariable=self.tab_treat_dry_set_final_var, width=20)
		self.tab_treat_dry_set_final_spin.grid(row=1, column=1, sticky=W)
		self.tab_treat_dry_set_final_var.set(False)
		
		self.tab_treat_dry_set_ramp_var = StringVar()
		self.tab_treat_dry_set_ramp_spin = Spinbox(self.tab_treat_dry_set_frame, from_=0, to=99999999, format="%.2f", increment=0.01, textvariable=self.tab_treat_dry_set_ramp_var, width=20)
		self.tab_treat_dry_set_ramp_spin.grid(row=1, column=2, sticky=W)
		self.tab_treat_dry_set_ramp_var.set(False)
		
		self.tab_treat_dry_set_time_var = StringVar()
		self.tab_treat_dry_set_time_spin = Spinbox(self.tab_treat_dry_set_frame, from_=0, to=99999999, format="%.2f", increment=0.01, textvariable=self.tab_treat_dry_set_time_var, width=20)
		self.tab_treat_dry_set_time_spin.grid(row=1, column=3, sticky=W)
		self.tab_treat_dry_set_time_var.set(False)
		
		############## buttons #######################
		self.tab_treat_dry_add_but = Button(self.tab_treat_dry_set_frame, text='Add to Drying Conditions', command=self.tab_treat_dry_add_to_listbox)
		self.tab_treat_dry_add_but.grid(row=2, column=0, sticky=W)
		
		self.tab_treat_dry_remove_but = Button(self.tab_treat_dry_set_frame, text='Remove from Drying Conditions', command=self.tab_treat_dry_remove_to_listbox)
		self.tab_treat_dry_remove_but.grid(row=2, column=1, sticky=W, columnspan=10)
		
		############### listboxes ###################
		#############################################
		self.tab_treat_dry_listbox_frame = Frame(self.tab_treat_dry_set_frame)
		self.tab_treat_dry_listbox_frame.grid(row=3, column=0, sticky=W, columnspan=10)
		
		self.tab_treat_dry_listbox_vsb = Scrollbar(self.tab_treat_dry_listbox_frame)
		self.tab_treat_dry_listbox_vsb.grid(row=0, column=4, sticky=N+S)
		
		self.tab_treat_dry_initial_listbox = Listbox(self.tab_treat_dry_listbox_frame, yscrollcommand=self.tab_treat_dry_listbox_vsb.set, exportselection=False)
		self.tab_treat_dry_initial_listbox.grid(row=0, column=0, sticky=W)
		self.tab_treat_dry_initial_listbox.bind('<<ListboxSelect>>', self.tab_treat_dry_listbox_selection_initial)
		
		self.tab_treat_dry_final_listbox = Listbox(self.tab_treat_dry_listbox_frame, yscrollcommand=self.tab_treat_dry_listbox_vsb.set, exportselection=False)
		self.tab_treat_dry_final_listbox.grid(row=0, column=1, sticky=W)
		self.tab_treat_dry_final_listbox.bind('<<ListboxSelect>>', self.tab_treat_dry_listbox_selection_final)
		
		self.tab_treat_dry_ramp_listbox = Listbox(self.tab_treat_dry_listbox_frame, yscrollcommand=self.tab_treat_dry_listbox_vsb.set, exportselection=False)
		self.tab_treat_dry_ramp_listbox.grid(row=0, column=2, sticky=W)
		self.tab_treat_dry_ramp_listbox.bind('<<ListboxSelect>>', self.tab_treat_dry_listbox_selection_ramp)
		
		self.tab_treat_dry_time_listbox = Listbox(self.tab_treat_dry_listbox_frame, yscrollcommand=self.tab_treat_dry_listbox_vsb.set, exportselection=False)
		self.tab_treat_dry_time_listbox.grid(row=0, column=3, sticky=W)
		self.tab_treat_dry_time_listbox.bind('<<ListboxSelect>>', self.tab_treat_dry_listbox_selection_time)
		
		self.tab_treat_dry_listbox_vsb.config(command=self.tab_treat_dry_multi_list_vsb)
		
		
		self.tab_treat_dry_commit_but = Button(self.tab_treat_dry_listbox_frame, command=self.tab_treat_dry_commit, text='Commit Drying Conditions to Database')
		self.tab_treat_dry_commit_but.grid(row=1, column=0, sticky=W, columnspan=10)
	
		self.tab_treat_dry_status_label_var = StringVar()
		self.tab_treat_dry_status_label = Label(self.tab_treat_dry_listbox_frame, textvariable=self.tab_treat_dry_status_label_var)
		self.tab_treat_dry_status_label.grid(row=2, column=0, sticky=W, columnspan=10)
		self.tab_treat_dry_status_label_var.set('Status:')
		
		
		######
		#Update the drying combo
		self.update_treat_dry_combo_box()
		#########
		
		#########
		
		#########
		self.tab_treat_clean_label_frame = Labelframe(self.tab_treat_frame, width=1000, height=600, text='Cleaning Treatments')
		self.tab_treat_clean_label_frame.grid(row=3, column=0,sticky=W)
		
		self.tab_treat_clean_label = Label(self.tab_treat_clean_label_frame, text='Cleaning Method Name:')
		self.tab_treat_clean_label.grid(row=0, column=0, sticky=E)
		
		###Combo for the methods
		self.tab_treat_clean_name_box_var = StringVar()	
		self.tab_treat_clean_name_list = []
		self.tab_treat_clean_name_box = Combobox(self.tab_treat_clean_label_frame, textvariable=self.tab_treat_clean_name_box_var, width=80)
		self.tab_treat_clean_name_box.bind('<<ComboboxSelected>>', self.tab_treat_clean_update_name_combo)
		self.tab_treat_clean_name_box['values'] = self.tab_treat_clean_name_list
		self.tab_treat_clean_name_box.grid(row=0, column=1, sticky=W, columnspan=10)
		
		#

		self.tab_treat_clean_note_label = Label(self.tab_treat_clean_label_frame, text='Cleaning Method Notes:')
		self.tab_treat_clean_note_label.grid(row=1, column=0, sticky=E)
				
		self.tab_treat_clean_notes_text = Text(self.tab_treat_clean_label_frame, width=100, height=10)
		self.tab_treat_clean_notes_text.grid(row=2, column=0, sticky=W, columnspan=25)
		
		##Notes of the method
		##Commit the method
		self.tab_treat_clean_commit_but = Button(self.tab_treat_clean_label_frame, command=self.tab_treat_clean_commit, text='Commit Cleaning Method to Database')
		self.tab_treat_clean_commit_but.grid(row=3, column=0, sticky=W, columnspan=2)
		
		self.tab_treat_clean_status_label_var = StringVar()
		self.tab_treat_clean_status_label = Label(self.tab_treat_clean_label_frame, textvariable=self.tab_treat_clean_status_label_var)
		self.tab_treat_clean_status_label.grid(row=3, column=2, sticky=W, columnspan=10)
		self.tab_treat_clean_status_label_var.set('Status:')
		
		###Update the name combo
		self.update_treat_clean_combo_box()
		###########################################
		###########################################
		###########################################
		#UV cure treatments
		self.tab_treat_uv_label_frame = Labelframe(self.tab_treat_frame, width=1000, height=600, text='Light, UV Treatments etc.')
		self.tab_treat_uv_label_frame.grid(row=4, column=0,sticky=W)
		
		self.tab_treat_uv_label = Label(self.tab_treat_uv_label_frame, text='Light Treatment Name:')
		self.tab_treat_uv_label.grid(row=0, column=0, sticky=E)
		
		self.tab_treat_uv_name_box_var = StringVar()
		self.tab_treat_uv_name_list = []
		self.tab_treat_uv_name_box = Combobox(self.tab_treat_uv_label_frame, textvariable=self.tab_treat_uv_name_box_var, width=80)
		self.tab_treat_uv_name_box.bind('<<ComboboxSelected>>')
		self.tab_treat_uv_name_box['values'] = self.tab_treat_uv_name_list
		self.tab_treat_uv_name_box.grid(row=0, column=1, sticky=W, columnspan=10)
		#### populate the list ###########
		#self.update_treat_uv_combo_box()

		self.tab_treat_uv_atm_label = Label(self.tab_treat_uv_label_frame, text='Light Treatment Atmosphere:')
		self.tab_treat_uv_atm_label.grid(row=1, column=0, sticky=E)
				
		self.tab_treat_uv_atm_box_label_var = StringVar()
		self.tab_treat_uv_atm_list = ['', 'Air', 'Nitrogen', 'Vacuum']
		self.tab_treat_uv_atm_box = Combobox(self.tab_treat_uv_label_frame, textvariable=self.tab_treat_uv_atm_box_label_var, width=30)
		self.tab_treat_uv_atm_box.bind('<<ComboboxSelected>>')
		self.tab_treat_uv_atm_box['values'] = self.tab_treat_uv_atm_list 
		self.tab_treat_uv_atm_box.grid(row=1, column=1, sticky=W)
		self.tab_treat_uv_atm_box.state(['readonly'])
		
		self.tab_treat_uv_source_label = Label(self.tab_treat_uv_label_frame, text='Light Source:')
		self.tab_treat_uv_source_label.grid(row=2, column=0, sticky=E)
		
		self.tab_treat_uv_source_box_label_var = StringVar()
		self.tab_treat_uv_source_list = ['Solar Simulator', 'Sulfur plasma', 'UV-lamp', 'UV-LED', 'BridgeLux LED', 'Glovebox UV lamp']
		self.tab_treat_uv_source_box = Combobox(self.tab_treat_uv_label_frame, textvariable=self.tab_treat_uv_source_box_label_var, width=30)
		self.tab_treat_uv_source_box.bind('<<ComboboxSelected>>')
		self.tab_treat_uv_source_box['values'] = self.tab_treat_uv_source_list 
		self.tab_treat_uv_source_box.grid(row=2, column=1, sticky=W)
		self.tab_treat_uv_source_box.state(['readonly'])
		
		self.tab_treat_uv_time_label = Label(self.tab_treat_uv_label_frame, text='Soak Time (min):')
		self.tab_treat_uv_time_label.grid(row=3, column=0, sticky=E)
		
		self.tab_treat_uv_time_var = StringVar()
		self.tab_treat_uv_time_spin = Spinbox(self.tab_treat_uv_label_frame, from_=0, to=99999999, format="%.2f", increment=0.01, textvariable=self.tab_treat_uv_time_var, width=20)
		self.tab_treat_uv_time_spin.grid(row=3, column=1, sticky=W)
		self.tab_treat_uv_time_var.set(False)
		
		self.tab_treat_uv_set_label = Label(self.tab_treat_uv_label_frame, text='Light Settings:')
		self.tab_treat_uv_set_label.grid(row=4, column=0, sticky=E)
		
		self.tab_treat_uv_set_var = StringVar()		
		self.tab_treat_uv_set_text = Entry(self.tab_treat_uv_label_frame, textvariable=self.tab_treat_uv_set_var)
		self.tab_treat_uv_set_text.grid(row=4, column=1, sticky=W, columnspan=4)
		
		##Commit the method
		self.tab_treat_uv_commit_but = Button(self.tab_treat_uv_label_frame, command=self.tab_treat_uv_commit, text='Commit Light Treatment to Database')
		self.tab_treat_uv_commit_but.grid(row=5, column=0, sticky=W, columnspan=1)
		
		self.tab_treat_uv_status_label_var = StringVar()
		self.tab_treat_uv_status_label = Label(self.tab_treat_uv_label_frame, textvariable=self.tab_treat_uv_status_label_var)
		self.tab_treat_uv_status_label.grid(row=5, column=1, sticky=W, columnspan=10)
		self.tab_treat_uv_status_label_var.set('Status:')
	
	def tab_treat_clean_update_name_combo(self, *args):
		name = self.tab_treat_clean_name_box.get()
		method = 'Cleaning'
		self.update_treat_conds(name, method)
	def tab_treat_dry_update_name_combo(self, *args):
		name = self.tab_treat_dry_name_box.get()
		method = 'Drying'
		self.update_treat_conds(name, method)
	def tab_treat_plasma_update_name_combo(self, *args):
		#Call the update treatments function using the combo box name as an input
		name = self.tab_treat_plasma_name_box.get()
		method = 'Plasma'
		self.update_treat_conds(name, method)
	def tab_treat_name_name_update_box(self, *args):
		#Clear the old values
		self.tab_treat_name_name_box_var.set('')
		self.tab_treat_name_name_box['values'] = []
		#Select all the treatment names for the treatment selected in the combo
		#the long way to do this is use the treatment type name from the combo to look up the id name then use that to get the treatment names
		id_select = self.conn.execute('SELECT id FROM treatment_methods WHERE name = ?', (self.tab_treat_type_name_box.get(),))
		id_select_result = id_select.fetchone()[0]
		
		if str(id_select_result) == 'None':
			print 'No treatment methods found.'
		else:
			select = self.conn.execute('SELECT name FROM treatments WHERE treatment_method_id = ?', (id_select_result,))
			select_result = select.fetchall()

			if select_result:
				self.tab_treat_name_name_list = []
				for i in select_result:
					self.tab_treat_name_name_list.append(i[0])
				self.tab_treat_name_name_box['values'] = self.tab_treat_name_name_list
			
		
	def tab_treat_type_name_update_box(self, *args):
		#Get the treatment names from the table and add to the combo
		select = self.conn.execute('SELECT name FROM treatment_methods')
		select_result = select.fetchall()
		
		if select_result:
			self.tab_treat_type_name_list = []
			for i in select_result:
				self.tab_treat_type_name_list.append(i[0])
			self.tab_treat_type_name_box['values'] = self.tab_treat_type_name_list
		else:
			print 'No treatment names found.'
	
	def update_treat_conds_main(self, *args):
		name = 'None'
		method = 'None'
		self.update_treat_conds(name, method)		
	def update_treat_conds(self, name, method):
		if name == 'None':
			name = self.tab_treat_name_name_box.get()
		if method == 'None':
			method = self.tab_treat_type_name_box.get()
		#clear the entry boxes
		self.tab_treat_plasma_name_box_var.set('')
		self.tab_treat_dry_name_box_var.set('')
		self.tab_treat_clean_name_box_var.set('')
		self.tab_treat_uv_name_box_var.set('')
		
		self.tab_treat_clean_notes_text.delete(1.0,END)
		
		self.tab_treat_dry_initial_listbox.delete(0, END)
		self.tab_treat_dry_final_listbox.delete(0, END)
		self.tab_treat_dry_ramp_listbox.delete(0, END)
		self.tab_treat_dry_time_listbox.delete(0, END)
				
		id_select = self.conn.execute('SELECT id FROM treatments WHERE name = ?', (name,))
		id_select_result = id_select.fetchone()[0]
		
		#This is used pointlessly later on
		method_select = self.conn.execute('SELECT id FROM treatment_methods WHERE name = ?', (method,))
		method_select_result = method_select.fetchone()[0]
		
		if str(id_select_result) == 'None':
			print 'No treatment conditions available'

		else:
			#Get the treatment_conds_id that matches the name
			cond_id_select = self.conn.execute('SELECT treatment_conds_id FROM treatments WHERE id = ?', (id_select_result,))
			cond_id_select_result = cond_id_select.fetchone()[0] 
			
			#Now get each ids that matches the treatment_conds_id
			all_id_select = self.conn.execute('SELECT id FROM treatment_conds WHERE treatment_conds_id = ?', (cond_id_select_result,))
			all_id_select_result = all_id_select.fetchall()
			
			#Go through these ids and enter in the table entries...
			for index, i in enumerate(all_id_select_result):
				i = i[0]
				#Which name box to update depends on which treatment it is
				#Could do this a lond way 
				#This is pointless, could just check the box...
				met_name_select = self.conn.execute('SELECT name FROM treatment_methods WHERE id = ?', (method_select_result,))
				met_name_select_result = met_name_select.fetchone()[0]
				
				name_select = self.conn.execute('SELECT name FROM treatment_conds WHERE id = ?', (i,))
				name_select_result = name_select.fetchone()[0]
				
				if met_name_select_result == 'Plasma':
					self.tab_treat_plasma_name_box_var.set(name_select_result)
				elif met_name_select_result == 'Drying': 
					self.tab_treat_dry_name_box_var.set(name_select_result)
				elif met_name_select_result == 'Cleaning':
					self.tab_treat_clean_name_box_var.set(name_select_result)
				elif met_name_select_result == 'Light':
					self.tab_treat_uv_name_box_var.set(name_select_result)
				#Start with the drying conds
				#### update the dry method ####
				
				dry_met_select = self.conn.execute('SELECT dry_met FROM treatment_conds WHERE id = ?', (i,))
				dry_met_select_result = dry_met_select.fetchone()[0]
				
				if dry_met_select_result:
					self.tab_treat_dry_met_box.current(dry_met_select_result)
				else:
					self.tab_treat_dry_met_box.current(False)
			
				#### update the dry atm ####
				dry_atm_select = self.conn.execute('SELECT dry_atm FROM treatment_conds WHERE id = ?', (i,))
				dry_atm_select_result = dry_atm_select.fetchone()[0]
				
				if dry_atm_select_result:
					self.tab_treat_dry_atm_box.current(dry_atm_select_result)
				else:
					self.tab_treat_dry_atm_box.current(False)	

				#### update the dry humidity ####
				dry_hum_select = self.conn.execute('SELECT humidity FROM treatment_conds WHERE id = ?', (i,))
				dry_hum_select_result = dry_hum_select.fetchone()[0]
				
				if dry_hum_select_result:
					self.tab_treat_dry_hum_var.set(dry_hum_select_result)
				else:
					self.tab_treat_dry_hum_var.set(False)	
				
				#### update the sc web speed ####
				dry_sc_web_select = self.conn.execute('SELECT sc_web_speed FROM treatment_conds WHERE id = ?', (i,))
				dry_sc_web_select_result = dry_sc_web_select.fetchone()[0]
				
				if dry_sc_web_select_result:
					self.tab_treat_dry_sc_speed_var.set(dry_sc_web_select_result)
				else:
					self.tab_treat_dry_sc_speed_var.set(False)
			
				#### update the sc oven 1 temp ####
				dry_sc_temp_1_select = self.conn.execute('SELECT sc_temp_1 FROM treatment_conds WHERE id = ?', (i,))
				dry_sc_temp_1_select_result = dry_sc_temp_1_select.fetchone()[0]
				
				if dry_sc_temp_1_select_result:
					self.tab_treat_dry_sc_temp_1_var.set(dry_sc_temp_1_select_result)
				else:
					self.tab_treat_dry_sc_temp_1_var.set(False)

				dry_sc_temp_2_select = self.conn.execute('SELECT sc_temp_2 FROM treatment_conds WHERE id = ?', (i,))
				dry_sc_temp_2_select_result = dry_sc_temp_2_select.fetchone()[0]
				
				if dry_sc_temp_2_select_result:
					self.tab_treat_dry_sc_temp_2_var.set(dry_sc_temp_2_select_result)
				else:
					self.tab_treat_dry_sc_temp_2_var.set(False)
		
				#### update the sc oven flows ####
				dry_sc_flow_1_select = self.conn.execute('SELECT sc_flow_1 FROM treatment_conds WHERE id = ?', (i,))
				dry_sc_flow_1_select_result = dry_sc_flow_1_select.fetchone()[0]
				
				if dry_sc_flow_1_select_result:
					self.tab_treat_dry_sc_flow_1_var.set(dry_sc_flow_1_select_result)
				else:
					self.tab_treat_dry_sc_flow_1_var.set(False)

				dry_sc_flow_2_select = self.conn.execute('SELECT sc_flow_2 FROM treatment_conds WHERE id = ?', (i,))
				dry_sc_flow_2_select_result = dry_sc_flow_2_select.fetchone()[0]
				
				if dry_sc_flow_2_select_result:
					self.tab_treat_dry_sc_flow_2_var.set(dry_sc_flow_2_select_result)
				else:
					self.tab_treat_dry_sc_flow_2_var.set(False)
				
				###These add to the list box so use the index to put in the correct row 
				dry_initial_exists = self.conn.execute('SELECT dry_temp_initial FROM treatment_conds WHERE id = ?', (i,))
				dry_initial_exists_results = dry_initial_exists.fetchone()[0]
				dry_initial_exists_results = str(dry_initial_exists_results)
				
				if dry_initial_exists_results == 'None':
					pass
				else:	
					self.tab_treat_dry_initial_listbox.insert(index, dry_initial_exists_results)
					
				dry_final_exists = self.conn.execute('SELECT dry_temp_final FROM treatment_conds WHERE id = ?', (i,))
				dry_final_exists_results = dry_final_exists.fetchone()[0]
				dry_final_exists_results = str(dry_final_exists_results)
				
				if dry_final_exists_results == 'None':
					pass
				else:	
					self.tab_treat_dry_final_listbox.insert(index, dry_final_exists_results)
				
				dry_ramp_exists = self.conn.execute('SELECT ramp_time FROM treatment_conds WHERE id = ?', (i,))
				dry_ramp_exists_results = dry_ramp_exists.fetchone()[0]
				dry_ramp_exists_results = str(dry_ramp_exists_results)
				
				if dry_ramp_exists_results == 'None':
					pass
				else:	
					self.tab_treat_dry_ramp_listbox.insert(index, dry_ramp_exists_results)
				
				dry_time_exists = self.conn.execute('SELECT dry_time FROM treatment_conds WHERE id = ?', (i,))
				dry_time_exists_results = dry_time_exists.fetchone()[0]
				dry_time_exists_results = str(dry_time_exists_results)
				
				if dry_time_exists_results == 'None':
					pass
				else:	
					self.tab_treat_dry_time_listbox.insert(index, dry_time_exists_results)
					
			
				#################
				################
				#### Now for the cleaning and UV #################
				##################
				#####################
				##Check if there is an entry in the table and update everything
			
		
				uv_atm_select = self.conn.execute('SELECT light_atm FROM treatment_conds WHERE id = ?', (i,))
				uv_atm_select_result = uv_atm_select.fetchone()[0]
				
				if uv_atm_select_result:
					self.tab_treat_uv_atm_box.set(uv_atm_select_result)
				else:
					self.tab_treat_uv_atm_box.set('')
					
				uv_source_select = self.conn.execute('SELECT light_source FROM treatment_conds WHERE id = ?', (i,))
				uv_source_select_result = uv_source_select.fetchone()[0]
				
				if uv_source_select_result:
					self.tab_treat_uv_source_box.set(uv_source_select_result)
				else:
					self.tab_treat_uv_source_box.set('')
					
				uv_time_select = self.conn.execute('SELECT light_time FROM treatment_conds WHERE id = ?', (i,))
				uv_time_select_result = uv_time_select.fetchone()[0]
				
				if uv_time_select_result:
					self.tab_treat_uv_time_var.set(uv_time_select_result)
				else:
					self.tab_treat_uv_time_var.set('')
				
				uv_set_select = self.conn.execute('SELECT light_intensity FROM treatment_conds WHERE id = ?', (i,))
				uv_set_select_result = uv_set_select.fetchone()[0]
				
				if uv_set_select_result:
					self.tab_treat_uv_set_var.set(uv_set_select_result)
				else:
					self.tab_treat_uv_set_var.set('')		
		
				clean_notes_select = self.conn.execute('SELECT clean_notes FROM treatment_conds WHERE id = ?', (i,))
				clean_notes_select_result = clean_notes_select.fetchone()[0]
				
				if clean_notes_select_result:
					self.tab_treat_clean_notes_text.insert(END, str(clean_notes_select_result))
				else:
					self.tab_treat_clean_notes_text.insert(END, 'No notes available.')
				
				#### update the plasma cleaner ####
				tab_plasma_cleaner_select = self.conn.execute('SELECT plasma_cleaner FROM treatment_conds WHERE id = ?', (i,))
				tab_plasma_cleaner_select_result = tab_plasma_cleaner_select.fetchone()[0]
				
				if tab_plasma_cleaner_select_result:
					self.tab_treat_plasma_cleaner_box.current(tab_plasma_cleaner_select_result)
				else:
					self.tab_treat_plasma_cleaner_box.set('')
					
				##### update the gas 1#####
				tab_plasma_gas1_select = self.conn.execute('SELECT gas_1 FROM treatment_conds WHERE id = ?', (i,))
				tab_plasma_gas1_select_result = tab_plasma_gas1_select.fetchone()[0]
				
				if tab_plasma_gas1_select_result:
					self.tab_treat_plasma_gas1_box.current(tab_plasma_gas1_select_result)
				else:
					self.tab_treat_plasma_gas1_box.current(False)	
					
				##### update the gas 2 #####
				tab_plasma_gas2_select = self.conn.execute('SELECT gas_2 FROM treatment_conds WHERE id = ?', (i,))
				tab_plasma_gas2_select_result = tab_plasma_gas2_select.fetchone()[0]
				
				if tab_plasma_gas2_select_result:
					self.tab_treat_plasma_gas2_box.current(tab_plasma_gas2_select_result)
				else:
					self.tab_treat_plasma_gas2_box.current(False)	
				
				#### update the gasflow 1 #####	
				tab_plasma_flow1_select = self.conn.execute('SELECT gas_flow_1 FROM treatment_conds WHERE id = ?', (i,))
				tab_plasma_flow1_select_result = tab_plasma_flow1_select.fetchone()[0]
				
				if tab_plasma_flow1_select_result:
					self.tab_plasma_spin_flow1_var.set(tab_plasma_flow1_select_result)
				else:
					self.tab_plasma_spin_flow1_var.set(False)
					
				#### update the gasflow 2 #####	
				tab_plasma_flow2_select = self.conn.execute('SELECT gas_flow_2 FROM treatment_conds WHERE id = ?', (i,))
				tab_plasma_flow2_select_result = tab_plasma_flow2_select.fetchone()[0]
				
				if tab_plasma_flow2_select_result:
					self.tab_plasma_spin_flow2_var.set(tab_plasma_flow2_select_result)
				else:
					self.tab_plasma_spin_flow2_var.set(False)		
					
				#### update the plasma pwer #####	
				tab_plasma_power_select = self.conn.execute('SELECT power_plasma FROM treatment_conds WHERE id = ?', (i,))
				tab_plasma_power_select_result = tab_plasma_power_select.fetchone()[0]
				
				if tab_plasma_power_select_result:
					self.tab_plasma_spin_power_var.set(tab_plasma_power_select_result)
				else:
					self.tab_plasma_spin_power_var.set(False)		
					
				#### update the plasma time #####	
				tab_plasma_time_select = self.conn.execute('SELECT time_plasma FROM treatment_conds WHERE id = ?', (i,))
				tab_plasma_time_select_result = tab_plasma_time_select.fetchone()[0]
				
				if tab_plasma_flow1_select_result:
					self.tab_plasma_spin_time_var.set(tab_plasma_time_select_result)
				else:
					self.tab_plasma_spin_time_var.set(False)
				
				#### update the plasma time #####	
				tab_plasma_vac_select = self.conn.execute('SELECT vac_plasma FROM treatment_conds WHERE id = ?', (i,))
				tab_plasma_vac_select_result = tab_plasma_vac_select.fetchone()[0]
				
				if tab_plasma_vac_select_result:
					self.tab_plasma_spin_vac_var.set(tab_plasma_vac_select_result)
				else:
					self.tab_plasma_spin_vac_var.set(False)	
	def tab_treat_clean_commit(self,*args):
		#Need to check if the name exists
		#Get the treatment_method_id
		#Get a new treatments id and add in the entry there too, do this first
		
		#Check the name
		clean_cond_name_exists_select = self.conn.execute('SELECT id FROM treatment_conds WHERE name = ?', (self.tab_treat_clean_name_box.get(),))
		clean_cond_name_exists_select_result = clean_cond_name_exists_select.fetchall()
		
		if clean_cond_name_exists_select_result:
			self.tab_treat_clean_status_label_var.set('Treatment Name Exists')
		else:
			#Add a new treatments id
			clean_notes = self.tab_treat_clean_notes_text.get(1.0,END)
			clean_notes = clean_notes[:-1]
			
			#Get the treatment_method as an id
			#Annoying this has to be dug around for
			conds_lst = []
			x = 'Cleaning'
			id_select = self.conn.execute('SELECT id FROM treatment_methods WHERE name = ?', (x,))
			id_select_result = id_select.fetchone()[0]
			clean_conds_dict = { 
						'name':self.tab_treat_clean_name_box.get(),
						'clean_notes':clean_notes,
						'treatment_method_id':id_select_result,					
						}
			conds_lst.append(clean_conds_dict)
			function_name = 'treatment_conds'
			other_col = 'treatment_conds_id'
			other_table = 'treatments'
			method_col = 'treatment_method_id'
			conds_col = 'treatment_conds_id'  
			name_col = 'name'
			name = '%s' % self.tab_treat_clean_name_box.get()		
			inputs_inserted = self.dep_conds_mod(self, conds_lst, id_select_result, function_name, self.conn, other_col, other_table, method_col, conds_col, name_col, name)
			self.tab_treat_clean_status_label_var.set(inputs_inserted[1])
			
	def tab_treat_dry_commit(self, *args):
		#Check the name
		name_exists_select = self.conn.execute('SELECT id FROM treatment_conds WHERE name = ?', (self.tab_treat_dry_name_box.get(),))
		name_exists_select_result = name_exists_select.fetchall()
		
		if name_exists_select_result:
			self.tab_treat_dry_status_label_var.set('Status: Drying name already exists, update and try again.')
		else:
			conds_lst = []
			x = 'Drying'
			id_select = self.conn.execute('SELECT id FROM treatment_methods WHERE name = ?', (x,))
			dep_met_id_select_result = id_select.fetchone()[0]

			conds_dict = {}
			test = self.tab_treat_dry_initial_listbox.get(0, END)
			if not test:
				conds_dict = { 
						'name':self.tab_treat_dry_name_box.get(),
						'treatment_method_id':dep_met_id_select_result,
						'humidity':self.tab_treat_dry_hum_var.get(),					
						}
				#Change this to a database table and lookup at some point	
				#['', 'Hot Plate', 'Natural', 'Lab Oven', 'Vacuum Oven','Smartcoater Ovens','Bench Top Coater Ovens','FOM Ovens']			
				if self.tab_treat_dry_met_box.get() == 'Hot Plate':
					conds_dict['dry_met'] = '1'
				elif self.tab_treat_dry_met_box.get() == 'Natural':
					conds_dict['dry_met'] = '2'
				elif self.tab_treat_dry_met_box.get() == 'Lab Oven':
					conds_dict['dry_met'] = '3'
				elif self.tab_treat_dry_met_box.get() == 'Vacuum Oven':
					conds_dict['dry_met'] = '4'	
				elif self.tab_treat_dry_met_box.get() == 'Smartcoater Ovens':
					conds_dict['dry_met'] = '5'	
				elif self.tab_treat_dry_met_box.get() == 'Bench Top Coater Ovens':
					conds_dict['dry_met'] = '6'	
				elif self.tab_treat_dry_met_box.get() == 'FOM Ovens':
					conds_dict['dry_met'] = '7'	
				
				#Get the smartcoater settings
				if self.tab_treat_dry_met_box.get() == 'Smartcoater Ovens':
					conds_dict['sc_web_speed'] = self.tab_treat_dry_sc_speed_var.get()
					conds_dict['sc_flow_1'] = self.tab_treat_dry_sc_flow_1_var.get()
					conds_dict['sc_flow_2'] = self.tab_treat_dry_sc_flow_2_var.get()
					conds_dict['sc_temp_1'] = self.tab_treat_dry_sc_temp_1_var.get()
					conds_dict['sc_temp_2'] = self.tab_treat_dry_sc_temp_2_var.get()
				
				#Change this to a database table and lookup at some point	
				if self.tab_treat_dry_atm_box.get() == 'Air':
					conds_dict['dry_atm'] = '1'	
				elif self.tab_treat_dry_atm_box.get() == 'Nitrogen':
					conds_dict['dry_atm'] = '2'	
				elif self.tab_treat_dry_atm_box.get() == 'Vacuum':
					conds_dict['dry_atm'] = '3'
					
				conds_lst.append(conds_dict)
				function_name = 'treatment_conds'
				other_col = 'treatment_conds_id'
				other_table = 'treatments'
				method_col = 'treatment_method_id'
				conds_col = 'treatment_conds_id'  
				name_col = 'name'
				name = '%s' % self.tab_treat_dry_name_box.get()		
				inputs_inserted = self.dep_conds_mod(self, conds_lst, dep_met_id_select_result, function_name, self.conn, other_col, other_table, method_col, conds_col, name_col, name)
				
				self.tab_treat_dry_status_label_var.set(inputs_inserted[1])
			else:
					
				
				#If there are no steps in the temp profile, ignore them, otherwise get them
				for index, i in enumerate(self.tab_treat_dry_initial_listbox.get(0, END)):
					conds_dict = {}
					conds_dict['name'] = self.tab_treat_dry_name_box.get()
					conds_dict['treatment_method_id'] = dep_met_id_select_result
					conds_dict['humidity'] = self.tab_treat_dry_hum_var.get()
					conds_dict['dry_temp_initial'] = str(i)
					conds_dict['dry_temp_final'] = str(self.tab_treat_dry_final_listbox.get(index))
					conds_dict['ramp_time'] = str(self.tab_treat_dry_ramp_listbox.get(index))
					conds_dict['dry_time'] = str(self.tab_treat_dry_time_listbox.get(index))
					
					#Change this to a database table and lookup at some point	
					#['', 'Hot Plate', 'Natural', 'Lab Oven', 'Vacuum Oven','Smartcoater Ovens','Bench Top Coater Ovens','FOM Ovens']			
					if self.tab_treat_dry_met_box.get() == 'Hot Plate':
						conds_dict['dry_met'] = '1'
					elif self.tab_treat_dry_met_box.get() == 'Natural':
						conds_dict['dry_met'] = '2'
					elif self.tab_treat_dry_met_box.get() == 'Lab Oven':
						conds_dict['dry_met'] = '3'
					elif self.tab_treat_dry_met_box.get() == 'Vacuum Oven':
						conds_dict['dry_met'] = '4'	
					elif self.tab_treat_dry_met_box.get() == 'Smartcoater Ovens':
						conds_dict['dry_met'] = '5'	
					elif self.tab_treat_dry_met_box.get() == 'Bench Top Coater Ovens':
						conds_dict['dry_met'] = '6'	
					elif self.tab_treat_dry_met_box.get() == 'FOM Ovens':
						conds_dict['dry_met'] = '7'	
					
					#Get the smartcoater settings
					if self.tab_treat_dry_met_box.get() == 'Smartcoater Ovens':
						conds_dict['sc_web_speed'] = self.tab_treat_dry_sc_speed_var.get()
						conds_dict['sc_flow_1'] = self.tab_treat_dry_sc_flow_1_var.get()
						conds_dict['sc_flow_2'] = self.tab_treat_dry_sc_flow_2_var.get()
						conds_dict['sc_temp_1'] = self.tab_treat_dry_sc_temp_1_var.get()
						conds_dict['sc_temp_2'] = self.tab_treat_dry_sc_temp_2_var.get()
					
					#Change this to a database table and lookup at some point	
					if self.tab_treat_dry_atm_box.get() == 'Air':
						conds_dict['dry_atm'] = '1'	
					elif self.tab_treat_dry_atm_box.get() == 'Nitrogen':
						conds_dict['dry_atm'] = '2'	
					elif self.tab_treat_dry_atm_box.get() == 'Vacuum':
						conds_dict['dry_atm'] = '3'
						
					conds_lst.append(conds_dict)
					function_name = 'treatment_conds'
					other_col = 'treatment_conds_id'
					other_table = 'treatments'
					method_col = 'treatment_method_id'
					conds_col = 'treatment_conds_id'  
					name_col = 'name'
					name = '%s' % self.tab_treat_dry_name_box.get()	
						
				inputs_inserted = self.dep_conds_mod(self, conds_lst, dep_met_id_select_result, function_name, self.conn, other_col, other_table, method_col, conds_col, name_col, name)
					
				self.tab_treat_dry_status_label_var.set(inputs_inserted[1])
				
				self.update_treat_dry_combo_box()						
	
	def commit_plasma_to_database(self, *args):
		##### check if the plasma name exists already #####	
		tab_plasma_name_exists_select = self.conn.execute('SELECT id FROM treatment_conds WHERE name = ?', (self.tab_treat_plasma_name_box.get(),))
		tab_plasma_name_exists_select_result = tab_plasma_name_exists_select.fetchall()
		
		if tab_plasma_name_exists_select_result:
			self.tab_plasma_status_label_var.set('Status: Plasma name already exists, update and try again.')
		else:
			conds_lst = []
			x = 'Plasma'
			id_select = self.conn.execute('SELECT id FROM treatment_methods WHERE name = ?', (x,))
			id_select_result = id_select.fetchone()[0]
			
			conds_dict = { 'name':self.tab_treat_plasma_name_box.get(),
						'plasma_cleaner':self.tab_treat_plasma_cleaner_box.current(),
						'gas_1':self.tab_treat_plasma_gas1_box.current(),
						'gas_2':self.tab_treat_plasma_gas2_box.current(),
						'gas_flow_1':self.tab_plasma_spin_flow1_spin.get(),
						'gas_flow_2':self.tab_plasma_spin_flow2_spin.get(),
						'vac_plasma':self.tab_plasma_spin_vac_spin.get(),
						'power_plasma':self.tab_plasma_spin_power_spin.get(),
						'time_plasma':self.tab_plasma_spin_time_spin.get(),
						'treatment_method_id':id_select_result,
						}
			conds_lst.append(conds_dict)
			function_name = 'treatment_conds'
			other_col = 'treatment_conds_id'
			other_table = 'treatments'
			method_col = 'treatment_method_id'
			conds_col = 'treatment_conds_id'  
			name_col = 'name'
			name = '%s' % self.tab_treat_plasma_name_box.get()		
			inputs_inserted = self.dep_conds_mod(self, conds_lst, id_select_result, function_name, self.conn, other_col, other_table, method_col, conds_col, name_col, name)
			self.tab_plasma_status_label_var.set(inputs_inserted[1])
			self.update_treat_plasma_combo_box()
			
	def tab_treat_uv_commit(self,*args):
		name_exists_select = self.conn.execute('SELECT id FROM treatment_conds WHERE name = ?', (self.tab_treat_uv_name_box.get(),))
		name_exists_select_result = name_exists_select.fetchall()
		
		if name_exists_select_result:
			self.tab_treat_uv_status_label_var.set('Status: Light treatment name already exists, update and try again.')
		else:
			conds_lst = []
			x = 'Light'
			id_select = self.conn.execute('SELECT id FROM treatment_methods WHERE name = ?', (x,))
			id_select_result = id_select.fetchone()[0]

			conds_dict = { 
						'name':self.tab_treat_uv_name_box.get(),
						'light_source':self.tab_treat_uv_source_box.get(),
						'light_time':self.tab_treat_uv_time_var.get(),
						'light_atm':self.tab_treat_uv_atm_box.get(),
						'light_intensity':self.tab_treat_uv_set_var.get(),
						'treatment_method_id':id_select_result,
						}
			conds_lst.append(conds_dict)
			function_name = 'treatment_conds'
			other_col = 'treatment_conds_id'
			other_table = 'treatments'
			method_col = 'treatment_method_id'
			conds_col = 'treatment_conds_id'  
			name_col = 'name'
			name = '%s' % self.tab_treat_uv_name_box.get()		
			inputs_inserted = self.dep_conds_mod(self, conds_lst, id_select_result, function_name, self.conn, other_col, other_table, method_col, conds_col, name_col, name)
			self.tab_treat_uv_status_label_var.set(inputs_inserted[1])
					
	def tab_treat_dry_listbox_selection_time(self, *args):
		items = map(int, self.tab_treat_dry_time_listbox.curselection())
		self.tab_treat_dry_initial_listbox.selection_clear(first=0, last=END)
		self.tab_treat_dry_ramp_listbox.selection_clear(first=0, last=END)
		self.tab_treat_dry_final_listbox.selection_clear(first=0, last=END)
		for i in items:
			self.tab_treat_dry_initial_listbox.select_set(i)
			self.tab_treat_dry_ramp_listbox.select_set(i)
			self.tab_treat_dry_final_listbox.select_set(i)
					
	def tab_treat_dry_listbox_selection_ramp(self, *args):
		items = map(int, self.tab_treat_dry_ramp_listbox.curselection())
		self.tab_treat_dry_initial_listbox.selection_clear(first=0, last=END)
		self.tab_treat_dry_final_listbox.selection_clear(first=0, last=END)
		self.tab_treat_dry_time_listbox.selection_clear(first=0, last=END)
		for i in items:
			self.tab_treat_dry_initial_listbox.select_set(i)
			self.tab_treat_dry_final_listbox.select_set(i)
			self.tab_treat_dry_time_listbox.select_set(i)
					
	def tab_treat_dry_listbox_selection_final(self, *args):
		items = map(int, self.tab_treat_dry_final_listbox.curselection())
		self.tab_treat_dry_initial_listbox.selection_clear(first=0, last=END)
		self.tab_treat_dry_ramp_listbox.selection_clear(first=0, last=END)
		self.tab_treat_dry_time_listbox.selection_clear(first=0, last=END)
		for i in items:
			self.tab_treat_dry_initial_listbox.select_set(i)
			self.tab_treat_dry_ramp_listbox.select_set(i)
			self.tab_treat_dry_time_listbox.select_set(i)

	def tab_treat_dry_listbox_selection_initial(self, *args):
		items = map(int, self.tab_treat_dry_initial_listbox.curselection())
		self.tab_treat_dry_final_listbox.selection_clear(first=0, last=END)
		self.tab_treat_dry_ramp_listbox.selection_clear(first=0, last=END)
		self.tab_treat_dry_time_listbox.selection_clear(first=0, last=END)
		for i in items:
			self.tab_treat_dry_final_listbox.select_set(i)
			self.tab_treat_dry_ramp_listbox.select_set(i)
			self.tab_treat_dry_time_listbox.select_set(i)
					
	def tab_treat_dry_multi_list_vsb(self, *args):
		self.tab_treat_dry_initial_listbox.yview(*args)
		self.tab_treat_dry_final_listbox.yview(*args)
		self.tab_treat_dry_ramp_listbox.yview(*args)
		self.tab_treat_dry_time_listbox.yview(*args)
			
	def tab_treat_dry_remove_to_listbox(self, *args):
		items = map(int, self.tab_treat_dry_initial_listbox.curselection())
		for i in items:
			self.tab_treat_dry_initial_listbox.delete(i)
			self.tab_treat_dry_final_listbox.delete(i)
			self.tab_treat_dry_ramp_listbox.delete(i)
			self.tab_treat_dry_time_listbox.delete(i)
			
	def tab_treat_dry_add_to_listbox(self, *args):
		initial_input = self.tab_treat_dry_set_initial_spin.get()
		final_input = self.tab_treat_dry_set_final_spin.get()
		ramp_input = self.tab_treat_dry_set_ramp_spin.get()
		time_input = self.tab_treat_dry_set_time_spin.get()
		if initial_input and final_input and ramp_input and time_input:
			self.tab_treat_dry_initial_listbox.insert(END, initial_input)
			self.tab_treat_dry_final_listbox.insert(END, final_input)
			self.tab_treat_dry_ramp_listbox.insert(END, ramp_input)
			self.tab_treat_dry_time_listbox.insert(END, time_input)

	
	def update_treat_clean_combo_box(self, *args):
		#Find the index of treatment_methods that corresponds to Cleaning
		#Use this to find all the treatments names that has this treatment_method_id
		#Add these to the list box
		self.tab_treat_clean_name_list = []
		self.tab_treat_clean_name_box.set(False)
		
		x = 'Cleaning'
		id_select = self.conn.execute('SELECT id FROM treatment_methods WHERE name = ?', (x,))
		id_select_result = id_select.fetchone()[0]
			
		name_exists_select = self.conn.execute('SELECT name FROM treatment_conds WHERE treatment_method_id = ?', (id_select_result,))
		name_exists_select_result = name_exists_select.fetchall()
		
		if not name_exists_select_result:
			self.tab_treat_clean_status_label_var.set('Status: No Cleaning treatments available.')
			
		else:		
			for i in name_exists_select_result:
				if i[0]:
					self.tab_treat_clean_name_list.append(i[0])
		self.tab_treat_clean_name_box['values'] = self.tab_treat_clean_name_list
											
	def update_treat_dry_combo_box(self, *args):
		#Find the index of treatment_methods that corresponds to Drying
		#Use this to find all the treatments names that has this treatment_method_id
		#Add these to the list box
		self.tab_treat_dry_name_list = []
		self.tab_treat_dry_name_box.set(False)
		
		x = 'Drying'
		id_select = self.conn.execute('SELECT id FROM treatment_methods WHERE name = ?', (x,))
		id_select_result = id_select.fetchone()[0]
			
		name_exists_select = self.conn.execute('SELECT name FROM treatment_conds WHERE treatment_method_id = ?', (id_select_result,))
		name_exists_select_result = name_exists_select.fetchall()
		
		if not name_exists_select_result:
			self.tab_treat_dry_status_label_var.set('Status: No Drying treatments available.')
			
		else:		
			for i in name_exists_select_result:
				if i[0]:
					self.tab_treat_dry_name_list.append(i[0])
		self.tab_treat_dry_name_box['values'] = self.tab_treat_dry_name_list
	
	
	def update_treat_plasma_combo_box(self, *args):
		#Find the index of treatment_methods that corresponds to Plasma
		#Use this to find all the treatments names that has this treatment_method_id
		#Add these to the list box
		self.tab_treat_plasma_name_list = []
		self.tab_treat_plasma_name_box.set(False)
		
		x = 'Plasma'
		id_select = self.conn.execute('SELECT id FROM treatment_methods WHERE name = ?', (x,))
		id_select_result = id_select.fetchone()[0]
			
		name_exists_select = self.conn.execute('SELECT name FROM treatment_conds WHERE treatment_method_id = ?', (id_select_result,))
		name_exists_select_result = name_exists_select.fetchall()

		if not name_exists_select_result:
			self.tab_plasma_status_label_var.set('Status: No Plasma treatments available.')
			
		else:		
			for i in name_exists_select_result:
				if i[0]:
					self.tab_treat_plasma_name_list.append(i[0])
		self.tab_treat_plasma_name_box['values'] = self.tab_treat_plasma_name_list
		
	def update_treat_canvas_scroll(self, *args):
		self.tab_treat_canvas.config(scrollregion=self.tab_treat_canvas.bbox(ALL))		
	def layers_tk(self, *args):
		self.tab_layers_canvas = Canvas(self.tab_layers, width=1300, height=600)
		self.tab_layers_canvas.grid(row=0, column=0)
		
		#A frame in canvas to hold all the other widgets
		self.tab_layers_frame = Frame(self.tab_layers_canvas, width=1300, height=600)
		self.tab_layers_frame.grid(row=1, column=0)
		
		#A scroll bar in the tab that controls the canvas position
		self.tab_layers_scroll = Scrollbar(self.tab_layers, orient='vertical', command=self.tab_layers_canvas.yview)
		
		self.tab_layers_canvas.configure(yscrollcommand=self.tab_layers_scroll.set)
		
		self.tab_layers_scroll.grid(row=0, column=1, sticky=N+S)
		#A window for the canvas
		self.tab_layers_canvas.create_window((4,4), window=self.tab_layers_frame, anchor="nw")
		
		self.tab_layers_frame.bind("<Configure>", self.update_layers_canvas_scroll)
		
		#Another frame in the first frame
		self.tab_layers_frame_prop = Frame(self.tab_layers_frame, width=1000, height=600)
		self.tab_layers_frame_prop.grid(row=0, column=0)
		
		#A widget in the second frame
		
		##### layer type ################
		self.tab_layers_type_label = Label(self.tab_layers_frame_prop, text="Layer Type:")
		self.tab_layers_type_label.grid(row=0, column=0, sticky=E)
		
		### Combobox for the deposited formulation ############
		self.tab_layers_type_list = []
		self.tab_layers_type_label_var = StringVar()
		self.tab_layers_type_box = Combobox(self.tab_layers_frame_prop, textvariable=self.tab_layers_type_label_var, width=40)
		self.tab_layers_type_box.bind('<<ComboboxSelected>>', self.update_layers_layer_combo_box)
		self.tab_layers_type_box['values'] = self.tab_layers_type_list
		self.tab_layers_type_box.grid(row=0, column=1, sticky=W)
		self.tab_layers_type_box.state(['readonly'])
		self.tab_layers_get_type_list()
		
		self.tab_layers_label = Label(self.tab_layers_frame_prop, text="Layer Name:")
		self.tab_layers_label.grid(row=1, column=0, sticky=E)
		
		#### Combobox layer name ####
		self.tab_layers_name_label_var = StringVar()
		self.tab_layers_names_list = []
		self.tab_layers_name_box = Combobox(self.tab_layers_frame_prop, textvariable=self.tab_layers_name_label_var, width=80)
		self.tab_layers_name_box.bind('<<ComboboxSelected>>', self.tab_layers_update_previous)
		self.tab_layers_name_box['values'] = self.tab_layers_names_list
		self.tab_layers_name_box.grid(row=1, column=1, sticky=W)
		
		self.tab_layer_check_var_complete = IntVar()
		self.tab_layer_check_complete = Checkbutton(self.tab_layers_frame_prop, text="Show Used", variable=self.tab_layer_check_var_complete,command=self.update_layers_layer_combo_box)
		self.tab_layer_check_complete.grid(row=1, column=2, sticky=W)
		
		self.tab_layer_but_complete = Button(self.tab_layers_frame_prop, text='Switch Used / Unused', command=self.mark_layer_complete)
		self.tab_layer_but_complete.grid(row=1, column=3)
		
		#### get the layer names already in the database ######
		self.tab_layers_get_layer_names()
		
		
		##### Deposited formulation ################
		self.tab_layers_form_label = Label(self.tab_layers_frame_prop, text="Formulation Name:")
		self.tab_layers_form_label.grid(row=2, column=0, sticky=E)
		
		### Combobox for the deposited formulation ############
		self.tab_layers_form_label_var = StringVar()
		self.tab_layers_form_list = []
		self.tab_layers_form_box = Combobox(self.tab_layers_frame_prop, textvariable=self.tab_layers_form_label_var, width=80)
		self.tab_layers_form_box.bind('<<ComboboxSelected>>')
		self.tab_layers_form_box['values'] = self.tab_layers_form_list
		self.tab_layers_form_box.grid(row=2, column=1, sticky=W)
		self.tab_layers_form_box.state(['readonly'])
		#### get the formulation names already in the database ######
		
		
		##### Deposition method ################
		self.tab_layers_dep_label = Label(self.tab_layers_frame_prop, text="Deposition Method:")
		self.tab_layers_dep_label.grid(row=3, column=0, sticky=E)
		
		### Combobox for the dep method ############
		self.tab_layers_dep_label_var = StringVar()
		self.tab_layers_dep_list = []
		self.tab_layers_dep_box = Combobox(self.tab_layers_frame_prop, textvariable=self.tab_layers_dep_label_var, width=20)
		self.tab_layers_dep_box.bind('<<ComboboxSelected>>', self.tab_layers_get_cond_list)
		self.tab_layers_dep_box['values'] = self.tab_layers_dep_list
		self.tab_layers_dep_box.grid(row=3, column=1, sticky=W)
		self.tab_layers_dep_box.state(['readonly'])
		self.tab_layers_get_dep_method_names()
		
		##### Deposition conditions ################
		self.tab_layers_cond_label = Label(self.tab_layers_frame_prop, text="Deposition Conditions:")
		self.tab_layers_cond_label.grid(row=4, column=0, sticky=E)
		
		### Combobox for the deposiion conds ############
		self.tab_layers_cond_label_var = StringVar()
		self.tab_layers_cond_list = []
		self.tab_layers_cond_box = Combobox(self.tab_layers_frame_prop, textvariable=self.tab_layers_cond_label_var, width=80)
		self.tab_layers_cond_box.bind('<<ComboboxSelected>>', self.tab_layers_dep_conds_update)
		self.tab_layers_cond_box['values'] = self.tab_layers_cond_list
		self.tab_layers_cond_box.grid(row=4, column=1, sticky=W)
		self.tab_layers_cond_box.state(['readonly'])
		
		
		#####  ################
		self.tab_layers_thick_label = Label(self.tab_layers_frame_prop, text="Layer Thickness (nm):")
		self.tab_layers_thick_label.grid(row=5, column=0, sticky=E)
		
		self.tab_layers_spin_thick_var = StringVar()
		self.tab_layers_spin_thick = Spinbox(self.tab_layers_frame_prop, from_=0, to=99999999, format="%.2f", increment=0.01, textvariable=self.tab_layers_spin_thick_var, width=20)
		self.tab_layers_spin_thick.grid(row=5, column=1, sticky=W)
		
		self.tab_layers_colour_but = Button(self.tab_layers_frame_prop, text='Select Colour', command=self.layer_get_colour)
		self.tab_layers_colour_but.grid(row=5, column=2, sticky=E)
		
		self.tab_layers_picture_canvas = Canvas(self.tab_layers_frame_prop, width=150, height=50)
		self.tab_layers_picture_canvas.grid(row=5, column=3)
		self.tab_layers_picture_canvas_rec = self.tab_layers_picture_canvas.create_rectangle(0, 0, 150, 50, fill="#FFFFFF")
		self.tab_layers_picture_canvas.create_text(10, 10, text="Layer Colour",width=60,anchor=NW)
		
		self.tab_layers_colour_entry_var = StringVar() 
		self.tab_layers_colour_entry = Entry(self.tab_layers_frame_prop, width=20, textvariable=self.tab_layers_colour_entry_var,state="readonly")
		self.tab_layers_colour_entry.grid(row=5, column=4, sticky=W)
		self.tab_layers_colour_entry_var.set("#FFFFFF")
		
		self.tab_layers_layer_commit_but = Button(self.tab_layers_frame_prop, text='Commit Layer to Database', command=self.commit_layer)
		self.tab_layers_layer_commit_but.grid(row=6, column=0, sticky=E)
		
		self.tab_layers_layer_status_label_var = StringVar()
		self.tab_layers_layer_status_label = Label(self.tab_layers_frame_prop, textvariable=self.tab_layers_layer_status_label_var)
		self.tab_layers_layer_status_label.grid(row=6, column=1, sticky=W)
		self.tab_layers_layer_status_label_var.set('Status:')
		
		### Each deposition method will have a frame below to enter new conditions in #########
		##### A frame to hold the spin coating condditions inputs ######
		self.tab_layers_spin_frame = LabelFrame(self.tab_layers_frame, text='Spin Coating Conditions')
		self.tab_layers_spin_frame.grid(row=1, column=0, sticky=W)
		
		self.tab_layers_spin_prop_frame = Frame(self.tab_layers_spin_frame)
		self.tab_layers_spin_prop_frame.grid(row=0, column=0, sticky=W)
		
		##### dddeposition conition name  ################
		self.tab_layers_spin_dep_name = Label(self.tab_layers_spin_prop_frame, text="Spin Coating Conditions Name:")
		self.tab_layers_spin_dep_name.grid(row=0, column=0, sticky=E)
		
		self.tab_layers_spin_dep_name_entry_var = StringVar() 
		self.tab_layers_spin_dep_name_entry = Entry(self.tab_layers_spin_prop_frame, width=80, textvariable=self.tab_layers_spin_dep_name_entry_var)
		self.tab_layers_spin_dep_name_entry.grid(row=0, column=1, sticky=W, columnspan=5)
		
		##### spin coater  ################
		self.tab_layers_spin_label = Label(self.tab_layers_spin_prop_frame, text="Spin Coater:")
		self.tab_layers_spin_label.grid(row=1, column=0, sticky=E)
		
		### Combobox for the spin coater id ############
		self.tab_layers_spin_id_label_var = StringVar()
		self.tab_layers_spin_id_list = ['PV-Lab', 'PV-GB', 'Low humidity','Ultra clean', '']
		self.tab_layers_spin_id_box = Combobox(self.tab_layers_spin_prop_frame, textvariable=self.tab_layers_spin_id_label_var, width=20)
		self.tab_layers_spin_id_box.bind('<<ComboboxSelected>>')
		self.tab_layers_spin_id_box['values'] = self.tab_layers_spin_id_list
		self.tab_layers_spin_id_box.grid(row=1, column=1, sticky=W)
		self.tab_layers_spin_id_box.state(['readonly'])
		
		##### temperature of substrate ################
		self.tab_layers_spin_temp_label = Label(self.tab_layers_spin_prop_frame, text="Substrate Temperature:")
		self.tab_layers_spin_temp_label.grid(row=2, column=0, sticky=E)
		
		self.tab_layers_spin_spin_temp_var = StringVar()
		self.tab_layers_spin_spin_temp = Spinbox(self.tab_layers_spin_prop_frame, from_=0, to=99999999, format="%.2f", increment=0.01, textvariable=self.tab_layers_spin_spin_temp_var, width=20)
		self.tab_layers_spin_spin_temp.grid(row=2, column=1, sticky=W)
		self.tab_layers_spin_spin_temp_var.set(False)	
		
		##### temperature of solution ################
		self.tab_layers_spin_soln_temp_label = Label(self.tab_layers_spin_prop_frame, text="Solution Temperature:")
		self.tab_layers_spin_soln_temp_label.grid(row=2, column=2, sticky=E)
		
		self.tab_layers_spin_spin_soln_temp_var = StringVar()
		self.tab_layers_spin_spin_soln_temp = Spinbox(self.tab_layers_spin_prop_frame, from_=0, to=99999999, format="%.2f", increment=0.01, textvariable=self.tab_layers_spin_spin_soln_temp_var, width=20)
		self.tab_layers_spin_spin_soln_temp.grid(row=2, column=3, sticky=W)
		self.tab_layers_spin_spin_soln_temp_var.set(20.0)
		
		##### delay before spin ################
		self.tab_layers_spin_delay_label = Label(self.tab_layers_spin_prop_frame, text="Delay before spin (s):")
		self.tab_layers_spin_delay_label.grid(row=3, column=0, sticky=E)
		
		self.tab_layers_spin_spin_delay_var = StringVar()
		self.tab_layers_spin_spin_delay = Spinbox(self.tab_layers_spin_prop_frame, from_=0, to=99999999, format="%.2f", increment=0.01, textvariable=self.tab_layers_spin_spin_delay_var, width=20)
		self.tab_layers_spin_spin_delay.grid(row=3, column=1, sticky=W)
		self.tab_layers_spin_spin_delay_var.set(False)		
		
		##### spin atmosphere  ################
		self.tab_layers_spin_atm_label = Label(self.tab_layers_spin_prop_frame, text="Spin Atmosphere:")
		self.tab_layers_spin_atm_label.grid(row=4, column=0, sticky=E)
		
		### Combobox for the spin coater id ############
		self.tab_layers_spin_atm_label_var = StringVar()
		self.tab_layers_spin_atm_list = ['Air', 'Nitrogen', '']
		self.tab_layers_spin_atm_box = Combobox(self.tab_layers_spin_prop_frame, textvariable=self.tab_layers_spin_atm_label_var, width=20)
		self.tab_layers_spin_atm_box.bind('<<ComboboxSelected>>')
		self.tab_layers_spin_atm_box['values'] = self.tab_layers_spin_atm_list
		self.tab_layers_spin_atm_box.grid(row=4, column=1, sticky=W)
		self.tab_layers_spin_atm_box.state(['readonly'])
		
		self.tab_layers_spin_vol_label = Label(self.tab_layers_spin_prop_frame, text="Volume Dispensed (ml):")
		self.tab_layers_spin_vol_label.grid(row=5, column=0, sticky=E)
		
		self.tab_layers_spin_spin_vol_var = StringVar()
		self.tab_layers_spin_spin_vol = Spinbox(self.tab_layers_spin_prop_frame, from_=0, to=99999999, format="%.2f", increment=0.01, textvariable=self.tab_layers_spin_spin_vol_var, width=20)
		self.tab_layers_spin_spin_vol.grid(row=5, column=1, sticky=W)
		self.tab_layers_spin_spin_vol_var.set(False)	
		
		#### A frame for the enrty boxes #######
		self.tab_layers_spin_entry_frame = Frame(self.tab_layers_spin_frame)
		self.tab_layers_spin_entry_frame.grid(row=4, column=0, sticky=W)
		
		self.tab_layers_spin_speed_entry_label = Label(self.tab_layers_spin_entry_frame, text='Spin Speed (RPM):')
		self.tab_layers_spin_speed_entry_label.grid(row=0, column=0)
		
		
		self.tab_layers_spin_spin_speed_var = StringVar()
		self.tab_layers_spin_spin_speed = Spinbox(self.tab_layers_spin_entry_frame, from_=0, to=99999999, format="%.2f", increment=0.01, textvariable=self.tab_layers_spin_spin_speed_var, width=20)
		self.tab_layers_spin_spin_speed.grid(row=0, column=1, sticky=W)
		self.tab_layers_spin_spin_speed_var.set(False)	

		self.tab_layers_spin_acc_entry_label = Label(self.tab_layers_spin_entry_frame, text='Spin Acceleration (RPM/s):')
		self.tab_layers_spin_acc_entry_label.grid(row=0, column=2)
		
		self.tab_layers_spin_spin_acc_var = StringVar()
		self.tab_layers_spin_spin_acc = Spinbox(self.tab_layers_spin_entry_frame, from_=0, to=99999999, format="%.2f", increment=0.01, textvariable=self.tab_layers_spin_spin_acc_var, width=20)
		self.tab_layers_spin_spin_acc.grid(row=0, column=3, sticky=W)
		self.tab_layers_spin_spin_acc_var.set(False)
		
		self.tab_layers_spin_time_entry_label = Label(self.tab_layers_spin_entry_frame, text='Spin Time (s):')
		self.tab_layers_spin_time_entry_label.grid(row=0, column=4)
		
		self.tab_layers_spin_spin_time_var = StringVar()
		self.tab_layers_spin_spin_time = Spinbox(self.tab_layers_spin_entry_frame, from_=0, to=99999999, format="%.2f", increment=0.01, textvariable=self.tab_layers_spin_spin_time_var, width=20)
		self.tab_layers_spin_spin_time.grid(row=0, column=5, sticky=W)
		self.tab_layers_spin_spin_time_var.set(False)
		
		self.tab_layers_spin_enter_but = Button(self.tab_layers_spin_entry_frame, text='Add New Spin Stage', command=self.tab_layers_spin_conds_add_stage)
		self.tab_layers_spin_enter_but.grid(row=1, column=0, sticky=W)
		
		self.tab_layers_spin_remove_but = Button(self.tab_layers_spin_entry_frame, text='Remove Spin Stage', command=self.tab_layers_spin_conds_remove_stage)
		self.tab_layers_spin_remove_but.grid(row=1, column=1, sticky=W)
		
		#####Solvent drip#####
		self.tab_layers_spin_drip_time_entry_label = Label(self.tab_layers_spin_entry_frame, text='Drip Time (s):')
		self.tab_layers_spin_drip_time_entry_label.grid(row=2, column=0)
		
		self.tab_layers_spin_drip_time_var = StringVar()
		self.tab_layers_spin_drip_time = Spinbox(self.tab_layers_spin_entry_frame, from_=0, to=99999999, format="%.2f", increment=0.01, textvariable=self.tab_layers_spin_drip_time_var, width=20)
		self.tab_layers_spin_drip_time.grid(row=3, column=0, sticky=W)
		self.tab_layers_spin_drip_time_var.set(False)
		
		self.tab_layers_spin_drip_sol_entry_label = Label(self.tab_layers_spin_entry_frame, text='Drip Formulation:')
		self.tab_layers_spin_drip_sol_entry_label.grid(row=2, column=1)
		
		self.tab_layers_spin_drip_sol_label_var = StringVar()
		self.tab_layers_spin_drip_sol_list = self.tab_layers_form_list
		self.tab_layers_spin_drip_sol_box = Combobox(self.tab_layers_spin_entry_frame, textvariable=self.tab_layers_spin_drip_sol_label_var, width=20)
		self.tab_layers_spin_drip_sol_box.bind('<<ComboboxSelected>>', self.tab_layers_get_form_names)
		self.tab_layers_spin_drip_sol_box['values'] = self.tab_layers_spin_drip_sol_list
		self.tab_layers_spin_drip_sol_box.grid(row=3, column=1, sticky=W)
		self.tab_layers_spin_drip_sol_box.state(['readonly'])
		self.tab_layers_get_form_names()
		
		self.tab_layers_spin_drip_quan_entry_label = Label(self.tab_layers_spin_entry_frame, text='Drip Volume (ml):')
		self.tab_layers_spin_drip_quan_entry_label.grid(row=2, column=2)
		
		self.tab_layers_spin_drip_quan_var = StringVar()
		self.tab_layers_spin_drip_quan = Spinbox(self.tab_layers_spin_entry_frame, from_=0, to=99999999, format="%.2f", increment=0.01, textvariable=self.tab_layers_spin_drip_quan_var, width=20)
		self.tab_layers_spin_drip_quan.grid(row=3, column=2, sticky=W)
		self.tab_layers_spin_drip_quan_var.set(False)
		
		

		#### A frame for the spin conditions boxes#######
		#### Could use list boxes and selection or a for loop to create lots of selectors... #####
		self.tab_layers_spin_conds_frame = Frame(self.tab_layers_spin_frame)
		self.tab_layers_spin_conds_frame.grid(row=5, column=0, sticky=W)
		
		self.tab_layers_spin_speed_label = Label(self.tab_layers_spin_conds_frame, text='Spin Speed (RPM):')
		self.tab_layers_spin_speed_label.grid(row=0, column=0)
		
		self.tab_layers_spin_acc_label = Label(self.tab_layers_spin_conds_frame, text='Spin Acceleration (RPM/s):')
		self.tab_layers_spin_acc_label.grid(row=0, column=1)
		
		self.tab_layers_spin_time_label = Label(self.tab_layers_spin_conds_frame, text='Spin Time (s):')
		self.tab_layers_spin_time_label.grid(row=0, column=2)
		
		self.tab_layers_listbox_vsb = Scrollbar(self.tab_layers_spin_conds_frame)
		self.tab_layers_listbox_vsb.grid(row=1, column=4, sticky=N+S)

		self.tab_layers_spin_speed_listbox = Listbox(self.tab_layers_spin_conds_frame, yscrollcommand=self.tab_layers_listbox_vsb.set, exportselection=False)
		self.tab_layers_spin_speed_listbox.grid(row=1, column=0)
		self.tab_layers_spin_speed_listbox.bind('<<ListboxSelect>>', self.tab_layers_spin_dep_conds_speed_list_selection)
		
		self.tab_layers_spin_acc_listbox = Listbox(self.tab_layers_spin_conds_frame, yscrollcommand=self.tab_layers_listbox_vsb.set, exportselection=False)
		self.tab_layers_spin_acc_listbox.grid(row=1, column=1)
		self.tab_layers_spin_acc_listbox.bind('<<ListboxSelect>>', self.tab_layers_spin_dep_conds_acc_list_selection)
		
		self.tab_layers_spin_time_listbox = Listbox(self.tab_layers_spin_conds_frame, yscrollcommand=self.tab_layers_listbox_vsb.set, exportselection=False)
		self.tab_layers_spin_time_listbox.grid(row=1, column=2)
		self.tab_layers_spin_time_listbox.bind('<<ListboxSelect>>', self.tab_layers_spin_dep_conds_time_list_selection)
		
		self.tab_layers_listbox_vsb.config(command=self.tab_layers_multi_list_vsb)
		
		self.tab_layers_spin_commit_but = Button(self.tab_layers_spin_conds_frame, text='Commit Spin Conditions to Database', command=self.tab_layers_spin_conds_commit_conds)
		self.tab_layers_spin_commit_but.grid(row=2, column=0, sticky=W, columnspan=10)
	
	
	
		######## Frame for the spray conds ######
		self.tab_layers_spray_conds_frame = Labelframe(self.tab_layers_frame, text='Spray Coating Conditions')
		self.tab_layers_spray_conds_frame.grid(row=2, column=0, sticky=W)
		
		self.tab_layers_spray_pres_label = Label(self.tab_layers_spray_conds_frame, text='Spray Pressure (PSI):')
		self.tab_layers_spray_pres_label.grid(row=0, column=0, sticky=E)
		
		self.tab_layers_spray_pres_spin_var = StringVar()
		self.tab_layers_spray_pres_spin = Spinbox(self.tab_layers_spray_conds_frame, from_=0, to=999, format="%.1f", increment=0.1, textvariable=self.tab_layers_spray_pres_spin_var, width=10)
		self.tab_layers_spray_pres_spin.grid(row=0, column=1, sticky=W)
		self.tab_layers_spray_pres_spin_var.set(False)
		
		self.tab_layers_spray_dist_label = Label(self.tab_layers_spray_conds_frame, text='Spray Height (cm):')
		self.tab_layers_spray_dist_label.grid(row=1, column=0, sticky=E)
		
		self.tab_layers_spray_dist_spin_var = StringVar()
		self.tab_layers_spray_dist_spin = Spinbox(self.tab_layers_spray_conds_frame, from_=0, to=999, format="%.1f", increment=0.1, textvariable=self.tab_layers_spray_dist_spin_var, width=10)
		self.tab_layers_spray_dist_spin.grid(row=1, column=1, sticky=W)
		self.tab_layers_spray_dist_spin_var.set(False)
		
		self.tab_layers_spray_temp_label = Label(self.tab_layers_spray_conds_frame, text='Substrate Temperature (degC):')
		self.tab_layers_spray_temp_label.grid(row=2, column=0, sticky=E)
		
		self.tab_layers_spray_temp_spin_var = StringVar()
		self.tab_layers_spray_temp_spin = Spinbox(self.tab_layers_spray_conds_frame, from_=0, to=999, format="%.1f", increment=0.1, textvariable=self.tab_layers_spray_temp_spin_var, width=10)
		self.tab_layers_spray_temp_spin.grid(row=2, column=1, sticky=W)
		self.tab_layers_spray_temp_spin_var.set(False)
		
		self.tab_layers_spray_vol_label = Label(self.tab_layers_spray_conds_frame, text='Volume Coated (ml):')
		self.tab_layers_spray_vol_label.grid(row=3, column=0, sticky=E)
		
		self.tab_layers_spray_vol_spin_var = StringVar()
		self.tab_layers_spray_vol_spin = Spinbox(self.tab_layers_spray_conds_frame, from_=0, to=999, format="%.1f", increment=0.1, textvariable=self.tab_layers_spray_vol_spin_var, width=10)
		self.tab_layers_spray_vol_spin.grid(row=3, column=1, sticky=W)
		self.tab_layers_spray_vol_spin_var.set(False)
		
		self.tab_layers_spray_pass_label = Label(self.tab_layers_spray_conds_frame, text='Number of Passes:')
		self.tab_layers_spray_pass_label.grid(row=4, column=0, sticky=E)
		
		self.tab_layers_spray_pass_spin_var = StringVar()
		self.tab_layers_spray_pass_spin = Spinbox(self.tab_layers_spray_conds_frame, from_=0, to=999, format="%.1f", increment=0.1, textvariable=self.tab_layers_spray_pass_spin_var, width=10)
		self.tab_layers_spray_pass_spin.grid(row=4, column=1, sticky=W)
		self.tab_layers_spray_pass_spin_var.set(False)
		
		self.tab_layers_spray_set_label = Label(self.tab_layers_spray_conds_frame, text='Screw setting (mm):')
		self.tab_layers_spray_set_label.grid(row=5, column=0, sticky=E)
		
		self.tab_layers_spray_set_spin_var = StringVar()
		self.tab_layers_spray_set_spin = Spinbox(self.tab_layers_spray_conds_frame, from_=0, to=999, format="%.1f", increment=0.1, textvariable=self.tab_layers_spray_set_spin_var, width=10)
		self.tab_layers_spray_set_spin.grid(row=5, column=1, sticky=W)
		self.tab_layers_spray_set_spin_var.set(False)
		
		self.tab_layers_spray_name_label = Label(self.tab_layers_spray_conds_frame, text='Spary Conditions Name:')
		self.tab_layers_spray_name_label.grid(row=0, column=2, sticky=E)
		
		self.tab_layers_spray_name_entry_var = StringVar()
		self.tab_layers_spray_name_entry = Entry(self.tab_layers_spray_conds_frame, textvariable=self.tab_layers_spray_name_entry_var, width=35)
		self.tab_layers_spray_name_entry.grid(row=0, column=3, sticky=W)
		
		self.tab_layers_spray_gun_label = Label(self.tab_layers_spray_conds_frame, text='Spary Gun:')
		self.tab_layers_spray_gun_label.grid(row=1, column=2, sticky=E)
		
		self.tab_layers_spray_gun_box_var = StringVar()
		self.tab_layers_spray_gun_list = ['', 'TiO2', 'Carbon']
		self.tab_layers_spray_gun_box = Combobox(self.tab_layers_spray_conds_frame, textvariable=self.tab_layers_spray_gun_box_var, width=15)
		self.tab_layers_spray_gun_box.bind('<<ComboboxSelected>>')
		self.tab_layers_spray_gun_box['values'] = self.tab_layers_spray_gun_list
		self.tab_layers_spray_gun_box.grid(row=1, column=3, sticky=W)
		self.tab_layers_spray_gun_box.state(['readonly'])
		
		self.tab_layers_spray_atm_label = Label(self.tab_layers_spray_conds_frame, text='Spary Atmosphere:')
		self.tab_layers_spray_atm_label.grid(row=2, column=2, sticky=E)
		
		self.tab_layers_spray_atm_box_var = StringVar()
		self.tab_layers_spray_atm_list = ['', 'Air', 'N2']
		self.tab_layers_spray_atm_box = Combobox(self.tab_layers_spray_conds_frame, textvariable=self.tab_layers_spray_atm_box_var, width=15)
		self.tab_layers_spray_atm_box.bind('<<ComboboxSelected>>')
		self.tab_layers_spray_atm_box['values'] = self.tab_layers_spray_atm_list
		self.tab_layers_spray_atm_box.grid(row=2, column=3, sticky=W)
		self.tab_layers_spray_atm_box.state(['readonly'])
		
		self.tab_layers_spray_gas_label = Label(self.tab_layers_spray_conds_frame, text='Spary Feed Gas:')
		self.tab_layers_spray_gas_label.grid(row=3, column=2, sticky=E)
		
		self.tab_layers_spray_gas_box_var = StringVar()
		self.tab_layers_spray_gas_list = ['', 'Compressor air', 'N2']
		self.tab_layers_spray_gas_box = Combobox(self.tab_layers_spray_conds_frame, textvariable=self.tab_layers_spray_gas_box_var, width=15)
		self.tab_layers_spray_gas_box.bind('<<ComboboxSelected>>')
		self.tab_layers_spray_gas_box['values'] = self.tab_layers_spray_gas_list
		self.tab_layers_spray_gas_box.grid(row=3, column=3, sticky=W)
		self.tab_layers_spray_gas_box.state(['readonly'])
		
		self.tab_layers_spray_commit_but = Button(self.tab_layers_spray_conds_frame, text='Commit Spray Conditions to Database', command=self.tab_layers_spray_conds_commit_conds)
		self.tab_layers_spray_commit_but.grid(row=4, column=2, sticky=W, columnspan=10)
	
		######## Frame for the dip conds ######
		self.tab_layers_dip_conds_frame = Labelframe(self.tab_layers_frame, text='Dip Coating Conditions')
		self.tab_layers_dip_conds_frame.grid(row=3, column=0, sticky=W)
		
		self.tab_layers_dip_name_label = Label(self.tab_layers_dip_conds_frame, text='Dip conditions name:')
		self.tab_layers_dip_name_label.grid(row=0, column=0, sticky=E)
		
		self.tab_layers_dip_name_entry_var = StringVar()
		self.tab_layers_dip_name_entry = Entry(self.tab_layers_dip_conds_frame, textvariable=self.tab_layers_dip_name_entry_var)
		self.tab_layers_dip_name_entry.grid(row=0, column=1, sticky=W)
		
		self.tab_layers_dip_quan_label = Label(self.tab_layers_dip_conds_frame, text='Volume of dip solution (cm3):')
		self.tab_layers_dip_quan_label.grid(row=1, column=0, sticky=E)
		
		self.tab_layers_dip_quan_spin_var = StringVar()
		self.tab_layers_dip_quan_spin = Spinbox(self.tab_layers_dip_conds_frame, from_=0, to=999, format="%.1f", increment=0.1, textvariable=self.tab_layers_dip_quan_spin_var, width=10)
		self.tab_layers_dip_quan_spin.grid(row=1, column=1, sticky=W)
		self.tab_layers_dip_quan_spin_var.set(False)
		
		self.tab_layers_dip_sub_temp_label = Label(self.tab_layers_dip_conds_frame, text='Temperature of substrate (degC):')
		self.tab_layers_dip_sub_temp_label.grid(row=2, column=0, sticky=E)
		
		self.tab_layers_dip_sub_temp_spin_var = StringVar()
		self.tab_layers_dip_sub_temp_spin = Spinbox(self.tab_layers_dip_conds_frame, from_=0, to=999, format="%.1f", increment=0.1, textvariable=self.tab_layers_dip_sub_temp_spin_var, width=10)
		self.tab_layers_dip_sub_temp_spin.grid(row=2, column=1, sticky=W)
		self.tab_layers_dip_sub_temp_spin_var.set(False)
		
		self.tab_layers_dip_sol_temp_label = Label(self.tab_layers_dip_conds_frame, text='Temperature of dip solution (degC):')
		self.tab_layers_dip_sol_temp_label.grid(row=3, column=0, sticky=E)
		
		self.tab_layers_dip_sol_temp_spin_var = StringVar()
		self.tab_layers_dip_sol_temp_spin = Spinbox(self.tab_layers_dip_conds_frame, from_=0, to=999, format="%.1f", increment=0.1, textvariable=self.tab_layers_dip_sol_temp_spin_var, width=10)
		self.tab_layers_dip_sol_temp_spin.grid(row=3, column=1, sticky=W)
		self.tab_layers_dip_sol_temp_spin_var.set(False)
		
		self.tab_layers_dip_time_label = Label(self.tab_layers_dip_conds_frame, text='Dip time (min):')
		self.tab_layers_dip_time_label.grid(row=4, column=0, sticky=E)
		
		self.tab_layers_dip_time_spin_var = StringVar()
		self.tab_layers_dip_time_spin = Spinbox(self.tab_layers_dip_conds_frame, from_=0, to=999, format="%.1f", increment=0.1, textvariable=self.tab_layers_dip_time_spin_var, width=10)
		self.tab_layers_dip_time_spin.grid(row=4, column=1, sticky=W)
		self.tab_layers_dip_time_spin_var.set(False)
		
		self.tab_layers_dip_agi_label = Label(self.tab_layers_dip_conds_frame, text='Solution agitated:')
		self.tab_layers_dip_agi_label.grid(row=5, column=0, sticky=E)
		
		self.tab_layers_dip_agi_check_var = IntVar()
		self.tab_layers_dip_agi_check_but = Checkbutton(self.tab_layers_dip_conds_frame, variable=self.tab_layers_dip_agi_check_var)
		self.tab_layers_dip_agi_check_but.grid(row=5, column=1, sticky=W)
		
		self.tab_layers_dip_commit_but = Button(self.tab_layers_dip_conds_frame, text='Commit dip conditions to database', command=self.tab_layers_dip_conds_commit_conds)
		self.tab_layers_dip_commit_but.grid(row=6, column=1, sticky=W)
		
		######## Frame for the bar conds ######
		self.tab_layers_bar_conds_frame = Labelframe(self.tab_layers_frame, text='Bar Coating Conditions')
		self.tab_layers_bar_conds_frame.grid(row=4, column=0, sticky=W)
		
		self.tab_layers_bar_name_label = Label(self.tab_layers_bar_conds_frame, text='Bar conditions name:')
		self.tab_layers_bar_name_label.grid(row=0, column=0, sticky=E)
		
		self.tab_layers_bar_name_entry_var = StringVar()
		self.tab_layers_bar_name_entry = Entry(self.tab_layers_bar_conds_frame, textvariable=self.tab_layers_bar_name_entry_var)
		self.tab_layers_bar_name_entry.grid(row=0, column=1, sticky=W)
		
		self.tab_layers_bar_quan_label = Label(self.tab_layers_bar_conds_frame, text='Volume of Solution (cm3):')
		self.tab_layers_bar_quan_label.grid(row=1, column=0, sticky=E)
		
		self.tab_layers_bar_quan_spin_var = StringVar()
		self.tab_layers_bar_quan_spin = Spinbox(self.tab_layers_bar_conds_frame, from_=0, to=999, format="%.1f", increment=0.1, textvariable=self.tab_layers_bar_quan_spin_var, width=10)
		self.tab_layers_bar_quan_spin.grid(row=1, column=1, sticky=W)
		self.tab_layers_bar_quan_spin_var.set(False)
		
		self.tab_layers_bar_sub_temp_label = Label(self.tab_layers_bar_conds_frame, text='Temperature of substrate (degC):')
		self.tab_layers_bar_sub_temp_label.grid(row=2, column=0, sticky=E)
		
		self.tab_layers_bar_sub_temp_spin_var = StringVar()
		self.tab_layers_bar_sub_temp_spin = Spinbox(self.tab_layers_bar_conds_frame, from_=0, to=999, format="%.1f", increment=0.1, textvariable=self.tab_layers_bar_sub_temp_spin_var, width=10)
		self.tab_layers_bar_sub_temp_spin.grid(row=2, column=1, sticky=W)
		self.tab_layers_bar_sub_temp_spin_var.set(False)
		
		self.tab_layers_bar_sub_temp_label = Label(self.tab_layers_bar_conds_frame, text='Temperature of Bed (degC):')
		self.tab_layers_bar_sub_temp_label.grid(row=3, column=0, sticky=E)
		
		self.tab_layers_bar_bed_temp_spin_var = StringVar()
		self.tab_layers_bar_bed_temp_spin = Spinbox(self.tab_layers_bar_conds_frame, from_=0, to=999, format="%.1f", increment=0.1, textvariable=self.tab_layers_bar_bed_temp_spin_var, width=10)
		self.tab_layers_bar_bed_temp_spin.grid(row=3, column=1, sticky=W)
		self.tab_layers_bar_bed_temp_spin_var.set(False)
		
		self.tab_layers_bar_sol_temp_label = Label(self.tab_layers_bar_conds_frame, text='Temperature of solution (degC):')
		self.tab_layers_bar_sol_temp_label.grid(row=4, column=0, sticky=E)
		
		self.tab_layers_bar_sol_temp_spin_var = StringVar()
		self.tab_layers_bar_sol_temp_spin = Spinbox(self.tab_layers_bar_conds_frame, from_=0, to=999, format="%.1f", increment=0.1, textvariable=self.tab_layers_bar_sol_temp_spin_var, width=10)
		self.tab_layers_bar_sol_temp_spin.grid(row=4, column=1, sticky=W)
		self.tab_layers_bar_sol_temp_spin_var.set(False)
		
		self.tab_layers_bar_speed_label = Label(self.tab_layers_bar_conds_frame, text='Bar Speed (m/min):')
		self.tab_layers_bar_speed_label.grid(row=5, column=0, sticky=E)
		
		self.tab_layers_bar_speed_spin_var = StringVar()
		self.tab_layers_bar_speed_spin = Spinbox(self.tab_layers_bar_conds_frame, from_=0, to=999, format="%.1f", increment=0.1, textvariable=self.tab_layers_bar_speed_spin_var, width=10)
		self.tab_layers_bar_speed_spin.grid(row=5, column=1, sticky=W)
		self.tab_layers_bar_speed_spin_var.set(False)
		
		self.tab_layers_bar_size_label = Label(self.tab_layers_bar_conds_frame, text='Bar Size (um):')
		self.tab_layers_bar_size_label.grid(row=6, column=0, sticky=E)
		
		self.tab_layers_bar_size_spin_var = StringVar()
		self.tab_layers_bar_size_spin = Spinbox(self.tab_layers_bar_conds_frame, from_=0, to=9999, format="%.1f", increment=0.1, textvariable=self.tab_layers_bar_size_spin_var, width=10)
		self.tab_layers_bar_size_spin.grid(row=6, column=1, sticky=W)
		self.tab_layers_bar_size_spin_var.set(False)
		
		self.tab_layers_bar_atm_label = Label(self.tab_layers_bar_conds_frame, text='Coating Atmosphere:')
		self.tab_layers_bar_atm_label.grid(row=7, column=0, sticky=E)
		
		self.tab_layers_bar_atm_box_var = StringVar()
		self.tab_layers_bar_atm_list = ['', 'Air', 'N2']
		self.tab_layers_bar_atm_box = Combobox(self.tab_layers_bar_conds_frame, textvariable=self.tab_layers_bar_atm_box_var, width=15)
		self.tab_layers_bar_atm_box.bind('<<ComboboxSelected>>')
		self.tab_layers_bar_atm_box['values'] = self.tab_layers_bar_atm_list
		self.tab_layers_bar_atm_box.grid(row=7, column=1, sticky=W)
		self.tab_layers_bar_atm_box.state(['readonly'])
		
		self.tab_layers_bar_commit_but = Button(self.tab_layers_bar_conds_frame, text='Commit bar coating conditions to database', command=self.tab_layers_bar_conds_commit_conds)
		self.tab_layers_bar_commit_but.grid(row=8, column=0, sticky=W)
		
		######
		########
		########## evaporation...
		######## Frame for the evap conds ######
		self.tab_layers_evap_conds_frame = Labelframe(self.tab_layers_frame, text='Evaporation Conditions')
		self.tab_layers_evap_conds_frame.grid(row=7, column=0, sticky=W)

		self.tab_layers_evap_name_label = Label(self.tab_layers_evap_conds_frame, text='Evaporation conditions name:')
		self.tab_layers_evap_name_label.grid(row=0, column=0, sticky=E)
		
		self.tab_layers_evap_name_entry_var = StringVar()
		self.tab_layers_evap_name_entry = Entry(self.tab_layers_evap_conds_frame, textvariable=self.tab_layers_evap_name_entry_var)
		self.tab_layers_evap_name_entry.grid(row=0, column=1, sticky=W)
		
		self.tab_layers_evap_label = Label(self.tab_layers_evap_conds_frame, text='Evaporator:')
		self.tab_layers_evap_label.grid(row=1, column=0, sticky=E)
		
		self.tab_layers_evap_box_var = StringVar()
		self.tab_layers_evap_list = ['', 'Bell jar', 'MBraun GB']
		self.tab_layers_evap_box = Combobox(self.tab_layers_evap_conds_frame, textvariable=self.tab_layers_evap_box_var, width=15)
		self.tab_layers_evap_box.bind('<<ComboboxSelected>>')
		self.tab_layers_evap_box['values'] = self.tab_layers_evap_list
		self.tab_layers_evap_box.grid(row=1, column=1, sticky=W)
		self.tab_layers_evap_box.state(['readonly'])

		self.tab_layers_evap_rate_label = Label(self.tab_layers_evap_conds_frame, text='Deposition rate (A/s):')
		self.tab_layers_evap_rate_label.grid(row=2, column=0, sticky=E)
		
		self.tab_layers_evap_rate_spin_var = StringVar()
		self.tab_layers_evap_rate_spin = Spinbox(self.tab_layers_evap_conds_frame, from_=0, to=9999, format="%.1f", increment=0.1, textvariable=self.tab_layers_evap_rate_spin_var, width=10)
		self.tab_layers_evap_rate_spin.grid(row=2, column=1, sticky=W)
		self.tab_layers_evap_rate_spin_var.set(False)
				
		self.tab_layers_evap_rate_commit_but = Button(self.tab_layers_evap_conds_frame, text='Commit evaporation conditions to database', command=self.tab_layers_evap_conds_commit_conds)
		self.tab_layers_evap_rate_commit_but.grid(row=3, column=0, sticky=W)
		
		#####################################
		#############################################
		#################################################
		
		#####################################################
		#############################################
		#####################################
		self.tab_layers_sd_conds_frame = Labelframe(self.tab_layers_frame, text='Slot-Die Conditions')
		self.tab_layers_sd_conds_frame.grid(row=8, column=0, sticky=W)

		self.tab_layers_sd_name_label = Label(self.tab_layers_sd_conds_frame, text='Slot-die conditions name:')
		self.tab_layers_sd_name_label.grid(row=0, column=0, sticky=E)
		
		self.tab_layers_sd_name_entry_var = StringVar()
		self.tab_layers_sd_name_entry = Entry(self.tab_layers_sd_conds_frame, textvariable=self.tab_layers_sd_name_entry_var,width=100)
		self.tab_layers_sd_name_entry.grid(row=0, column=1, sticky=W,columnspan=10)

		self.tab_layers_coat_label = Label(self.tab_layers_sd_conds_frame, text='Coater:')
		self.tab_layers_coat_label.grid(row=1, column=0, sticky=E)
		
		self.tab_layers_coat_box_var = StringVar()
		self.tab_layers_coat_list = ['', 'Smartcoater', 'Bench Top Coater','FOM']
		self.tab_layers_coat_box = Combobox(self.tab_layers_sd_conds_frame, textvariable=self.tab_layers_coat_box_var, width=15)
		self.tab_layers_coat_box.bind('<<ComboboxSelected>>')
		self.tab_layers_coat_box['values'] = self.tab_layers_coat_list
		self.tab_layers_coat_box.grid(row=1, column=1, sticky=W)
		self.tab_layers_coat_box.state(['readonly'])

		self.tab_layers_sd_head_label = Label(self.tab_layers_sd_conds_frame, text='Slot-Die Head:')
		self.tab_layers_sd_head_label.grid(row=2, column=0, sticky=E)
		
		self.tab_layers_sd_head_box_var = StringVar()
		self.tab_layers_sd_head_list = []
		self.tab_layers_sd_head_box = Combobox(self.tab_layers_sd_conds_frame, textvariable=self.tab_layers_sd_head_box_var, width=15)
		self.tab_layers_sd_head_box.bind('<<ComboboxSelected>>', self.tab_layers_sd_mgs_update)
		self.tab_layers_sd_head_box['values'] = self.tab_layers_sd_head_list
		self.tab_layers_sd_head_box.grid(row=2, column=1, sticky=W)
		self.tab_layers_sd_head_box.state(['readonly'])
		self.tab_layers_sd_heads_update()
		
		self.tab_layers_sd_mg_label = Label(self.tab_layers_sd_conds_frame, text='Meniscus Guide:')
		self.tab_layers_sd_mg_label.grid(row=3, column=0, sticky=E)
		
		self.tab_layers_sd_mg_box_var = StringVar()
		self.tab_layers_sd_mg_list = []
		self.tab_layers_sd_mg_box = Combobox(self.tab_layers_sd_conds_frame, textvariable=self.tab_layers_sd_mg_box_var, width=15)
		self.tab_layers_sd_mg_box.bind('<<ComboboxSelected>>', self.tab_layers_sd_mg_box_update)
		self.tab_layers_sd_mg_box['values'] = self.tab_layers_sd_mg_list
		self.tab_layers_sd_mg_box.grid(row=3, column=1, sticky=W)
		self.tab_layers_sd_mg_box.state(['readonly'])
		
		self.tab_layers_sd_mg_wid_label = Label(self.tab_layers_sd_conds_frame, text='MG Coating Width:')
		self.tab_layers_sd_mg_wid_label.grid(row=3, column=2, sticky=E)
		
		self.tab_layers_sd_mg_wid_text_var = StringVar()
		self.tab_layers_sd_mg_wid_text = Spinbox(self.tab_layers_sd_conds_frame, textvariable=self.tab_layers_sd_mg_wid_text_var, width=10,state='readonly')
		self.tab_layers_sd_mg_wid_text.grid(row=3, column=3, sticky=W)
		self.tab_layers_sd_mg_wid_text_var.set(False)

		self.tab_layers_sd_mg_thick_label = Label(self.tab_layers_sd_conds_frame, text='MG Thickness:')
		self.tab_layers_sd_mg_thick_label.grid(row=3, column=4, sticky=E)
		
		self.tab_layers_sd_mg_thick_text_var = StringVar()
		self.tab_layers_sd_mg_thick_text = Spinbox(self.tab_layers_sd_conds_frame, textvariable=self.tab_layers_sd_mg_thick_text_var, width=10,state='readonly')
		self.tab_layers_sd_mg_thick_text.grid(row=3, column=5, sticky=W)
		self.tab_layers_sd_mg_thick_text_var.set(False)

		self.tab_layers_sd_mg_stripes_label = Label(self.tab_layers_sd_conds_frame, text='MG Stripes:')
		self.tab_layers_sd_mg_stripes_label.grid(row=3, column=6, sticky=E)
		
		self.tab_layers_sd_mg_stripes_var = StringVar()
		self.tab_layers_sd_mg_stripes = Spinbox(self.tab_layers_sd_conds_frame, textvariable=self.tab_layers_sd_mg_stripes_var, width=10,state='readonly')
		self.tab_layers_sd_mg_stripes.grid(row=3, column=7, sticky=W)
		self.tab_layers_sd_mg_stripes_var.set(False)

		self.tab_layers_sd_mg_tab_label = Label(self.tab_layers_sd_conds_frame, text='MG Tab Depth:')
		self.tab_layers_sd_mg_tab_label.grid(row=3, column=8, sticky=E)
		
		self.tab_layers_sd_mg_tab_var = StringVar()
		self.tab_layers_sd_mg_tab = Spinbox(self.tab_layers_sd_conds_frame, textvariable=self.tab_layers_sd_mg_tab_var, width=10,state='readonly')
		self.tab_layers_sd_mg_tab.grid(row=3, column=9, sticky=W)
		self.tab_layers_sd_mg_tab_var.set(False)
				
		self.tab_layers_sd_shim_label = Label(self.tab_layers_sd_conds_frame, text='Shim:')
		self.tab_layers_sd_shim_label.grid(row=4, column=0, sticky=E)
		
		self.tab_layers_sd_shim_box_var = StringVar()
		self.tab_layers_sd_shim_list = []
		self.tab_layers_sd_shim_box = Combobox(self.tab_layers_sd_conds_frame, textvariable=self.tab_layers_sd_shim_box_var, width=15)
		self.tab_layers_sd_shim_box.bind('<<ComboboxSelected>>', self.tab_layers_sd_shim_box_update)
		self.tab_layers_sd_shim_box['values'] = self.tab_layers_sd_shim_list
		self.tab_layers_sd_shim_box.grid(row=4, column=1, sticky=W)
		self.tab_layers_sd_shim_box.state(['readonly'])

		self.tab_layers_sd_shim_wid_label = Label(self.tab_layers_sd_conds_frame, text='Shim Coating Width:')
		self.tab_layers_sd_shim_wid_label.grid(row=4, column=2, sticky=E)
		
		self.tab_layers_sd_shim_wid_var = StringVar()
		self.tab_layers_sd_shim_wid = Spinbox(self.tab_layers_sd_conds_frame, textvariable=self.tab_layers_sd_shim_wid_var, width=10,state='readonly')
		self.tab_layers_sd_shim_wid.grid(row=4, column=3, sticky=W)
		self.tab_layers_sd_shim_wid_var.set(False)

		self.tab_layers_sd_shim_stripes_label = Label(self.tab_layers_sd_conds_frame, text='Shim Stripes:')
		self.tab_layers_sd_shim_stripes_label.grid(row=4, column=4, sticky=E)
		
		self.tab_layers_sd_shim_stripes_var = StringVar()
		self.tab_layers_sd_shim_stripes = Spinbox(self.tab_layers_sd_conds_frame, textvariable=self.tab_layers_sd_shim_stripes_var, width=10,state='readonly')
		self.tab_layers_sd_shim_stripes.grid(row=4, column=5, sticky=W)
		self.tab_layers_sd_shim_stripes_var.set(False)
		
		self.tab_layers_sd_shim_thick_label = Label(self.tab_layers_sd_conds_frame, text='Shim Thickness:')
		self.tab_layers_sd_shim_thick_label.grid(row=4, column=6, sticky=E)
		
		self.tab_layers_sd_shim_thick_var = StringVar()
		self.tab_layers_sd_shim_thick = Spinbox(self.tab_layers_sd_conds_frame, textvariable=self.tab_layers_sd_shim_thick_var, width=10,state='readonly')
		self.tab_layers_sd_shim_thick.grid(row=4, column=7, sticky=W)
		self.tab_layers_sd_shim_thick_var.set(False)
				
		self.tab_layers_sd_shim_num_label = Label(self.tab_layers_sd_conds_frame, text='Number of Shims:')
		self.tab_layers_sd_shim_num_label.grid(row=5, column=0, sticky=E)
		
		self.tab_layers_sd_shim_num_spin_var = StringVar()
		self.tab_layers_sd_shim_num_spin = Spinbox(self.tab_layers_sd_conds_frame, from_=1, to=100, increment=1, textvariable=self.tab_layers_sd_shim_num_spin_var, width=10)
		self.tab_layers_sd_shim_num_spin.grid(row=5, column=1, sticky=W)
		self.tab_layers_sd_shim_num_spin_var.set(1)

		self.tab_layers_sd_plat_label = Label(self.tab_layers_sd_conds_frame, text='Platten:')
		self.tab_layers_sd_plat_label.grid(row=6, column=0, sticky=E)
		
		self.tab_layers_sd_plat_box_var = StringVar()
		self.tab_layers_sd_plat_list = ['', 'Steel', 'Plastic',]
		self.tab_layers_sd_plat_box = Combobox(self.tab_layers_sd_conds_frame, textvariable=self.tab_layers_sd_plat_box_var, width=15)
		self.tab_layers_sd_plat_box.bind('<<ComboboxSelected>>')
		self.tab_layers_sd_plat_box['values'] = self.tab_layers_sd_plat_list
		self.tab_layers_sd_plat_box.grid(row=6, column=1, sticky=W)
		self.tab_layers_sd_plat_box.state(['readonly'])
		
		self.tab_layers_sd_plat_temp_label = Label(self.tab_layers_sd_conds_frame, text='Platten Temperature (degC):')
		self.tab_layers_sd_plat_temp_label.grid(row=6, column=2, sticky=E)
		
		self.tab_layers_sd_plat_temp_spin_var = StringVar()
		self.tab_layers_sd_plat_temp_spin = Spinbox(self.tab_layers_sd_conds_frame, from_=-200, to=9999, format="%.1f", increment=0.1, textvariable=self.tab_layers_sd_plat_temp_spin_var, width=10)
		self.tab_layers_sd_plat_temp_spin.grid(row=6, column=3, sticky=W)
		self.tab_layers_sd_plat_temp_spin_var.set(20.0)
			
		self.tab_layers_sd_rate_label = Label(self.tab_layers_sd_conds_frame, text='Pump rate (ml/min):')
		self.tab_layers_sd_rate_label.grid(row=7, column=0, sticky=E)
		
		self.tab_layers_sd_rate_spin_var = StringVar()
		self.tab_layers_sd_rate_spin = Spinbox(self.tab_layers_sd_conds_frame, from_=0, to=9999, format="%.1f", increment=0.1, textvariable=self.tab_layers_sd_rate_spin_var, width=10)
		self.tab_layers_sd_rate_spin.grid(row=7, column=1, sticky=W)
		self.tab_layers_sd_rate_spin_var.set(False)

		self.tab_layers_sd_web_label = Label(self.tab_layers_sd_conds_frame, text='Coating Speed (m/min):')
		self.tab_layers_sd_web_label.grid(row=8, column=0, sticky=E)
		
		self.tab_layers_sd_web_spin_var = StringVar()
		self.tab_layers_sd_web_spin = Spinbox(self.tab_layers_sd_conds_frame, from_=0, to=9999, format="%.1f", increment=0.1, textvariable=self.tab_layers_sd_web_spin_var, width=10)
		self.tab_layers_sd_web_spin.grid(row=8, column=1, sticky=W)
		self.tab_layers_sd_web_spin_var.set(False)
		
		self.tab_layers_sd_ink_temp_label = Label(self.tab_layers_sd_conds_frame, text='Ink Temperature (degC):')
		self.tab_layers_sd_ink_temp_label.grid(row=9, column=0, sticky=E)
		
		self.tab_layers_sd_ink_temp_spin_var = StringVar()
		self.tab_layers_sd_ink_temp_spin = Spinbox(self.tab_layers_sd_conds_frame, from_=-200, to=9999, format="%.1f", increment=0.1, textvariable=self.tab_layers_sd_ink_temp_spin_var, width=10)
		self.tab_layers_sd_ink_temp_spin.grid(row=9, column=1, sticky=W)
		self.tab_layers_sd_ink_temp_spin_var.set(20.0)

		self.tab_layers_sd_head_temp_label = Label(self.tab_layers_sd_conds_frame, text='Head Temperature (degC):')
		self.tab_layers_sd_head_temp_label.grid(row=10, column=0, sticky=E)
		
		self.tab_layers_sd_head_temp_spin_var = StringVar()
		self.tab_layers_sd_head_temp_spin = Spinbox(self.tab_layers_sd_conds_frame, from_=-200, to=9999, format="%.1f", increment=0.1, textvariable=self.tab_layers_sd_head_temp_spin_var, width=10)
		self.tab_layers_sd_head_temp_spin.grid(row=10, column=1, sticky=W)
		self.tab_layers_sd_head_temp_spin_var.set(20.0)
				
		self.tab_layers_sd_height_label = Label(self.tab_layers_sd_conds_frame, text='Head Offset (micron):')
		self.tab_layers_sd_height_label.grid(row=11, column=0, sticky=E)
		
		self.tab_layers_sd_height_spin_var = StringVar()
		self.tab_layers_sd_height_spin = Spinbox(self.tab_layers_sd_conds_frame, from_=0, to=999999, format="%.1f", increment=0.1, textvariable=self.tab_layers_sd_height_spin_var, width=10)
		self.tab_layers_sd_height_spin.grid(row=11, column=1, sticky=W)
		self.tab_layers_sd_height_spin_var.set(False)
		
		self.tab_layers_sd_angle_label = Label(self.tab_layers_sd_conds_frame, text='Head Angle (Degrees):')
		self.tab_layers_sd_angle_label.grid(row=12, column=0, sticky=E)
		
		self.tab_layers_sd_angle_spin_var = StringVar()
		self.tab_layers_sd_angle_spin = Spinbox(self.tab_layers_sd_conds_frame, from_=-180, to=180, format="%.1f", increment=0.1, textvariable=self.tab_layers_sd_angle_spin_var, width=10)
		self.tab_layers_sd_angle_spin.grid(row=12, column=1, sticky=W)
		self.tab_layers_sd_angle_spin_var.set(False)
		
		self.tab_layers_sd_sub_temp_label = Label(self.tab_layers_sd_conds_frame, text='Substrate Temperature (degC):')
		self.tab_layers_sd_sub_temp_label.grid(row=13, column=0, sticky=E)
		
		self.tab_layers_sd_sub_temp_spin_var = StringVar()
		self.tab_layers_sd_sub_temp_spin = Spinbox(self.tab_layers_sd_conds_frame, from_=-200, to=9999, format="%.1f", increment=0.1, textvariable=self.tab_layers_sd_sub_temp_spin_var, width=10)
		self.tab_layers_sd_sub_temp_spin.grid(row=13, column=1, sticky=W)
		self.tab_layers_sd_sub_temp_spin_var.set(20.0)
		
		self.tab_layers_sd_pre_delay_label = Label(self.tab_layers_sd_conds_frame, text='Pre-Coat Delay (s):')
		self.tab_layers_sd_pre_delay_label.grid(row=14, column=0, sticky=E)
		
		self.tab_layers_sd_pre_delay_spin_var = StringVar()
		self.tab_layers_sd_pre_delay_spin = Spinbox(self.tab_layers_sd_conds_frame, from_=0, to=999999, format="%.1f", increment=0.1, textvariable=self.tab_layers_sd_pre_delay_spin_var, width=10)
		self.tab_layers_sd_pre_delay_spin.grid(row=14, column=1, sticky=W)
		self.tab_layers_sd_pre_delay_spin_var.set(False)
		
		self.tab_layers_sd_pre_coat_delay_label = Label(self.tab_layers_sd_conds_frame, text='Pre-Coat Pump Delay (s):')
		self.tab_layers_sd_pre_coat_delay_label.grid(row=15, column=0, sticky=E)
		
		self.tab_layers_sd_pre_coat_delay_spin_var = StringVar()
		self.tab_layers_sd_pre_coat_delay_spin = Spinbox(self.tab_layers_sd_conds_frame, from_=0, to=999999, format="%.1f", increment=0.1, textvariable=self.tab_layers_sd_pre_coat_delay_spin_var, width=10)
		self.tab_layers_sd_pre_coat_delay_spin.grid(row=15, column=1, sticky=W)
		self.tab_layers_sd_pre_coat_delay_spin_var.set(False)
		
		self.tab_layers_sd_pump_delay_label = Label(self.tab_layers_sd_conds_frame, text='Pump Delay (s):')
		self.tab_layers_sd_pump_delay_label.grid(row=16, column=0, sticky=E)
		
		self.tab_layers_sd_pump_delay_spin_var = StringVar()
		self.tab_layers_sd_pump_delay_spin = Spinbox(self.tab_layers_sd_conds_frame, from_=0, to=999999, format="%.1f", increment=0.1, textvariable=self.tab_layers_sd_pump_delay_spin_var, width=10)
		self.tab_layers_sd_pump_delay_spin.grid(row=16, column=1, sticky=W)
		self.tab_layers_sd_pump_delay_spin_var.set(False)
		
		self.tab_layers_sd_web_ten_label = Label(self.tab_layers_sd_conds_frame, text='Web Tension (N):')
		self.tab_layers_sd_web_ten_label.grid(row=17, column=0, sticky=E)
		
		self.tab_layers_sd_web_ten_spin_var = StringVar()
		self.tab_layers_sd_web_ten_spin = Spinbox(self.tab_layers_sd_conds_frame, from_=0, to=999999, format="%.1f", increment=0.1, textvariable=self.tab_layers_sd_web_ten_spin_var, width=10)
		self.tab_layers_sd_web_ten_spin.grid(row=17, column=1, sticky=W)
		self.tab_layers_sd_web_ten_spin_var.set(False)
		
		self.tab_layers_sd_commit_but = Button(self.tab_layers_sd_conds_frame, text='Commit slot-die conditions to database', command=self.tab_layers_sd_conds_commit_conds)
		self.tab_layers_sd_commit_but.grid(row=18, column=0, sticky=W)
	
	def mark_layer_complete(self, *args):
		#Get the layer name and id and find the state
		#Convert the name to an id...
		id_result = self.select_one_thing('id', 'layers', 'layer_name', self.tab_layers_name_box.get())
		#Find the current state of layer
		if str(id_result):
			layer_state = self.select_many_things_where('state', 'layers', 'id', id_result)
			
			if layer_state == 1:
				state = 0
			else:
				state = 1
			
			self.conn.execute('UPDATE layers SET state = ? WHERE id = ?',(state, id_result,));
			self.conn.commit()
			
			self.update_layers_layer_combo_box()
			
		
		
	def layer_get_colour(self, *args):
		color = askcolor() 
		layer_colour = color[1]
		if layer_colour == None:
			layer_colour = "#FFFFFF"
		
		self.tab_layers_picture_canvas.itemconfig(self.tab_layers_picture_canvas_rec, fill=layer_colour)
		#self.tab_layers_picture_canvas.create_rectangle(0, 0, 150, 50, fill=layer_colour)
		#self.tab_layers_picture_canvas.create_text(10, 10, text="Layer Colour",width=60,anchor=NW)
		self.tab_layers_colour_entry_var.set(layer_colour)
		
		#print self.tab_layers_colour_entry_var.get()
		
	def commit_layer(self, *args):
		##### find if the layer name exists already #####
		tab_layers_layer_already_exists = self.conn.execute('SELECT layer_name FROM layers WHERE layer_name = ?', (self.tab_layers_name_box.get(),))
		tab_layers_layer_already_exists_results = tab_layers_layer_already_exists.fetchall()
		
		if tab_layers_layer_already_exists_results:
			self.tab_layers_layer_status_label_var.set('Layer name exists already, rename and try again.')
		else:	
			#To update layers table a form_id, dep_id, layer_name, layer_type, thickness and colour are needed
			###### Get the form_id from the formulations table and its name ########
			tab_layers_form_id_select = self.conn.execute('SELECT form_id FROM formulations WHERE form_name = ?', (self.tab_layers_form_box.get(),))
			tab_layers_form_id_select_result = tab_layers_form_id_select.fetchone()[0]
			
			#####Get the dep_id from the depositions table- this needs the dep_met and dep_conds ids
			#Get the dep_met id
			dep_met_id_select = self.conn.execute('SELECT id FROM dep_methods WHERE dep_name = ?', (self.tab_layers_dep_box.get(),))
			dep_met_id_select_result = dep_met_id_select.fetchone()[0]
			#Make sure something has been selected?
			#Get the dep_conds from the deposition_conds table and the name from drop down
			#Just select the first as all others should be other stages in same set
			
			
			dep_conds_id_select = self.conn.execute('SELECT dep_conds_id FROM deposition_conds WHERE name = ?', (self.tab_layers_cond_box.get(),))
			dep_conds_id_select_result = dep_conds_id_select.fetchone()[0]
			
			
			#Get the depositions id from the method and conditions
			#What is it doesn't exist e.g. None on the drop down?		
			tab_layer_dep_conds_id_exists = self.conn.execute('SELECT id FROM depositions WHERE dep_met = ? AND dep_conds = ?', (dep_met_id_select_result,dep_conds_id_select_result,))
			tab_layer_dep_conds_id_exists_result = tab_layer_dep_conds_id_exists.fetchone()[0]
			
			#Get the layer type id
			
			tab_layer_type_id_exists = self.conn.execute('SELECT id FROM layer_types WHERE layer_type = ?', (self.tab_layers_type_box.get(),))
			tab_layer_type_id_exists_result = tab_layer_type_id_exists.fetchone()[0]
			
			layer_inputs_dict = { 'layer_name':self.tab_layers_name_box.get(),
						'dep_id':tab_layer_dep_conds_id_exists_result,
						'layer_type':tab_layer_type_id_exists_result,
						'form_id':tab_layers_form_id_select_result,
						'layer_thickness':self.tab_layers_spin_thick.get(),
						'layer_colour':self.tab_layers_colour_entry_var.get(),
						'state':0,
						}
			
			function_name = 'layers'		
			layer_inputs_inserted = self.materials_mod(self, layer_inputs_dict, function_name, self.conn)	
			self.tab_layers_layer_status_label_var.set(layer_inputs_inserted[1])
			self.update_layers_layer_combo_box()		
			self.tab_layers_dep_conds_update()
	
	def tab_layers_sd_mg_box_update(self, *args):
		#Get the mg name and set the parameters
		x_id = self.conn.execute('SELECT stripes FROM mgs WHERE mg_name = ?', (self.tab_layers_sd_mg_box.get(),))
		x_id_result = x_id.fetchone()[0]
		if x_id_result:
			self.tab_layers_sd_mg_stripes_var.set(x_id_result)
		else:
			self.tab_layers_sd_mg_stripes_var.set('')
			
		x_id = self.conn.execute('SELECT width FROM mgs WHERE mg_name = ?', (self.tab_layers_sd_mg_box.get(),))
		x_id_result = x_id.fetchone()[0]
		if x_id_result:
			self.tab_layers_sd_mg_wid_text_var.set(x_id_result)
		else:
			self.tab_layers_sd_mg_wid_text_var.set('')
		
		x_id = self.conn.execute('SELECT thickness FROM mgs WHERE mg_name = ?', (self.tab_layers_sd_mg_box.get(),))
		x_id_result = x_id.fetchone()[0]
		if x_id_result:
			self.tab_layers_sd_mg_thick_text_var.set(x_id_result)
		else:
			self.tab_layers_sd_mg_thick_text_var.set('')	
			
		x_id = self.conn.execute('SELECT tab_length FROM mgs WHERE mg_name = ?', (self.tab_layers_sd_mg_box.get(),))
		x_id_result = x_id.fetchone()[0]
		if x_id_result:
			self.tab_layers_sd_mg_tab_var.set(x_id_result)
		else:
			self.tab_layers_sd_mg_tab_var.set('')
	
	def tab_layers_sd_shim_box_update(self, *args):
		#Get the mg name and set the parameters
		x_id = self.conn.execute('SELECT stripes FROM shims WHERE shim_name = ?', (self.tab_layers_sd_shim_box.get(),))
		x_id_result = x_id.fetchone()[0]
		if x_id_result:
			self.tab_layers_sd_shim_stripes_var.set(x_id_result)
		else:
			self.tab_layers_sd_shim_stripes_var.set('')
			
		x_id = self.conn.execute('SELECT width FROM shims WHERE shim_name = ?', (self.tab_layers_sd_shim_box.get(),))
		x_id_result = x_id.fetchone()[0]
		if x_id_result:
			self.tab_layers_sd_shim_wid_var.set(x_id_result)
		else:
			self.tab_layers_sd_shim_wid_var.set('')
		
		x_id = self.conn.execute('SELECT thickness FROM shims WHERE shim_name = ?', (self.tab_layers_sd_shim_box.get(),))
		x_id_result = x_id.fetchone()[0]
		if x_id_result:
			self.tab_layers_sd_shim_thick_var.set(x_id_result)
		else:
			self.tab_layers_sd_shim_thick_var.set('')	
			
						
	def tab_layers_sd_mgs_update(self, *args):
		self.tab_layers_sd_mg_list = []
		self.tab_layers_sd_shim_list = []
		self.tab_layers_sd_mg_box.set('')
		self.tab_layers_sd_shim_box.set('')
		self.tab_layers_sd_mg_tab_var.set('')
		self.tab_layers_sd_mg_thick_text_var.set('')
		self.tab_layers_sd_mg_wid_text_var.set('')
		self.tab_layers_sd_mg_stripes_var.set('')
		self.tab_layers_sd_shim_thick_var.set('')
		self.tab_layers_sd_shim_wid_var.set('')	
		self.tab_layers_sd_shim_stripes_var.set('')
		#get the current head name from list box and use to find corresponding guides
		mg_id = self.conn.execute('SELECT mg_name FROM mgs WHERE sd_head_name = ?', (self.tab_layers_sd_head_box.get(),))
		mg_id_result = mg_id.fetchall()
		if mg_id_result:
			for i in mg_id_result:
				self.tab_layers_sd_mg_list.append(i[0])
		self.tab_layers_sd_mg_box['values'] = list(self.tab_layers_sd_mg_list)	
		#And for shims too
		sh_id = self.conn.execute('SELECT shim_name FROM shims WHERE sd_head_name = ?', (self.tab_layers_sd_head_box.get(),))
		sh_id_result = sh_id.fetchall()
		if sh_id_result:
			for i in sh_id_result:
				self.tab_layers_sd_shim_list.append(i[0])
		self.tab_layers_sd_shim_box['values'] = list(self.tab_layers_sd_shim_list)
	def tab_layers_sd_heads_update(self, *args):
		self.tab_layers_sd_head_list = []
		self.tab_layers_sd_mg_list = []
		self.tab_layers_sd_shim_list = []
		#Read the sd head names from the database
		head_id = self.conn.execute('SELECT sd_head_name FROM sd_heads')
		head_id_result = head_id.fetchall()
		if head_id_result:
			for i in head_id_result:
				self.tab_layers_sd_head_list.append(i[0])
		self.tab_layers_sd_head_box['values'] = list(self.tab_layers_sd_head_list)
			
	def update_layers_layer_combo_box(self, *args):
		self.tab_layers_name_list = []
		self.tab_layers_name_box.set('')
		#Get the state of used/unused
		if self.tab_layer_check_var_complete.get() == True:
			state = 1
		else:
			state = 0
		## get the id of the material ###
		if self.tab_layers_type_box.get() == "Any":
			tab_layers_layer_type_name_select_results = self.select_many_things_where('layer_name', 'layers', 'state', state)

		else:	
			#Convert the name to an id...
			type_id_result = self.select_one_thing('id', 'layer_types', 'layer_type', self.tab_layers_type_box.get())

			tab_layers_layer_type_name_select_results = self.select_many_things_where_two('layer_name', 'layers', 'layer_type', 'state', type_id_result, state)
				
		if tab_layers_layer_type_name_select_results:
			for i in tab_layers_layer_type_name_select_results:
				if i[0]:
					self.tab_layers_name_list.append(i[0])
		self.tab_layers_name_box['values'] = list(reversed(self.tab_layers_name_list))	
	
	def select_one_thing(self, selection, table, column, cond):
		#If there is nothing selected need to say
		x = self.conn.execute('SELECT '+selection+' FROM '+table+' WHERE '+column+' = ?', (cond,))
		xx = x.fetchone()[0]
		if xx is None:
			print 'one thing xx is None'	
		return xx
	
	def select_many_things(self, selection, table):
		x = self.conn.execute('SELECT '+selection+' FROM '+table+'')
		xx = x.fetchall()
		#This returns a list
		#What if the selection didn't run correctly?
		#Should there be a default to return?
		if xx is None:
			print 'many things xx is None'	
		return xx
		
	def select_many_things_where(self, selection, table, column, cond):
		x = self.conn.execute('SELECT '+selection+' FROM '+table+' WHERE '+column+' = ?', (cond,))
		xx = x.fetchall()
		#This returns a list
		#What if the selection didn't run correctly?
		#Should there be a default to return?
		if xx is None:
			print 'many things xx is None'	
		return xx
	
	def select_many_things_where_two(self, selection, table, column, column1, cond, cond1):
		x = self.conn.execute('SELECT '+selection+' FROM '+table+' WHERE '+column+' = ? AND '+column1+' = ?', (cond,cond1))
		xx = x.fetchall()
		#This returns a list
		#What if the selection didn't run correctly?
		#Should there be a default to return?
		if xx is None:
			print 'many things xx is None'	
		return xx
		
	def tab_layers_sd_conds_commit_conds(self, *args):
		dep_met_id_select_result = self.select_one_thing('id', 'dep_methods', 'dep_name', 'Slot-Die Coating')
		cond_lst = []
		conds_dict = {
					'name':self.tab_layers_sd_name_entry.get(),
					'sd_coater':self.tab_layers_coat_box.get(),
					'sd_head':self.tab_layers_sd_head_box.get(),
					'shim':self.tab_layers_sd_shim_box.get(),
					'shim_num':self.tab_layers_sd_shim_num_spin.get(),
					'mg':self.tab_layers_sd_mg_box.get(),
					'platten':self.tab_layers_sd_plat_box.get(),
					'plat_temp':self.tab_layers_sd_plat_temp_spin.get(),
					'sd_soln_temp':self.tab_layers_sd_ink_temp_spin.get(),
					'sd_sub_temp':self.tab_layers_sd_sub_temp_spin.get(),
					'gap_height':self.tab_layers_sd_height_spin.get(),
					'angle':self.tab_layers_sd_angle_spin.get(),
					'speed':self.tab_layers_sd_web_spin.get(),
					'flow_rate':self.tab_layers_sd_rate_spin.get(),
					'pre_coat_delay':self.tab_layers_sd_pre_delay_spin.get(),
					'pre_coat_pump_delay':self.tab_layers_sd_pre_coat_delay_spin.get(),
					'pump_delay':self.tab_layers_sd_pump_delay_spin.get(),
					'web_tension':self.tab_layers_sd_web_ten_spin.get(),
					}
		cond_lst.append(conds_dict)	
		function_name = 'deposition_conds'
		other_col = 'dep_conds_id'
		other_table = 'depositions'
		method_col = 'dep_met'
		conds_col = 'dep_conds'  
		name_col = 'name'
		name = '%s' % self.tab_layers_sd_name_entry.get()			
		conds_inserted = self.dep_conds_mod(self, cond_lst, dep_met_id_select_result, function_name, self.conn, other_col, other_table, method_col, conds_col, name_col, name)
		
	def tab_layers_bar_conds_commit_conds(self, *args):
		dep_met_id_select_result = self.select_one_thing('id', 'dep_methods', 'dep_name', 'Bar Coating')
		cond_lst = []
		conds_dict = {
					'name':self.tab_layers_bar_name_entry.get(),
					'bar_quan':self.tab_layers_bar_quan_spin.get(),
					'bar_temp':self.tab_layers_bar_sol_temp_spin.get(),
					'bar_sub_temp':self.tab_layers_bar_sub_temp_spin.get(),
					'bed_temp':self.tab_layers_bar_bed_temp_spin.get(),
					'bar_speed_m_min':self.tab_layers_bar_speed_spin.get(),
					'bar_size_um':self.tab_layers_bar_size_spin.get(),
					'bar_atm_id':self.tab_layers_bar_atm_box.current(),
					}

		cond_lst.append(conds_dict)	
		function_name = 'deposition_conds'
		other_col = 'dep_conds_id'
		other_table = 'depositions'
		method_col = 'dep_met'
		conds_col = 'dep_conds'  
		name_col = 'name'
		name = '%s' % self.tab_layers_bar_name_entry.get()			
		conds_inserted = self.dep_conds_mod(self, cond_lst, dep_met_id_select_result, function_name, self.conn, other_col, other_table, method_col, conds_col, name_col, name)
		
	def tab_layers_evap_conds_commit_conds(self,*args):
		dep_met_id_select_result = self.select_one_thing('id', 'dep_methods', 'dep_name', 'Evaporation')

		cond_lst = []
		conds_dict = {
					'name':self.tab_layers_evap_name_entry.get(),
					'evap_rate':self.tab_layers_evap_rate_spin.get(),
					'evaporator':self.tab_layers_evap_box.current(),
					}	
		cond_lst.append(conds_dict)	
		function_name = 'deposition_conds'
		other_col = 'dep_conds_id'
		other_table = 'depositions'
		method_col = 'dep_met'
		conds_col = 'dep_conds'  
		name_col = 'name'
		name = '%s' % self.tab_layers_evap_name_entry.get()
		conds_inserted = self.dep_conds_mod(self, cond_lst, dep_met_id_select_result, function_name, self.conn, other_col, other_table, method_col, conds_col, name_col, name)
		
	def tab_layers_dip_conds_commit_conds(self, *args):
		dep_met_id_select_result = self.select_one_thing('id', 'dep_methods', 'dep_name', 'Dip Coating')
		cond_lst = []
		conds_dict = {
					'name':self.tab_layers_dip_name_entry.get(),
					'dip_quan':self.tab_layers_dip_quan_spin.get(),
					'dip_temp':self.tab_layers_dip_sol_temp_spin.get(),
					'dip_sub_temp':self.tab_layers_dip_sub_temp_spin.get(),
					'dip_time':self.tab_layers_dip_time_spin.get(),
					'dip_agi':self.tab_layers_dip_agi_check_var.get(),
					}	
		cond_lst.append(conds_dict)	
		function_name = 'deposition_conds'
		other_col = 'dep_conds_id'
		other_table = 'depositions'
		method_col = 'dep_met'
		conds_col = 'dep_conds'  
		name_col = 'name'
		name = '%s' % self.tab_layers_dip_name_entry.get()		
		conds_inserted = self.dep_conds_mod(self, cond_lst, dep_met_id_select_result, function_name, self.conn, other_col, other_table, method_col, conds_col, name_col, name)
		#Why is this here?
	def tab_layers_spray_conds_commit_conds(self, *args):
		dep_met_id_select_result = self.select_one_thing('id', 'dep_methods', 'dep_name', 'Spray Coating')
		cond_lst = []
		conds_dict = {
					'name':self.tab_layers_spray_name_entry.get(),
					'spray_gun_id':self.tab_layers_spray_gun_box.current(),
					'distance':self.tab_layers_spray_dist_spin.get(),
					'spray_sub_temp':self.tab_layers_spray_temp_spin.get(),
					'passes':self.tab_layers_spray_pass_spin.get(),
					'spray_pressure':self.tab_layers_spray_pres_spin.get(),
					'spray_vol':self.tab_layers_spray_vol_spin.get(),
					'feed_gas_id':self.tab_layers_spray_gas_box.current(),
					'spray_atm_id':self.tab_layers_spray_atm_box.current(),
					'spray_screw':self.tab_layers_spray_set_spin.get(),
					}	
		cond_lst.append(conds_dict)	
		function_name = 'deposition_conds'
		other_col = 'dep_conds_id'
		other_table = 'depositions'
		method_col = 'dep_met'
		conds_col = 'dep_conds'  
		name_col = 'name'
		name = '%s' % self.tab_layers_spray_name_entry.get()	
		conds_inserted = self.dep_conds_mod(self, cond_lst, dep_met_id_select_result, function_name, self.conn, other_col, other_table, method_col, conds_col, name_col, name)
		
	def tab_layers_spin_conds_commit_conds(self, *args):
		dep_met_id_select_result = self.select_one_thing('id', 'dep_methods', 'dep_name', 'Spin Coating')
		cond_lst = []
		#we should test if this has actually been filled in or not
		#The same dep_conds_id needs to be kept for each row...	
		for index, i in enumerate(self.tab_layers_spin_speed_listbox.get(0, END)):

			conds_dict = {
					'spin_coater_id':self.tab_layers_spin_id_box.current(),
					'temp':self.tab_layers_spin_spin_temp.get(),
					'delay':self.tab_layers_spin_spin_delay.get(),
					'spin_atm':self.tab_layers_spin_atm_box.current(),
					'name':self.tab_layers_spin_dep_name_entry.get(),
					'drip_vol':self.tab_layers_spin_drip_quan_var.get(),
					'drip_time':self.tab_layers_spin_drip_time_var.get(),
					'drip_sol':self.tab_layers_spin_drip_sol_box.get(),
					'spin_vol':self.tab_layers_spin_spin_vol_var.get(),
					'spin_soln_temp':self.tab_layers_spin_spin_soln_temp_var.get(),
					'spin_speed':i,
					'spin_acc':self.tab_layers_spin_acc_listbox.get(index),
					'time':self.tab_layers_spin_time_listbox.get(index),
					}
			cond_lst.append(conds_dict)	
			function_name = 'deposition_conds'
			other_col = 'dep_conds_id'
			other_table = 'depositions'
			method_col = 'dep_met'
			conds_col = 'dep_conds'  
			name_col = 'name'
			name = '%s' % self.tab_layers_spin_dep_name_entry.get()
			function_name = 'deposition_conds'		
		conds_inserted = dep_conds_mod(self, cond_lst, dep_met_id_select_result, function_name, self.conn, other_col, other_table, method_col, conds_col, name_col, name)
		
					
	def tab_layers_spin_conds_add_stage(self, *args):
		self.spin_speed_input = self.tab_layers_spin_spin_speed.get()
		self.spin_acc_input = self.tab_layers_spin_spin_acc.get()
		self.spin_time_input = self.tab_layers_spin_spin_time.get()
		
		if self.spin_speed_input and self.spin_acc_input and self.spin_time_input:
			self.tab_layers_spin_speed_listbox.insert(END, self.spin_speed_input)
			self.tab_layers_spin_acc_listbox.insert(END, self.spin_acc_input)
			self.tab_layers_spin_time_listbox.insert(END, self.spin_time_input)
			
	def tab_layers_spin_conds_remove_stage(self, *args):
		items = map(int, self.tab_layers_spin_speed_listbox.curselection())
		for i in items:
			self.tab_layers_spin_speed_listbox.delete(i)
			self.tab_layers_spin_acc_listbox.delete(i)
			self.tab_layers_spin_time_listbox.delete(i)		
			
	def tab_layers_spin_dep_conds_speed_list_selection(self, *args):
		items = map(int, self.tab_layers_spin_speed_listbox.curselection())
		self.tab_layers_spin_acc_listbox.selection_clear(first=0, last=END)
		self.tab_layers_spin_time_listbox.selection_clear(first=0, last=END)
		for i in items:
			self.tab_layers_spin_acc_listbox.select_set(i)
			self.tab_layers_spin_time_listbox.select_set(i)
	
	def tab_layers_spin_dep_conds_acc_list_selection(self, *args):
		items = map(int, self.tab_layers_spin_acc_listbox.curselection())
		self.tab_layers_spin_speed_listbox.selection_clear(first=0, last=END)
		self.tab_layers_spin_time_listbox.selection_clear(first=0, last=END)
		for i in items:
			self.tab_layers_spin_speed_listbox.select_set(i)
			self.tab_layers_spin_time_listbox.select_set(i)		
			
	def tab_layers_spin_dep_conds_time_list_selection(self, *args):
		items = map(int, self.tab_layers_spin_time_listbox.curselection())
		self.tab_layers_spin_acc_listbox.selection_clear(first=0, last=END)
		self.tab_layers_spin_speed_listbox.selection_clear(first=0, last=END)
		for i in items:
			self.tab_layers_spin_acc_listbox.select_set(i)
			self.tab_layers_spin_speed_listbox.select_set(i)		
	def tab_layers_dep_conds_update(self, *args):
		self.tab_layers_all_conds_update_inputs()
				
	def tab_layers_update_previous(self, *args):
		#get the layer name selected from the combobox
		layer_selected = self.tab_layers_name_box.get()	
		#poll the database for the id of that layer_name
		layer_select = self.conn.execute('SELECT id FROM layers WHERE layer_name = ?', (layer_selected,))
		layer_select_id = layer_select.fetchone()[0]
		
		#### get the thickness for that layer id and set the spinbox #####
		layer_select_thick = self.conn.execute('SELECT layer_thickness FROM layers WHERE id = ?', (layer_select_id,))
		layer_select_thick_result = layer_select_thick.fetchone()[0]
		
		if layer_select_thick_result:
			self.tab_layers_spin_thick_var.set(layer_select_thick_result)
		else:
			self.tab_layers_spin_thick_var.set(False)	
		#### select the formulation id for that id and set the combo ######
		self.tab_layers_form_label_var.set(False)
		layer_form_id_exists = self.conn.execute('SELECT form_id FROM layers WHERE id = ?', (layer_select_id,))
		layer_form_id_exists_result = layer_form_id_exists.fetchone()[0]
		#### from formulations select the formulation name with that form_id ####
		#Multiple formulations row ids have one form_id, just selecting the first should be fine
		layer_form_exists = self.conn.execute('SELECT form_name FROM formulations WHERE form_id = ?', (layer_form_id_exists_result,))
		layer_form_exists_result = layer_form_exists.fetchone()[0]
		##### If the common name exists set the formulation name as it or to false if not####
		if layer_form_exists_result:
			self.tab_layers_form_box.set(layer_form_exists_result)
		else:
			self.tab_layers_form_box.set(False)
		
		####Get the layer colour
		layer_col_exists = self.conn.execute('SELECT layer_colour FROM layers WHERE id = ?', (layer_select_id,))
		layer_col_exists_result = layer_col_exists.fetchone()[0]
		
		if layer_col_exists_result:
			self.tab_layers_colour_entry_var.set(str(layer_col_exists_result))
			self.tab_layers_picture_canvas.itemconfig(self.tab_layers_picture_canvas_rec, fill=str(layer_col_exists_result))
		else:
			self.tab_layers_colour_entry_var.set('#FFFFFF')
			self.tab_layers_picture_canvas.itemconfig(self.tab_layers_picture_canvas_rec, fill='#FFFFFF')
		### select the deposition method id and set the combo #####
		self.tab_layers_dep_label_var.set(False)
		layer_dep_id_exists = self.conn.execute('SELECT dep_id FROM layers WHERE id = ?', (layer_select_id,))
		layer_dep_id_exists_result = layer_dep_id_exists.fetchone()[0]
		
		
		#Use the dep_id to get the dep_met and dep_conds from the depositions table
		#Get the id for the depositions and then use to select the deposition_conds and select in the box and update
		#first get the the depositions id
		layer_dep_met_exists = self.conn.execute('SELECT dep_met FROM depositions WHERE id = ?', (layer_dep_id_exists_result,))
		layer_dep_met_exists_result = layer_dep_met_exists.fetchone()[0]
		
		##### Each dep_met id corresponds to a method in the dep_met list, set to the correct one or None ####
		if layer_dep_met_exists_result:
			self.tab_layers_dep_box.current(layer_dep_met_exists_result)
		else:
			self.tab_layers_dep_box.current(0)
		
		#dep_cond_id_exists = self.conn.execute('SELECT dep_conds FROM depositions WHERE id = ?', (layer_dep_id_exists_result,))
		#dep_cond_id_exists_result = dep_cond_id_exists.fetchone()[0]
		#print dep_cond_id_exists_result
		#Use the id to get the name and add that to the conds box
		cond_name_select = self.conn.execute('SELECT name FROM depositions WHERE id = ?', (layer_dep_id_exists_result,))
		cond_name_select_results = cond_name_select.fetchone()[0]
		
		if cond_name_select_results:
			self.tab_layers_cond_box.set(cond_name_select_results)
		else:
			self.tab_layers_cond_box.set(False)
		
		#update the conditions ,uses the name?	
		self.tab_layers_all_conds_update_inputs()	
			
	def tab_layers_all_conds_update_inputs(self,*args):
		###Replace all this with a dict and loop
		#dicts_lst = [
		#{'type':'one', 'selection':'layer_thickness', 'table':'layers', 'column':'id','cond':layer_select_id, 'var_type':'set','variable':self.tab_layers_spin_thick_var},
		#{'type':'one', 'selection':'form_id', 'table':'layers', 'column':'id','cond':layer_select_id, 'var_type':'set','variable':self.tab_layers_spin_thick_var},
		#]
		#for i in dicts_lst:
			#print i
			#if i['type'] == 'one':
				#x = self.select_one_thing(i['selection'],i['table'],i['column'],i['cond'])
				#if x:
					#if i['var_type'] == 'set':
						#i['variable'].set(x)
					#elif i['var_type'] == 'current':
						#i['variable'].current(x)
				#else:
					#if i['var_type'] == 'set':
						#i['variable'].set(False)
					#elif i['var_type'] == 'current':
						#i['variable'].current(0)
		##### get the deposition name #########
		#Not sure if this works ok?
		if not self.tab_layers_cond_box.get():
			layer_cond_name = "None"
		else:
			layer_cond_name = self.tab_layers_cond_box.get()
		
		
		#This just doesn't make any sense...
		#There is a name for the conditions in the box
		#This relates to an a depositions id (or a deposition_conds id)
		#Need to select all the entys for the deposition_cond and update
		dep_cond_id_select = self.conn.execute('SELECT id FROM depositions WHERE name = ?', (layer_cond_name,))
		dep_cond_id_exists_result = dep_cond_id_select.fetchone()[0]
		
		#Why o why- these should match anyway... but just incase...
		cond_name_select = self.conn.execute('SELECT name FROM depositions WHERE id = ?', (dep_cond_id_exists_result,))
		cond_name_select_results = cond_name_select.fetchone()[0]
		
		
		#clear all the boxes first
		self.tab_layers_evap_name_entry_var.set('')
		self.tab_layers_sd_name_entry_var.set('')
		self.tab_layers_bar_name_entry_var.set('')
		self.tab_layers_dip_name_entry_var.set('')
		self.tab_layers_spray_name_entry_var.set('')
		self.tab_layers_spin_dep_name_entry_var.set('')
		
		if cond_name_select_results:
			#Get the dep_conds id for the depositon (common to many rows in deposition_conds)
			dc = self.conn.execute('SELECT dep_conds FROM depositions WHERE id = ?', (dep_cond_id_exists_result,))
			dc_result = dc.fetchone()[0]
			print 'This is dc_result %s' % dc_result
			#Get the id of a row with that dep_conds_id from the depostion_conds table
			#Only need one row as the entries are duplicated in  each
			#The spin coating entries that are different are sorted later
			dcid = self.conn.execute('SELECT id FROM deposition_conds WHERE dep_conds_id = ?', (dc_result,))
			dcid_result = dcid.fetchone()[0]
			#This is to save having to rename everything...
			print 'This is dcid_result %s' % dcid_result
			layer_cond_id_exists_result = dcid_result
			#Get the method id and use to find the method_name and set the conditions name in the correct box
			dm = self.conn.execute('SELECT dep_met FROM depositions WHERE id = ?', (dep_cond_id_exists_result,))
			dm_result = dm.fetchone()[0]
			#Convert this to a name... why is it this way??????!
			dn = self.conn.execute('SELECT dep_name FROM dep_methods WHERE id = ?', (dm_result,))
			dn_result = dn.fetchone()[0]
			#use this to select which table to update... could use the id directly...
			if dn_result == "None": 
				pass
			elif dn_result == "Spin Coating":
				self.tab_layers_spin_dep_name_entry_var.set(cond_name_select_results)
			elif dn_result == "Spray Coating":
				self.tab_layers_spray_name_entry_var.set(cond_name_select_results)
			elif dn_result == "Dip Coating":
				self.tab_layers_dip_name_entry_var.set(cond_name_select_results)
			elif dn_result == "Bar Coating":
				self.tab_layers_bar_name_entry_var.set(cond_name_select_results)
			elif dn_result == "Slot-Die Coating":
				self.tab_layers_sd_name_entry_var.set(cond_name_select_results)
			elif dn_result == "Evaporation":
				self.tab_layers_evap_name_entry_var.set(cond_name_select_results)

			
		sol_select = self.conn.execute('SELECT evap_rate FROM deposition_conds WHERE id = ?', (dcid_result,))
		sol_select_results = sol_select.fetchone()[0]
		
		if sol_select_results:
			self.tab_layers_evap_rate_spin_var.set(sol_select_results)
		else:
			self.tab_layers_evap_rate_spin_var.set(False)

		atm_select = self.conn.execute('SELECT evaporator FROM deposition_conds WHERE id = ?', (dcid_result,))
		atm_select_results = atm_select.fetchone()[0]
		
		if atm_select_results:
			self.tab_layers_evap_box.current(atm_select_results)
		else:
			self.tab_layers_evap_box.current(0)	
		
		agi_select = self.conn.execute('SELECT dip_agi FROM deposition_conds WHERE id = ?', (dcid_result,))
		agi_select_results = agi_select.fetchone()[0]
		
		if agi_select_results:
			self.tab_layers_dip_agi_check_var.set(True)
		else:
			self.tab_layers_dip_agi_check_var.set(False)
		
		sol_select = self.conn.execute('SELECT dip_temp FROM deposition_conds WHERE id = ?', (dcid_result,))
		sol_select_results = sol_select.fetchone()[0]
		
		if sol_select_results:
			self.tab_layers_dip_sol_temp_spin_var.set(sol_select_results)
		else:
			self.tab_layers_dip_sol_temp_spin_var.set(False)
			
		sub_select = self.conn.execute('SELECT dip_sub_temp FROM deposition_conds WHERE id = ?', (dcid_result,))
		sub_select_results = sub_select.fetchone()[0]
		
		if sub_select_results:
			self.tab_layers_dip_sub_temp_spin_var.set(sub_select_results)
		else:
			self.tab_layers_dip_sub_temp_spin_var.set(False)
			
		time_select = self.conn.execute('SELECT dip_time FROM deposition_conds WHERE id = ?', (dcid_result,))
		time_select_results = time_select.fetchone()[0]
		
		if time_select_results:
			self.tab_layers_dip_time_spin_var.set(time_select_results)
		else:
			self.tab_layers_dip_time_spin_var.set(False)
			
		quan_select = self.conn.execute('SELECT dip_quan FROM deposition_conds WHERE id = ?', (dcid_result,))
		quan_select_results = quan_select.fetchone()[0]
		
		if quan_select_results:
			self.tab_layers_dip_quan_spin_var.set(quan_select_results)
		else:
			self.tab_layers_dip_quan_spin_var.set(False)
		
		speed_select = self.conn.execute('SELECT bar_speed_m_min FROM deposition_conds WHERE id = ?', (dcid_result,))
		speed_select_results = speed_select.fetchone()[0]
		
		if speed_select_results:
			self.tab_layers_bar_speed_spin_var.set(True)
		else:
			self.tab_layers_bar_speed_spin_var.set(False)
		
		sol_select = self.conn.execute('SELECT bar_temp FROM deposition_conds WHERE id = ?', (dcid_result,))
		sol_select_results = sol_select.fetchone()[0]
		
		if sol_select_results:
			self.tab_layers_bar_sol_temp_spin_var.set(sol_select_results)
		else:
			self.tab_layers_bar_sol_temp_spin_var.set(False)
		
		bed_select = self.conn.execute('SELECT bed_temp FROM deposition_conds WHERE id = ?', (dcid_result,))
		bed_select_results = bed_select.fetchone()[0]
		
		if bed_select_results:
			self.tab_layers_bar_bed_temp_spin_var.set(bed_select_results)
		else:
			self.tab_layers_bar_bed_temp_spin_var.set(False)
			
		sub_select = self.conn.execute('SELECT bar_sub_temp FROM deposition_conds WHERE id = ?', (dcid_result,))
		sub_select_results = sub_select.fetchone()[0]
		
		if sub_select_results:
			self.tab_layers_bar_sub_temp_spin_var.set(sub_select_results)
		else:
			self.tab_layers_bar_sub_temp_spin_var.set(False)
			
		size_select = self.conn.execute('SELECT bar_size_um FROM deposition_conds WHERE id = ?', (dcid_result,))
		size_select_results = size_select.fetchone()[0]
		
		if size_select_results:
			self.tab_layers_bar_size_spin_var.set(size_select_results)
		else:
			self.tab_layers_bar_size_spin_var.set(False)
			
		quan_select = self.conn.execute('SELECT bar_quan FROM deposition_conds WHERE id = ?', (dcid_result,))
		quan_select_results = quan_select.fetchone()[0]
		
		if quan_select_results:
			self.tab_layers_bar_quan_spin_var.set(quan_select_results)
		else:
			self.tab_layers_bar_quan_spin_var.set(False)
		
		bar_atm_select = self.conn.execute('SELECT bar_atm_id FROM deposition_conds WHERE id = ?', (dcid_result,))
		bar_atm_select_results = bar_atm_select.fetchone()[0]
		
		if bar_atm_select_results:
			self.tab_layers_bar_atm_box.current(bar_atm_select_results)
		else:
			self.tab_layers_bar_atm_box.current(0)
			
		pres_select = self.conn.execute('SELECT spray_pressure FROM deposition_conds WHERE id = ?', (dcid_result,))
		pres_select_results = pres_select.fetchone()[0]
		
		if pres_select_results:
			self.tab_layers_spray_pres_spin_var.set(pres_select_results)
		else:
			self.tab_layers_spray_pres_spin_var.set('')
		
		gun_select = self.conn.execute('SELECT spray_gun_id FROM deposition_conds WHERE id = ?', (dcid_result,))
		gun_select_results = gun_select.fetchone()[0]
		
		if gun_select_results:
			self.tab_layers_spray_gun_box.current(int(gun_select_results))
		else:
			self.tab_layers_spray_gun_box.current(0)
		
		dist_select = self.conn.execute('SELECT distance FROM deposition_conds WHERE id = ?', (dcid_result,))
		dist_select_results = dist_select.fetchone()[0]
		
		if dist_select_results:
			self.tab_layers_spray_dist_spin_var.set(dist_select_results)
		else:
			self.tab_layers_spray_dist_spin_var.set('')
		
		temp_select = self.conn.execute('SELECT spray_sub_temp FROM deposition_conds WHERE id = ?', (dcid_result,))
		temp_select_results = temp_select.fetchone()[0]
		
		if temp_select_results:
			self.tab_layers_spray_temp_spin_var.set(temp_select_results)
		else:
			self.tab_layers_spray_temp_spin_var.set('')
			
		pres_select = self.conn.execute('SELECT spray_pressure FROM deposition_conds WHERE id = ?', (dcid_result,))
		pres_select_results = pres_select.fetchone()[0]
		
		if pres_select_results:
			self.tab_layers_spray_pres_spin_var.set(pres_select_results)
		else:
			self.tab_layers_spray_pres_spin_var.set('')
			
		pass_select = self.conn.execute('SELECT passes FROM deposition_conds WHERE id = ?', (dcid_result,))
		pass_select_results = pass_select.fetchone()[0]
		
		if pass_select_results:
			self.tab_layers_spray_pass_spin_var.set(pass_select_results)
		else:
			self.tab_layers_spray_pass_spin_var.set('')	
			
		vol_select = self.conn.execute('SELECT spray_vol FROM deposition_conds WHERE id = ?', (dcid_result,))
		vol_select_results = vol_select.fetchone()[0]
		
		if vol_select_results:
			self.tab_layers_spray_vol_spin_var.set(vol_select_results)
		else:
			self.tab_layers_spray_vol_spin_var.set('')
			
		screw_select = self.conn.execute('SELECT spray_screw FROM deposition_conds WHERE id = ?', (dcid_result,))
		screw_select_results = screw_select.fetchone()[0]
		
		if screw_select_results:
			self.tab_layers_spray_set_spin_var.set(screw_select_results)
		else:
			self.tab_layers_spray_set_spin_var.set('')	
		
		feed_select = self.conn.execute('SELECT feed_gas_id FROM deposition_conds WHERE id = ?', (dcid_result,))
		feed_select_results = feed_select.fetchone()[0]
		
		if feed_select_results:
			self.tab_layers_spray_gas_box.current(int(feed_select_results))
		else:
			self.tab_layers_spray_gas_box.current(0)
			
		atm_select = self.conn.execute('SELECT spray_atm_id FROM deposition_conds WHERE id = ?', (dcid_result,))
		atm_select_results = atm_select.fetchone()[0]
		
		if atm_select_results:
			self.tab_layers_spray_atm_box.current(int(atm_select_results))
		else:
			self.tab_layers_spray_atm_box.current(0)
		
		
		####SD
		#######	
		coat_select = self.conn.execute('SELECT sd_coater FROM deposition_conds WHERE id = ?', (dcid_result,))
		coat_select_results = coat_select.fetchone()[0]
		
		if coat_select_results:
			self.tab_layers_coat_box.set(coat_select_results)
		else:
			self.tab_layers_coat_box.set('None')
		
		head_select = self.conn.execute('SELECT sd_head FROM deposition_conds WHERE id = ?', (dcid_result,))
		head_select_results = head_select.fetchone()[0]
		
		if head_select_results:
			self.tab_layers_sd_head_box.set(head_select_results)
		else:
			self.tab_layers_sd_head_box.set('None')

		shim_select = self.conn.execute('SELECT shim FROM deposition_conds WHERE id = ?', (dcid_result,))
		shim_select_results = shim_select.fetchone()[0]
		
		if shim_select_results:
			self.tab_layers_sd_shim_box.set(shim_select_results)
			##run this to update the paras
			self.tab_layers_sd_shim_box_update()
		else:
			self.tab_layers_sd_shim_box.set('None')
			#Set these false if not needed
			self.tab_layers_sd_shim_thick_var.set('')
			self.tab_layers_sd_shim_wid_var.set('')	
			self.tab_layers_sd_shim_stripes_var.set('')

		shn_select = self.conn.execute('SELECT shim_num FROM deposition_conds WHERE id = ?', (dcid_result,))
		shn_select_results = shn_select.fetchone()[0]
		
		if shn_select_results:
			self.tab_layers_sd_shim_num_spin_var.set(int(shn_select_results))
		else:
			self.tab_layers_sd_shim_num_spin_var.set('')

		mg_select = self.conn.execute('SELECT mg FROM deposition_conds WHERE id = ?', (dcid_result,))
		mg_select_results = mg_select.fetchone()[0]
		
		if mg_select_results:
			self.tab_layers_sd_mg_box.set(mg_select_results)
			#run this to update the paras
			self.tab_layers_sd_mg_box_update()
		else:
			self.tab_layers_sd_mg_box.set('None')	
			##Set these false if not needed
			self.tab_layers_sd_mg_tab_var.set('')
			self.tab_layers_sd_mg_thick_text_var.set('')
			self.tab_layers_sd_mg_wid_text_var.set('')
			self.tab_layers_sd_mg_stripes_var.set('')	
		
		
		pl_select = self.conn.execute('SELECT platten FROM deposition_conds WHERE id = ?', (dcid_result,))
		pl_select_results = pl_select.fetchone()[0]
		
		if pl_select_results:
			self.tab_layers_sd_plat_box.set(pl_select_results)
		else:
			self.tab_layers_sd_plat_box.set('None')
		
		
		plt_select = self.conn.execute('SELECT plat_temp FROM deposition_conds WHERE id = ?', (dcid_result,))
		plt_select_results = plt_select.fetchone()[0]
		
		if plt_select_results:
			self.tab_layers_sd_plat_temp_spin_var.set(float(plt_select_results))
		else:
			self.tab_layers_sd_plat_temp_spin_var.set('')
			
		sst_select = self.conn.execute('SELECT sd_soln_temp FROM deposition_conds WHERE id = ?', (dcid_result,))
		sst_select_results = sst_select.fetchone()[0]
		
		if sst_select_results:
			self.tab_layers_sd_ink_temp_spin_var.set(float(sst_select_results))
		else:
			self.tab_layers_sd_ink_temp_spin_var.set('')
		
		st_select = self.conn.execute('SELECT sd_sub_temp FROM deposition_conds WHERE id = ?', (dcid_result,))
		st_select_results = st_select.fetchone()[0]
		
		if st_select_results:
			self.tab_layers_sd_sub_temp_spin_var.set(float(st_select_results))
		else:
			self.tab_layers_sd_sub_temp_spin_var.set('')	
			
		
		gh_select = self.conn.execute('SELECT gap_height FROM deposition_conds WHERE id = ?', (dcid_result,))
		gh_select_results = gh_select.fetchone()[0]
		
		if gh_select_results:
			self.tab_layers_sd_height_spin_var.set(float(gh_select_results))
		else:
			self.tab_layers_sd_height_spin_var.set('')
			
		an_select = self.conn.execute('SELECT angle FROM deposition_conds WHERE id = ?', (dcid_result,))
		an_select_results = an_select.fetchone()[0]
		
		if an_select_results:
			self.tab_layers_sd_angle_spin_var.set(float(an_select_results))
		else:
			self.tab_layers_sd_angle_spin_var.set(0)
			
		sp_select = self.conn.execute('SELECT speed FROM deposition_conds WHERE id = ?', (dcid_result,))
		sp_select_results = sp_select.fetchone()[0]
		
		if sp_select_results:
			self.tab_layers_sd_web_spin_var.set(float(sp_select_results))
		else:
			self.tab_layers_sd_web_spin_var.set(0)		

		fl_select = self.conn.execute('SELECT flow_rate FROM deposition_conds WHERE id = ?', (dcid_result,))
		fl_select_results = fl_select.fetchone()[0]
		
		if fl_select_results:
			self.tab_layers_sd_rate_spin_var.set(float(fl_select_results))
		else:
			self.tab_layers_sd_rate_spin_var.set('')			
			
		pcd_select = self.conn.execute('SELECT pre_coat_delay FROM deposition_conds WHERE id = ?', (dcid_result,))
		pcd_select_results = pcd_select.fetchone()[0]
		
		if pcd_select_results:
			self.tab_layers_sd_pre_delay_spin_var.set(float(pcd_select_results))
		else:
			self.tab_layers_sd_pre_delay_spin_var.set(0)
			
		pcpd_select = self.conn.execute('SELECT pre_coat_pump_delay FROM deposition_conds WHERE id = ?', (dcid_result,))
		pcpd_select_results = pcpd_select.fetchone()[0]
		
		if pcpd_select_results:
			self.tab_layers_sd_pre_coat_delay_spin_var.set(float(pcpd_select_results))
		else:
			self.tab_layers_sd_pre_coat_delay_spin_var.set(0)
			
					
		pd_select = self.conn.execute('SELECT pump_delay FROM deposition_conds WHERE id = ?', (dcid_result,))
		pd_select_results = pd_select.fetchone()[0]
		
		if pd_select_results:
			self.tab_layers_sd_pump_delay_spin_var.set(float(pd_select_results))
		else:
			self.tab_layers_sd_pump_delay_spin_var.set(0)
			
		ten_select = self.conn.execute('SELECT web_tension FROM deposition_conds WHERE id = ?', (dcid_result,))
		ten_select_results = ten_select.fetchone()[0]
		
		if ten_select_results:
			self.tab_layers_sd_web_ten_spin_var.set(float(ten_select_results))
		else:
			self.tab_layers_sd_web_ten_spin_var.set(0)
		###Spin
		##### get the spin coater id #########
		tab_layers_layer_cond_coater_select = self.conn.execute('SELECT spin_coater_id FROM deposition_conds WHERE id = ?', (dcid_result,))
		tab_layers_layer_cond_coater_select_results = tab_layers_layer_cond_coater_select.fetchone()[0]
		
		if str(tab_layers_layer_cond_coater_select_results):
			self.tab_layers_spin_id_box.current(tab_layers_layer_cond_coater_select_results)
		else:
			self.tab_layers_spin_id_box.set('')
		
		##### get the substrate temp ########
		tab_layers_layer_cond_temp_select = self.conn.execute('SELECT temp FROM deposition_conds WHERE id = ?', (dcid_result,))
		tab_layers_layer_cond_temp_select_results = tab_layers_layer_cond_temp_select.fetchone()[0]
		
		if tab_layers_layer_cond_temp_select_results:
			self.tab_layers_spin_spin_temp_var.set(tab_layers_layer_cond_temp_select_results)
		else:
			self.tab_layers_spin_spin_temp_var.set(0)
			
		###### get the delay before spin ######
		tab_layers_layer_cond_delay_select = self.conn.execute('SELECT delay FROM deposition_conds WHERE id = ?', (dcid_result,))
		tab_layers_layer_cond_delay_select_results = tab_layers_layer_cond_delay_select.fetchone()[0]
		
		if tab_layers_layer_cond_delay_select_results:
			self.tab_layers_spin_spin_delay_var.set(tab_layers_layer_cond_delay_select_results)
		else:
			self.tab_layers_spin_spin_delay_var.set(0)
		
		##### get the spin atmosphere
		tab_layers_layer_cond_atm_select = self.conn.execute('SELECT spin_atm FROM deposition_conds WHERE id = ?', (dcid_result,))
		tab_layers_layer_cond_atm_select_results = tab_layers_layer_cond_atm_select.fetchone()[0]
		
		tab_layers_layer_cond_atm_select_results = str(tab_layers_layer_cond_atm_select_results)
		if tab_layers_layer_cond_atm_select_results == 'None':
			self.tab_layers_spin_atm_box.set('')
		else:
			self.tab_layers_spin_atm_box.current(tab_layers_layer_cond_atm_select_results)
		##### get the drip time....	
		tab_layers_layer_drip_time_select = self.conn.execute('SELECT drip_time FROM deposition_conds WHERE id = ?', (dcid_result,))
		tab_layers_layer_drip_time_select_results = tab_layers_layer_drip_time_select.fetchone()[0]
		
		if tab_layers_layer_drip_time_select_results:
			self.tab_layers_spin_drip_time_var.set(tab_layers_layer_drip_time_select_results)
		else:
			self.tab_layers_spin_drip_time_var.set('')
			
		##### get the drip vol....	
		tab_layers_layer_drip_vol_select = self.conn.execute('SELECT drip_vol FROM deposition_conds WHERE id = ?', (dcid_result,))
		tab_layers_layer_drip_vol_select_results = tab_layers_layer_drip_vol_select.fetchone()[0]
		
		if tab_layers_layer_drip_vol_select_results:
			self.tab_layers_spin_drip_quan_var.set(tab_layers_layer_drip_vol_select_results)
		else:
			self.tab_layers_spin_drip_quan_var.set('')

		####Get the drip formulation
		tab_layers_layer_drip_form_select = self.conn.execute('SELECT drip_sol FROM deposition_conds WHERE id = ?', (dcid_result,))
		tab_layers_layer_drip_form_select_results = tab_layers_layer_drip_form_select.fetchone()[0]
		
		tab_layers_layer_drip_form_select_results = str(tab_layers_layer_drip_form_select_results)
		if tab_layers_layer_drip_form_select_results:
			self.tab_layers_spin_drip_sol_box.set(tab_layers_layer_drip_form_select_results)
		else:
			self.tab_layers_spin_drip_sol_box.set('')

		##### get the dispensed vol....	
		tab_layers_layer_spin_vol_select = self.conn.execute('SELECT spin_vol FROM deposition_conds WHERE id = ?', (dcid_result,))
		tab_layers_layer_spin_vol_select_results = tab_layers_layer_spin_vol_select.fetchone()[0]
		
		if tab_layers_layer_spin_vol_select_results:
			self.tab_layers_spin_spin_vol_var.set(tab_layers_layer_spin_vol_select_results)
		else:
			self.tab_layers_spin_spin_vol_var.set(0)
			
		##### get the solution temp....	
		tab_layers_layer_spin_soln_temp_select = self.conn.execute('SELECT spin_soln_temp FROM deposition_conds WHERE id = ?', (dcid_result,))
		tab_layers_layer_spin_soln_temp_select_results = tab_layers_layer_spin_soln_temp_select.fetchone()[0]
		
		if tab_layers_layer_spin_soln_temp_select_results:
			self.tab_layers_spin_spin_soln_temp_var.set(tab_layers_layer_spin_soln_temp_select_results)
		else:
			self.tab_layers_spin_spin_soln_temp_var.set('')

		##### for loop to populate the listboxes ##########	
		self.tab_layers_spin_speed_listbox.delete(0,END)
		self.tab_layers_spin_acc_listbox.delete(0,END)
		self.tab_layers_spin_time_listbox.delete(0,END)

		#Go through all the rows with this name/conds id and extract the parameters and add to the listboxes
		spin_speed_ids = self.conn.execute('SELECT id FROM deposition_conds WHERE dep_conds_id = ?', (dc_result,))
		spin_speed_ids_results = spin_speed_ids.fetchall()
		
		for index, i in enumerate(spin_speed_ids_results):
			i = i[0]
			print i
			tab_layer_spin_speed_list_exists = self.conn.execute('SELECT spin_speed FROM deposition_conds WHERE id = ?', (i,))
			tab_layer_spin_speed_list_exists_results = tab_layer_spin_speed_list_exists.fetchone()[0]

			if not tab_layer_spin_speed_list_exists_results:
				pass
			else:	
				self.tab_layers_spin_speed_listbox.insert(index, tab_layer_spin_speed_list_exists_results)

			tab_layer_spin_acc_list_exists = self.conn.execute('SELECT spin_acc FROM deposition_conds WHERE id = ?', (i,))
			tab_layer_spin_acc_list_exists_results = tab_layer_spin_acc_list_exists.fetchone()[0]

			
			if not tab_layer_spin_acc_list_exists_results:
				pass
			else:	
				self.tab_layers_spin_acc_listbox.insert(index, tab_layer_spin_acc_list_exists_results)
			
			tab_layer_spin_time_list_exists = self.conn.execute('SELECT time  FROM deposition_conds WHERE id = ?', (i,))
			tab_layer_spin_time_list_exists_results = tab_layer_spin_time_list_exists.fetchone()[0]
			
			if not tab_layer_spin_time_list_exists_results:
				pass
			else:	
				self.tab_layers_spin_time_listbox.insert(index, tab_layer_spin_time_list_exists_results)	
	

	def tab_layers_get_cond_list(self, *args):
		#Clear the list...
		self.tab_layers_cond_list = []
		#Use the selected dep_met to list all the conditions for that method
		#Use the drop down name to get the id	
		dep_met_select = self.conn.execute('SELECT id FROM dep_methods WHERE dep_name = ?', (self.tab_layers_dep_box.get(),))
		dep_met_select_result = dep_met_select.fetchone()[0]

		#Use the id to get the dep_conds_id from the depositions table - it is the id
		dep_conds_select = self.conn.execute('SELECT id FROM depositions WHERE dep_met = ?', (dep_met_select_result,))
		dep_conds_select_results = dep_conds_select.fetchall()
		
		#Check if they are there... 
		#and go through and populate the drop down list with the names selected from the conds_table
		if dep_conds_select_results:
			for i in dep_conds_select_results:

				dep_conds_name_select = self.conn.execute('SELECT name FROM depositions WHERE id = ?', (i[0],))
				dep_conds_name_select_result = dep_conds_name_select.fetchone()[0]
				print dep_conds_name_select_result
				#Only selecting the first should be fine as the name is the same for all of the records with the same dep_conds_id (could use the name instead...)
				#Check if it is there...
				#Add to the list 
				self.tab_layers_cond_list.append(dep_conds_name_select_result)
			#Add the list names to the drop down...
			self.tab_layers_cond_box['values'] = self.tab_layers_cond_list
		else:
			self.tab_layers_cond_box['values'] = []
			self.tab_layers_cond_label_var.set('')
	def tab_layers_get_form_names(self, *args):
		self.tab_layers_form_list = []
		self.tab_layers_spin_drip_sol_list =[]
		#self.tab_layers_form_box.set('')
		#self.tab_layers_spin_drip_sol_box.set('')
		## get the id of the material ###
		tab_layers_layer_form_select = self.conn.execute('SELECT form_name FROM formulations WHERE state = 0')
		tab_layers_layer_form_select_results = tab_layers_layer_form_select.fetchall()
		
		if tab_layers_layer_form_select_results:
			for i in tab_layers_layer_form_select_results:
				if i[0]:
					self.tab_layers_form_list.append(i[0])
		
		self.tab_layers_form_box['values'] = list(reversed(list(sorted(set(i for i in self.tab_layers_form_list)))))
		self.tab_layers_spin_drip_sol_box['values'] = list(reversed(list(sorted(set(i for i in self.tab_layers_form_list)))))
	
	
	
	def tab_layers_get_type_list(self, *args):
		self.tab_layers_type_list = []
		## get the names of the deposition methods ###
		type_select = self.conn.execute('SELECT layer_type FROM layer_types')
		type_select_results = type_select.fetchall()
		
		if type_select_results:
			for i in type_select_results:
				if i[0]:
					self.tab_layers_type_list.append(i[0])
		self.tab_layers_type_box['values'] = list(sorted(self.tab_layers_type_list))
		
	def tab_layers_get_dep_method_names(self, *args):
		self.tab_layers_dep_list = []
		## get the names of the deposition methods ###
		dep_met_select = self.conn.execute('SELECT dep_name FROM dep_methods')
		dep_met_select_results = dep_met_select.fetchall()
		
		if dep_met_select_results:
			for i in dep_met_select_results:
				if i[0]:
					self.tab_layers_dep_list.append(i[0])
		self.tab_layers_dep_box['values'] = list(self.tab_layers_dep_list)
		#####
	def tab_layers_get_layer_names(self, *args):
		self.tab_layers_names_list = []
		self.tab_layers_name_box.set('New layer name or select previous layer to show conditions')
		## get the id of the material ###
		tab_layers_layer_name_select = self.conn.execute('SELECT layer_name FROM layers')
		tab_layers_layer_name_select_results = tab_layers_layer_name_select.fetchall()
		
		if tab_layers_layer_name_select_results:
			for i in tab_layers_layer_name_select_results:
				if i[0]:
					self.tab_layers_names_list.append(i[0])
		self.tab_layers_name_box['values'] = list(reversed(self.tab_layers_names_list))
				
	def tab_layers_multi_list_vsb(self, *args):
		self.tab_layers_spin_speed_listbox.yview(*args)
		self.tab_layers_spin_acc_listbox.yview(*args)
		self.tab_layers_spin_time_listbox.yview(*args)	
	def mat_batch_tk(self, *args):
		self.tab_bat_frame0 = Frame(self.tab_mat_batch, width=1300, height=800)
		self.tab_bat_frame0.grid()
		
		##Frame for the propeties etc of the material
		self.tab_bat_frame_prop = Frame(self.tab_bat_frame0, width=100, height=8)
		self.tab_bat_frame_prop.grid(row=0, column=0, sticky=W)

		self.tab_bat_frame_prop_sub = Frame(self.tab_bat_frame_prop)
		self.tab_bat_frame_prop_sub.grid(row=0, column=0, sticky=W, columnspan=10)
		
		#### material id common name #####
		self.tab_bat_label_com_name = Label(self.tab_bat_frame_prop_sub, text="Material:")
		self.tab_bat_label_com_name.grid(row=0, column=0, sticky=E)
		
		#does putting an empty list here slow everything down
		self.tab_bat_materials_names_list = []
		self.tab_bat_com = StringVar()
		self.tab_bat_com_box = Combobox(self.tab_bat_frame_prop_sub, textvariable=self.tab_bat_com,width=100)
		self.tab_bat_com_box.bind('<<ComboboxSelected>>', self.tab_bat_get_batches)
		self.tab_bat_com_box['values'] = self.tab_bat_materials_names_list
		self.tab_bat_com_box.grid(row=0, column=1, sticky=W)
		self.tab_bat_com_box.state(['readonly'])
		self.tab_bat_populate_materials_list()
		
		self.tab_bat_mat_id_var = StringVar()
		self.tab_bat_label_mat_id = Label(self.tab_bat_frame_prop_sub, textvariable=self.tab_bat_mat_id_var)
		self.tab_bat_label_mat_id.grid(row=0, column=2, sticky=E)
		#### material batch codes #####
		self.tab_bat_label_batch_code = Label(self.tab_bat_frame_prop, text="Batch Codes:")
		self.tab_bat_label_batch_code.grid(row=1, column=0, sticky=E)
		
		self.tab_bat_batch_codes_list = []
		self.tab_bat_batch_codes = StringVar()
		self.tab_bat_batch_codes_box = Combobox(self.tab_bat_frame_prop, textvariable=self.tab_bat_batch_codes, width=60)
		self.tab_bat_batch_codes_box.bind('<<ComboboxSelected>>', self.update_material_batch_data)
		self.tab_bat_batch_codes_box['values'] = self.tab_bat_batch_codes_list
		self.tab_bat_batch_codes_box.grid(row=1, column=1, sticky=W)
		
		self.tab_bat_check_var_complete = IntVar()
		self.tab_bat_check_complete = Checkbutton(self.tab_bat_frame_prop, text="Show Complete", variable=self.tab_bat_check_var_complete,command=self.tab_bat_get_batches)
		self.tab_bat_check_complete.grid(row=1, column=2, sticky=W)
		
		self.tab_bat_but_complete = Button(self.tab_bat_frame_prop, text='Switch Complete / Remaining', command=self.mark_material_batch_complete)
		self.tab_bat_but_complete.grid(row=1, column=3)
		
		self.tab_bat_populate_materials_list()
		######
		######
		if platform.system() == "Windows":
			photo = Image.open("..\\..\\_database\\deps\\blank.gif")
			photo = photo.resize((200, 200), Image.ANTIALIAS)
			photo_temp = photo.save("..\\..\\_database\\deps\\material_batch_gifs\\temp\\temp_photo.gif")
			photo = PhotoImage(file="..\\..\\_database\\deps\\material_batch_gifs\\temp\\temp_photo.gif")
		else:
			photo = Image.open("../../_database/deps/blank.gif")
			photo = photo.resize((200, 200), Image.ANTIALIAS)
			photo_temp = photo.save("../../_database/deps/material_batch_gifs/temp/temp_photo.gif")
			photo = PhotoImage(file="../../_database/deps/material_batch_gifs/temp/temp_photo.gif")
		
		self.image_finam = "blank.gif"	
		self.tab_bat_pic = Label(self.tab_bat_frame_prop, image=photo)
		self.tab_bat_pic.image = photo
		self.tab_bat_pic.grid(row=2, column=1, sticky=W)
		
		self.tab_bat_pic_but = Button(self.tab_bat_frame_prop, text='Add Picture', command=self.tab_bat_pic_update)
		self.tab_bat_pic_but.grid(row=2, column=2, sticky=W)
		######
		######
		
		### product name ######
		self.tab_bat_label_prod_name = Label(self.tab_bat_frame_prop, text="Product Name:")
		self.tab_bat_label_prod_name.grid(row=3, column=0, sticky=E)
		
		self.tab_bat_prod_name_var = StringVar()
		self.tab_bat_entry_prod_name = Entry(self.tab_bat_frame_prop, textvariable=self.tab_bat_prod_name_var, width=75)
		self.tab_bat_entry_prod_name.grid(row=3, column=1, sticky=W, columnspan=10)
		
		###### product code #####
		self.tab_bat_label_prod_code = Label(self.tab_bat_frame_prop, text="Product Code:")
		self.tab_bat_label_prod_code.grid(row=4, column=0, sticky=E)
		
		self.tab_bat_prod_code_var = StringVar()
		self.tab_bat_entry_prod_code = Entry(self.tab_bat_frame_prop, textvariable=self.tab_bat_prod_code_var, width=75)
		self.tab_bat_entry_prod_code.grid(row=4, column=1, sticky=W, columnspan=10)
		
		### supplier ##### currently only predefined #####
		self.tab_bat_label_sup = Label(self.tab_bat_frame_prop, text="Supplier:")
		self.tab_bat_label_sup.grid(row=5, column=0, sticky=E)
		
		self.tab_bat_sup_var = StringVar()
		self.tab_bat_sup_box = Combobox(self.tab_bat_frame_prop, textvariable=self.tab_bat_sup_var)
		self.tab_bat_sup_box.bind('<<ComboboxSelected>>')
		#self.tab_bat_sup_box['values'] = self.tab_bat_sup_list
		self.tab_bat_sup_box.grid(row=5, column=1, sticky=W)
		self.tab_bat_sup_box.state(['readonly'])
		self.mat_bat_populate_sups_list()	
		
		self.tab_bat_sup_add = Button(self.tab_bat_frame_prop, text='Add New Supplier', command=self.mat_bat_add_sup)
		self.tab_bat_sup_add.grid(row=5, column=2, sticky=E)
		
		self.tab_bat_sup_name_var = StringVar()
		self.tab_bat_entry_sup_name = Entry(self.tab_bat_frame_prop, textvariable=self.tab_bat_sup_name_var, width=50)
		self.tab_bat_entry_sup_name.grid(row=5, column=3, sticky=W, columnspan=10)
		
		### cost ##### 
		self.tab_bat_label_cost = Label(self.tab_bat_frame_prop, text="Cost (GBP):")
		self.tab_bat_label_cost.grid(row=6, column=0, sticky=E)

		self.tab_bat_spin_cost_var = StringVar()
		self.tab_bat_spin_cost = Spinbox(self.tab_bat_frame_prop, from_=0, to=9999999, format="%04.2f", increment='0.01', textvariable=self.tab_bat_spin_cost_var)
		self.tab_bat_spin_cost.grid(row=6, column=1, sticky=W)
		#### Date batch recieved ##### 
		##Frame for the date stuff
		self.tab_bat_frame_date = Frame(self.tab_bat_frame0, width=100, height=8)
		self.tab_bat_frame_date.grid(row=2, column=0, sticky=W)
		
		self.tab_bat_label_date = Label(self.tab_bat_frame_date, text="Date Recieved:")
		self.tab_bat_label_date.grid(row=0, column=0, sticky=E)

		self.tab_bat_spin_year_var = StringVar()
		self.tab_bat_spin_year = Spinbox(self.tab_bat_frame_date, from_=2014, to=2020, format="%04.0f", textvariable=self.tab_bat_spin_year_var, width=6)
		self.tab_bat_spin_year.grid(row=0, column=1, sticky=W)
		self.tab_bat_spin_year_var.set(time.strftime("%Y"))

		self.tab_bat_spin_month_var = StringVar()
		self.tab_bat_spin_month = Spinbox(self.tab_bat_frame_date, from_=01, to=31, format="%02.0f", textvariable=self.tab_bat_spin_month_var, width=6)
		self.tab_bat_spin_month.grid(row=0, column=2, sticky=W)
		self.tab_bat_spin_month_var.set(time.strftime("%m"))
		
		self.tab_bat_spin_day_var = StringVar()
		self.tab_bat_spin_day = Spinbox(self.tab_bat_frame_date, from_=01, to=31, format="%02.0f", textvariable=self.tab_bat_spin_day_var, width=6)
		self.tab_bat_spin_day.grid(row=0, column=3, sticky=W)
		self.tab_bat_spin_day_var.set(time.strftime("%d"))
		
		#### amount recieved ########
		self.tab_bat_frame_amount = Frame(self.tab_bat_frame0, width=100, height=8)
		self.tab_bat_frame_amount.grid(row=3, column=0, sticky=W)
		
		self.tab_bat_label_amount = Label(self.tab_bat_frame_amount, text="Amount Recieved:")
		self.tab_bat_label_amount.grid(row=0, column=0, sticky=E)

		self.tab_bat_spin_amount_var = StringVar()
		self.tab_bat_spin_amount = Spinbox(self.tab_bat_frame_amount, from_=0, to=9999999, format="%04.3f", increment='0.001', textvariable=self.tab_bat_spin_amount_var)
		self.tab_bat_spin_amount.grid(row=0, column=1, sticky=W)
		
		#### amount units ######### 
		### supplier ##### currently only predefined #####
		self.tab_bat_label_units = Label(self.tab_bat_frame_amount, text="Units:")
		self.tab_bat_label_units.grid(row=0, column=2, sticky=E)
		
		self.tab_bat_units_var = StringVar()
		self.tab_bat_units_box = Combobox(self.tab_bat_frame_amount, textvariable=self.tab_bat_units_var)
		self.tab_bat_units_box.bind('<<ComboboxSelected>>')
		self.tab_bat_units_box['values'] = self.tab_bat_units_list
		self.tab_bat_units_box.grid(row=0, column=3, sticky=W)
		self.tab_bat_units_box.state(['readonly'])	
		
		
		self.tab_bat_frame_buttons = Frame(self.tab_bat_frame0, width=100, height=8)
		self.tab_bat_frame_buttons.grid(row=6, column=0, sticky=W)
		
		self.tab_bat_but_commit = Button(self.tab_bat_frame_buttons, text='Commit Material Batch to Database', command=self.commit_material_batch)
		self.tab_bat_but_commit.grid(row=0, column=0, sticky=W)
		
		self.mat_bat_status_var = StringVar()
		self.tab_bat_status = Label(self.tab_bat_frame_buttons, textvariable=self.mat_bat_status_var)
		self.tab_bat_status.grid(row=1, column=0, sticky=W)
		
	def mark_material_batch_complete(self, *args):
		#long way round
		#Get the material batch id
		tab_bat_id = self.conn.execute('SELECT id FROM mat_bat WHERE batch_code = ?', (self.tab_bat_batch_codes_box.get(),))
		tab_bat_id_result = tab_bat_id.fetchone()[0]
		if str(tab_bat_id_result):
			#Find the current state and switch
			tab_bat_state = self.conn.execute('SELECT state FROM mat_bat WHERE id = ?', (tab_bat_id_result,))
			tab_bat_state_result = tab_bat_state.fetchone()[0]
			#Change the state
			if tab_bat_state_result == 1:
				state = 0
			else:
				state = 1
			self.conn.execute('UPDATE mat_bat SET state = ? WHERE id = ?',(state, tab_bat_id_result,));
			self.conn.commit()
			
			self.tab_bat_get_batches()
	def tab_bat_pic_update(self, *args):
		if platform.system() == "Windows":
			finam = tkFileDialog.askopenfilename(initialdir = "..\\..\\_database\\deps\\material_batch_gifs\\",title = "Select file",filetypes = (("gif files","*.gif"),("all files","*.*")))		
			if finam:
				### test this works on windows
				finam = os.path.basename(finam)
				print finam
				finam = str(finam)
			else:
				finam = "blank.gif"
			photo = Image.open("..\\..\\_database\\deps\\material_batch_gifs\\%s" % (finam))
			photo = photo.resize((200, 200), Image.ANTIALIAS)
			photo_temp = photo.save("..\\..\\_database\\deps\\material_batch_gifs\\temp\\temp_photo.gif")
			photo = PhotoImage(file="..\\..\\_database\\deps\\material_batch_gifs\\temp\\temp_photo.gif")
		else:
			finam = tkFileDialog.askopenfilename(initialdir = "../../_database/deps/material_batch_gifs/",title = "Select file",filetypes = (("gif files","*.gif"),("all files","*.*")))		
			if finam:
				finam= os.path.basename(finam)
				print finam
				finam = str(finam)
			else:
				finam = "blank.gif"
			photo = Image.open("../../_database/deps/material_batch_gifs/%s" % (finam))
			photo = photo.resize((200, 200), Image.ANTIALIAS)
			photo_temp = photo.save("../../_database/deps/material_batch_gifs/temp/temp_photo.gif")
			photo = PhotoImage(file="../../_database/deps/material_batch_gifs/temp/temp_photo.gif")
		
		
		self.tab_bat_pic.configure(image=photo)	
		self.tab_bat_pic.image = photo
		self.image_finam = finam
		
	def mat_bat_populate_sups_list(self, *args):
		self.tab_bat_sups_names_list = []
		## get the common names of the materials ###
		tab_bat_id_select = self.conn.execute('SELECT name FROM suppliers')
		tab_bat_id_select_result = tab_bat_id_select.fetchall()
		
		if tab_bat_id_select_result:
			for i in tab_bat_id_select_result:
				self.tab_bat_sups_names_list.append(i[0])
			self.tab_bat_sup_box['values'] = list(sorted(self.tab_bat_sups_names_list))
				
	def mat_bat_add_sup(self, *args):
		name = self.tab_bat_entry_sup_name.get()

		mat_bat_dict = {
				'name':self.tab_bat_sup_name_var.get(),
				}
		function_name = 'suppliers'
		mat_bat_results = self.materials_mod(self, mat_bat_dict, function_name, self.conn)
		self.mat_bat_status_var.set(mat_bat_results[1])
		self.mat_bat_populate_sups_list()	
	def update_material_batch_data(self, *args):
		###clear the ref to the old picture
		try:
			del self.image_finam
		except:
			pass
		## get the id of the material ###
		tab_bat_mat_id_select_update = self.conn.execute('SELECT id FROM materials WHERE common_name = ?', (self.tab_bat_com_box.get(),))
		tab_bat_mat_id_select_update_result = tab_bat_mat_id_select_update.fetchone()[0]
		## get the id of the batch_code ###
		tab_bat_batch_id_select = self.conn.execute('SELECT id FROM mat_bat WHERE batch_code =? AND mat_id = ?', (self.tab_bat_batch_codes_box.get(), tab_bat_mat_id_select_update_result,))
		tab_bat_batch_id_select_result = tab_bat_batch_id_select.fetchone()[0]
		
		prev_prod_name_bat_inputs = self.conn.execute('SELECT prod_name FROM mat_bat WHERE id = ?', (tab_bat_batch_id_select_result,))
		prev_prod_name_bat_inputs_results = prev_prod_name_bat_inputs.fetchone()[0]
		if prev_prod_name_bat_inputs_results:
			self.tab_bat_prod_name_var.set(prev_prod_name_bat_inputs_results)
		else:
			self.tab_bat_prod_name_var.set(False)
		
		prev_prod_code_bat_inputs = self.conn.execute('SELECT prod_code FROM mat_bat WHERE id = ?', (tab_bat_batch_id_select_result,))
		prev_prod_code_bat_inputs_results = prev_prod_code_bat_inputs.fetchone()[0]
		if prev_prod_code_bat_inputs_results:
			self.tab_bat_prod_code_var.set(prev_prod_code_bat_inputs_results)
		else:
			self.tab_bat_prod_code_var.set(False)
		

		
		prev_prod_cost_bat_inputs = self.conn.execute('SELECT cost FROM mat_bat WHERE id = ?', (tab_bat_batch_id_select_result,))
		prev_prod_cost_bat_inputs_results = prev_prod_cost_bat_inputs.fetchone()[0]
		if prev_prod_cost_bat_inputs_results:
			self.tab_bat_spin_cost_var.set(prev_prod_cost_bat_inputs_results)
		else:
			self.tab_bat_spin_cost_var.set(False)
		
		prev_mat_bat_date = self.conn.execute('SELECT date_rec FROM mat_bat WHERE id = ?', (tab_bat_batch_id_select_result,))
		prev_mat_bat_date_results = prev_mat_bat_date.fetchone()[0]
		if prev_mat_bat_date_results:
			self.tab_bat_spin_year_var.set(prev_mat_bat_date_results[:4])
			self.tab_bat_spin_month_var.set(prev_mat_bat_date_results[5:7])
			self.tab_bat_spin_day_var.set(prev_mat_bat_date_results[8:10])
			
		else:
			self.tab_bat_spin_year_var.set(False)
			self.tab_bat_spin_month_var.set(False)
			self.tab_bat_spin_day_var.set(False)
		
		prev_amount_bat_inputs = self.conn.execute('SELECT amount FROM mat_bat WHERE id = ?', (tab_bat_batch_id_select_result,))
		prev_amount_bat_inputs_results = prev_amount_bat_inputs.fetchone()[0]
		if prev_amount_bat_inputs_results:
			self.tab_bat_spin_amount_var.set(prev_amount_bat_inputs_results)
		else:
			self.tab_bat_spin_amount_var.set(False)
		
		mat_bat_units_exists = self.conn.execute('SELECT units FROM mat_bat WHERE id = ?', (tab_bat_batch_id_select_result,))
		mat_bat_units_exists_results = mat_bat_units_exists.fetchall()
		
		mat_bat_units = str(mat_bat_units_exists_results[0][0])
		if mat_bat_units:
			if mat_bat_units == '0':
				x = 0
			elif mat_bat_units == '1':
				x = 1
			elif mat_bat_units == '2':
				x = 2
			else:
				x = 3
		else:
			x = 3
		self.tab_bat_units_box.current(x)
		
		prev_sup = self.conn.execute('SELECT supplier FROM mat_bat WHERE id = ?', (tab_bat_batch_id_select_result,))
		prev_sup_result = prev_sup.fetchone()[0]
		if prev_sup_result:
			self.tab_bat_sup_var.set(prev_sup_result)
		else:
			self.tab_bat_sup_var.set(False)
			
		####
		mat_bat_finam_exists = self.conn.execute('SELECT pic_loc FROM mat_bat WHERE id = ?', (tab_bat_batch_id_select_result,))
		mat_bat_finam_exists_results = mat_bat_finam_exists.fetchall()
		finam = str(mat_bat_finam_exists_results[0][0])
		
		if finam:
			finam = finam
		else:
			finam = "blank.gif"	

		self.image_finam = finam
		
		if platform.system() == "Windows":
			photo = Image.open("..\\..\\_database\\deps\\material_batch_gifs\\%s" % (finam))
			photo = photo.resize((200, 200), Image.ANTIALIAS)
			photo_temp = photo.save("..\\..\\_database\\deps\\material_batch_gifs\\temp\\temp_photo.gif")
			photo = PhotoImage(file="..\\..\\_database\\deps\\material_batch_gifs\\temp\\temp_photo.gif")
		else:
			photo = Image.open("../../_database/deps/material_batch_gifs/%s" % (finam))
			photo = photo.resize((200, 200), Image.ANTIALIAS)
			photo_temp = photo.save("../../_database/deps/material_batch_gifs/temp/temp_photo.gif")
			photo = PhotoImage(file="../../_database/deps/material_batch_gifs/temp/temp_photo.gif")
		
		
		self.tab_bat_pic.configure(image=photo)	
		self.tab_bat_pic.image = photo
		self.tab_bat_units_box.current(x)	
	def commit_material_batch(self, *args):
		#Test if the batch code is unique? 
		#self.tab_bat_batch_codes_box.get()
		already_exists = self.conn.execute('SELECT batch_code FROM mat_bat WHERE batch_code = ?', (self.tab_bat_batch_codes_box.get(),))
		already_exists_results = already_exists.fetchall()
		
		if already_exists_results:
			self.mat_bat_status_var.set('Batch code exists already, rename and try again e.g. ...v2 or with date etc.')
		else:
			units = self.tab_bat_units_box.get()
			if units == 'Grams':
				units = '0'
			elif units == 'Millilitres':
				units = '1'
			elif units == 'Units':
				units = '2'

			if not self.image_finam:
				self.image_finam = "blank.gif"	
			
			mat_bat_dict = {
					'mat_id':self.tab_bat_mat_id_var.get(),
					'batch_code':self.tab_bat_batch_codes_box.get(),
					'prod_name':self.tab_bat_prod_name_var.get(),
					'prod_code':self.tab_bat_prod_code_var.get(),
					'supplier':self.tab_bat_sup_var.get(),
					'date_rec':'%s-%s-%s' % (self.tab_bat_spin_year_var.get(), self.tab_bat_spin_month_var.get(), self.tab_bat_spin_day_var.get()),
					'amount':self.tab_bat_spin_amount_var.get(),
					'units':units,
					'cost':self.tab_bat_spin_cost_var.get(),
					'pic_loc':self.image_finam,
					'state':0,
					}
			function_name = 'mat_bat'
			mat_bat_results = self.materials_mod(self, mat_bat_dict, function_name, self.conn)
			self.mat_bat_status_var.set(mat_bat_results[1])
			###clear the ref to the old picture
			try:
				del self.image_finam
			except:
				pass
			self.tab_bat_get_batches()
		
	def materials_tk(self, *args):
		self.tab_mat_frame0 = Frame(self.tab_materials, width=1300, height=800)
		self.tab_mat_frame0.grid()
		
		##Frame for the propeties etc of the material
		self.tab_mat_frame_prop = Frame(self.tab_mat_frame0, width=100, height=8)
		self.tab_mat_frame_prop.grid(row=1, column=0, sticky=W)

		####### material common name ######
		self.tab_mat_label_com_name = Label(self.tab_mat_frame_prop, text="Common Name:")
		self.tab_mat_label_com_name.grid(row=0, column=0, sticky=E)
		
		self.com_name_var = StringVar()
		self.tab_mat_entry_com_name = Entry(self.tab_mat_frame_prop, textvariable=self.com_name_var, width=75)
		self.tab_mat_entry_com_name.grid(row=0, column=1, sticky=W, columnspan=10)

		#### material full name ########
		self.tab_mat_label_full_name = Label(self.tab_mat_frame_prop, text="Full Name:")
		self.tab_mat_label_full_name.grid(row=1, column=0, sticky=E)
		
		self.full_name_var = StringVar()
		self.tab_mat_entry_full_name = Entry(self.tab_mat_frame_prop, textvariable=self.full_name_var, width=75)
		self.tab_mat_entry_full_name.grid(row=1, column=1, sticky=W)

		#### material short name #######
		self.tab_mat_label_short_name = Label(self.tab_mat_frame_prop, text="Short Name:")
		self.tab_mat_label_short_name.grid(row=2, column=0, sticky=E)
		
		self.short_name_var = StringVar()
		self.tab_mat_entry_short_name = Entry(self.tab_mat_frame_prop, textvariable=self.short_name_var, width=75)
		self.tab_mat_entry_short_name.grid(row=2, column=1, sticky=W)

		#### material other name #####
		self.tab_mat_label_other_name = Label(self.tab_mat_frame_prop, text="Other Name:")
		self.tab_mat_label_other_name.grid(row=3, column=0, sticky=E)
		
		self.other_name_var = StringVar()
		self.tab_mat_entry_other_name = Entry(self.tab_mat_frame_prop, textvariable=self.other_name_var, width=75)
		self.tab_mat_entry_other_name.grid(row=3, column=1, sticky=W)

		#### material formula #####
		self.tab_mat_label_formula = Label(self.tab_mat_frame_prop, text="Chemical Formula:")
		self.tab_mat_label_formula.grid(row=4, column=0, sticky=E)
		
		self.formula_var = StringVar()
		self.tab_mat_entry_formula = Entry(self.tab_mat_frame_prop, textvariable=self.formula_var, width=75)
		self.tab_mat_entry_formula.grid(row=4, column=1, sticky=W)

		
		#### mol mass ####
		self.tab_mat_label_mol = Label(self.tab_mat_frame_prop, text="Molar Mass(g/mol):")
		self.tab_mat_label_mol.grid(row=5, column=0, sticky=E)

		self.mol_spin_var = StringVar()
		self.tab_mat_spin_mol = Spinbox(self.tab_mat_frame_prop, from_=0, to=99999999, format="%.8f", increment=0.00000001, textvariable=self.mol_spin_var, width=20)
		self.tab_mat_spin_mol.grid(row=5, column=1, sticky=W)
		self.mol_spin_var.set(False)
		### form ####
		self.tab_mat_label_phys_form = Label(self.tab_mat_frame_prop, text="Form of Material:")
		self.tab_mat_label_phys_form.grid(row=6, column=0, sticky=E)
	
		self.tab_mat_form_list = ["Solid","Liquid","Gas"]
		self.phys_form_spin_var = StringVar()
		self.tab_mat_spin_phys_form = Combobox(self.tab_mat_frame_prop, textvariable=self.phys_form_spin_var)
		self.tab_mat_spin_phys_form['values'] = self.tab_mat_form_list
		self.tab_mat_spin_phys_form.bind('<<ComboboxSelected>>')
		self.tab_mat_spin_phys_form.grid(row=6, column=1, sticky=W)
		self.tab_mat_spin_phys_form.state(['readonly'])
		
		#### viscosity ####
		self.tab_mat_label_viscosity = Label(self.tab_mat_frame_prop, text="Viscosity (mPa.s):")
		self.tab_mat_label_viscosity.grid(row=7, column=0, sticky=E)

		self.viscosity_spin_var = StringVar()
		self.tab_mat_spin_viscosity = Spinbox(self.tab_mat_frame_prop, from_=0, to=99999999, format="%.2f", increment=0.01, textvariable=self.viscosity_spin_var, width=20)
		self.tab_mat_spin_viscosity.grid(row=7, column=1, sticky=W)
		self.viscosity_spin_var.set(False)
		#### HOMO ####
		self.tab_mat_label_homo = Label(self.tab_mat_frame_prop, text="HOMO(eV):")
		self.tab_mat_label_homo.grid(row=8, column=0, sticky=E)

		self.homo_spin_var = StringVar()
		self.tab_mat_spin_homo = Spinbox(self.tab_mat_frame_prop, from_=-99, to=99, format="%.2f", increment=0.01, textvariable=self.homo_spin_var, width=20)
		self.tab_mat_spin_homo.grid(row=8, column=1, sticky=W)
		self.homo_spin_var.set(False)
		#### LUMO ###
		self.tab_mat_label_lumo = Label(self.tab_mat_frame_prop, text="LUMO(eV):")
		self.tab_mat_label_lumo.grid(row=9, column=0, sticky=E)

		self.lumo_spin_var = StringVar()
		self.tab_mat_spin_lumo = Spinbox(self.tab_mat_frame_prop, from_=-99, to=99, format="%.2f", increment=0.01, textvariable=self.lumo_spin_var, width=20)
		self.tab_mat_spin_lumo.grid(row=9, column=1, sticky=W)
		self.lumo_spin_var.set(False)
		#### Work Function ####
		self.tab_mat_label_wf = Label(self.tab_mat_frame_prop, text="Work Function (eV):")
		self.tab_mat_label_wf.grid(row=10, column=0, sticky=E)

		self.wf_spin_var = StringVar()
		self.tab_mat_spin_wf = Spinbox(self.tab_mat_frame_prop, from_=-99, to=99, format="%.2f", increment=0.01, textvariable=self.wf_spin_var, width=20)
		self.tab_mat_spin_wf.grid(row=10, column=1, sticky=W)
		self.wf_spin_var.set(False)
		#### Colour ####
		self.tab_mat_label_colour = Label(self.tab_mat_frame_prop, text="Colour:")
		self.tab_mat_label_colour.grid(row=11, column=0, sticky=E)

		self.colour_var = StringVar()
		self.tab_mat_entry_colour = Entry(self.tab_mat_frame_prop, textvariable=self.colour_var)
		self.tab_mat_entry_colour.grid(row=11, column=1, sticky=W)
		self.colour_var.set(False)
		#### Density ####
		self.tab_mat_label_density = Label(self.tab_mat_frame_prop, text="Density (g/cm3):")
		self.tab_mat_label_density.grid(row=12, column=0, sticky=E)

		self.density_spin_var = StringVar()
		self.tab_mat_spin_density = Spinbox(self.tab_mat_frame_prop, from_=0, to=999, format="%.4f", increment=0.0001, textvariable=self.density_spin_var, width=20)
		self.tab_mat_spin_density.grid(row=12, column=1, sticky=W)
		self.density_spin_var.set(False)
		#### Poly Dispersity Index ####
		self.tab_mat_label_pdi = Label(self.tab_mat_frame_prop, text="PDI:")
		self.tab_mat_label_pdi.grid(row=13, column=0, sticky=E)

		self.pdi_spin_var = StringVar()
		self.tab_mat_spin_pdi = Spinbox(self.tab_mat_frame_prop, from_=0, to=99999, format="%.2f", increment=0.01, textvariable=self.pdi_spin_var, width=20)
		self.tab_mat_spin_pdi.grid(row=13, column=1, sticky=W)
		self.pdi_spin_var.set(False)
		#### Molecular Weight ####
		self.tab_mat_label_mw = Label(self.tab_mat_frame_prop, text="Molecular Weight:")
		self.tab_mat_label_mw.grid(row=14, column=0, sticky=E)

		self.mw_spin_var = StringVar()
		self.tab_mat_spin_mw = Spinbox(self.tab_mat_frame_prop, from_=0, to=9999999999, format="%.2f", increment=0.01, textvariable=self.mw_spin_var, width=20)
		self.tab_mat_spin_mw.grid(row=14, column=1, sticky=W)
		self.mw_spin_var.set(False)
		#### Molecular Number ####
		self.tab_mat_label_mn = Label(self.tab_mat_frame_prop, text="Molecular Number:")
		self.tab_mat_label_mn.grid(row=15, column=0, sticky=E)

		self.mn_spin_var = StringVar()
		self.tab_mat_spin_mn = Spinbox(self.tab_mat_frame_prop, from_=0, to=9999999999, format="%.2f", increment=0.01, textvariable=self.mn_spin_var, width=20)
		self.tab_mat_spin_mn.grid(row=15, column=1, sticky=W)
		self.mn_spin_var.set(False)
		###%weight form
		self.tab_mat_label_wtperc = Label(self.tab_mat_frame_prop, text="wt%:")
		self.tab_mat_label_wtperc.grid(row=16, column=0, sticky=E)

		self.wtperc_spin_var = StringVar()
		self.tab_mat_spin_wtperc = Spinbox(self.tab_mat_frame_prop, from_=0, to=100, format="%.2f", increment=0.01, textvariable=self.wtperc_spin_var, width=20)
		self.tab_mat_spin_wtperc.grid(row=16, column=1, sticky=W)
		self.wtperc_spin_var.set(100)
		
		#### material type #####
		self.tab_mat_label_type = Label(self.tab_mat_frame_prop, text="Material Type:")
		self.tab_mat_label_type.grid(row=17, column=0, sticky=E)
		
		self.tab_mat_type = StringVar()
		self.tab_mat_type_box = Combobox(self.tab_mat_frame_prop, textvariable=self.tab_mat_type)
		self.tab_mat_type_box.bind('<<ComboboxSelected>>')
		self.tab_mat_type_box['values'] = self.mat_type_list
		self.tab_mat_type_box.grid(row=17, column=1, sticky=W)
		self.tab_mat_type_box.state(['readonly'])
		
		### material database id #####
		self.tab_mat_label_id = Label(self.tab_mat_frame_prop, text="Material Database ID:")
		self.tab_mat_label_id.grid(row=18, column=0, sticky=E)
		
		self.id_update_materials = StringVar()
		self.tab_mat_label_id_update = Label(self.tab_mat_frame_prop, textvariable=self.id_update_materials, width=75)
		self.tab_mat_label_id_update.grid(row=18, column=1, sticky=W)
		
		## status message #####
		self.tab_mat_label_status = Label(self.tab_mat_frame_prop, text="Status:")
		self.tab_mat_label_status.grid(row=19, column=0, sticky=E)
		
		self.status_update_materials = StringVar()
		self.tab_mat_label_status_update = Label(self.tab_mat_frame_prop, textvariable=self.status_update_materials, width=75)
		self.tab_mat_label_status_update.grid(row=19, column=1, sticky=W)
		
		### commit material to database #####
		self.tab_mat_but_com_mat = Button(self.tab_mat_frame_prop, text="Commit Material to Database", command=self.commit_material)
		self.tab_mat_but_com_mat.grid(row=19, column=0, sticky=W)
		
		####Update a material#####
		self.tab_mat_but_upd_mat = Button(self.tab_mat_frame_prop, text="Update Material", command=self.material_update)
		self.tab_mat_but_upd_mat.grid(row=20, column=1)
		### Select Material #####
		self.tab_mat_label_prev = Label(self.tab_mat_frame_prop, text="Select Previous Material:")
		self.tab_mat_label_prev.grid(row=21, column=0, sticky=E)
		
		self.tab_mat_label_prev_name = StringVar()
		self.mat_prev_names_list = []
		self.tab_mat_prev_name_box = Combobox(self.tab_mat_frame_prop, textvariable=self.tab_mat_label_prev_name)
		self.tab_mat_prev_name_box.bind('<<ComboboxSelected>>', self.update_material_data)
		self.tab_mat_prev_name_box['values'] = self.mat_prev_names_list
		self.tab_mat_prev_name_box.grid(row=21, column=1, sticky=W)
		self.tab_mat_prev_name_box.state(['readonly'])
		self.tab_mat_populate_combo()
	
	def material_update(self,*args):
		#Should get this to check if the material has already been used in some way before, e.g. the phys form as part of a formulation 
		## get the id of the material ###
		mat_id_select = self.conn.execute('SELECT id FROM materials WHERE common_name = ?', (self.tab_mat_prev_name_box.get(),))
		mat_id_select_result = mat_id_select.fetchone()[0]
		
		#get the physical form of the material as an index
		form = self.tab_mat_spin_phys_form.get()
		if form == 'Solid':
			form_id = 0
		elif form == 'Liquid':
			form_id = 1
		elif form == 'Gas':
			form_id = 2
		else: 
			form_id = 0
			
		if mat_id_select_result:
			materials_dict = {
			'common_name': self.com_name_var.get(),
			'full_name': self.full_name_var.get(),
			'short_name': self.short_name_var.get(),
			'other_name': self.other_name_var.get(),
			'formula': self.formula_var.get(), 
			'mol_mass': self.mol_spin_var.get(), 
			'visc': self.viscosity_spin_var.get(), 
			'form': form_id,
			'homo': self.homo_spin_var.get(),
			'lumo': self.lumo_spin_var.get(),  
			'work_func': self.wf_spin_var.get(), 
			'colour': self.colour_var.get(), 
			'density': self.density_spin_var.get(), 
			'pdi': self.pdi_spin_var.get(),
			'mw': self.mw_spin_var.get(),
			'mn': self.mn_spin_var.get(), 
			'mat_type': self.tab_mat_type.get(),
			'wt_perc':self.wtperc_spin_var.get(),
			}
			function_name = 'materials'
			material_results = self.materials_update(self, materials_dict, function_name, self.conn,mat_id_select_result)
			self.status_update_materials.set(material_results[1])
			self.id_update_materials.set(material_results[0])
			self.tab_mat_populate_combo()
			self.update_form_mat_combo()
			self.tab_bat_populate_materials_list()
	def tab_bat_get_batches(self, *args):
		self.tab_bat_batch_codes_list = []
		self.tab_bat_batch_codes_box['values'] = self.tab_bat_batch_codes_list
		self.tab_bat_batch_codes_box.set('')
		self.tab_bat_prod_name_var.set('')
		self.tab_bat_prod_code_var.set('')
		self.tab_bat_sup_name_var.set('')
		self.tab_bat_sup_var.set('')
		self.tab_bat_spin_year_var.set(time.strftime("%Y"))
		self.tab_bat_spin_month_var.set(time.strftime("%m"))
		self.tab_bat_spin_day_var.set(time.strftime("%d"))
		self.tab_bat_spin_amount_var.set('')
		self.tab_bat_spin_cost_var.set('')
		self.tab_bat_units_box.current(3)
		####
		finam = "blank.gif"
		if platform.system() == "Windows":
			photo = Image.open("..\\..\\_database\\deps\\material_batch_gifs\\%s" % (finam))
			photo = photo.resize((200, 200), Image.ANTIALIAS)
			photo_temp = photo.save("..\\..\\_database\\deps\\material_batch_gifs\\temp\\temp_photo.gif")
			photo = PhotoImage(file="..\\..\\_database\\deps\\material_batch_gifs\\temp\\temp_photo.gif")
		else:
			photo = Image.open("../../_database/deps/material_batch_gifs/%s" % (finam))
			photo = photo.resize((200, 200), Image.ANTIALIAS)
			photo_temp = photo.save("../../_database/deps/material_batch_gifs/temp/temp_photo.gif")
			photo = PhotoImage(file="../../_database/deps/material_batch_gifs/temp/temp_photo.gif")
		
		
		self.tab_bat_pic.configure(image=photo)	
		self.tab_bat_pic.image = photo
		####
		## get the id of the material ###
		material_name = self.tab_bat_com_box.get()
		tab_bat_mat_id_select = self.conn.execute('SELECT id FROM materials WHERE common_name = ?', (material_name,))
		tab_bat_mat_id_select_result = tab_bat_mat_id_select.fetchone()[0]
		
		self.tab_bat_mat_id_var.set(tab_bat_mat_id_select_result)
		
		if self.tab_bat_check_var_complete.get() == True:
			state = 1
		else:
			state = 0
			
		tab_bat_batch_code_exists = self.conn.execute('SELECT batch_code FROM mat_bat WHERE mat_id = ? AND state = ?', (tab_bat_mat_id_select_result,state,))
		tab_bat_batch_code_exists_results = tab_bat_batch_code_exists.fetchall()
		if tab_bat_batch_code_exists_results:
			for i in tab_bat_batch_code_exists_results:
				self.tab_bat_batch_codes_list.append(i[0])
		self.tab_bat_batch_codes_box['values'] = list(sorted(self.tab_bat_batch_codes_list))	
	def tab_bat_populate_materials_list(self, *args):
		self.tab_bat_materials_names_list = []
		## get the common names of the materials ###
		tab_bat_id_select = self.conn.execute('SELECT common_name FROM materials')
		tab_bat_id_select_result = tab_bat_id_select.fetchall()
		
		if tab_bat_id_select_result:
			for i in tab_bat_id_select_result:
				self.tab_bat_materials_names_list.append(i[0])
			self.tab_bat_com_box['values'] = list(sorted(self.tab_bat_materials_names_list))
	def update_material_data(self, *args):	
		## get the id of the material ###
		mat_id_select = self.conn.execute('SELECT id FROM materials WHERE common_name = ?', (self.tab_mat_prev_name_box.get(),))
		mat_id_select_result = mat_id_select.fetchone()[0]
		
		
		### get the common name ####
		prev_com_name_mat_inputs = self.conn.execute('SELECT common_name FROM materials WHERE id = ?', (mat_id_select_result,))
		prev_com_name_mat_inputs_results = prev_com_name_mat_inputs.fetchone()[0]
		if prev_com_name_mat_inputs_results:
			self.com_name_var.set(prev_com_name_mat_inputs_results)
		else:
			self.com_name_var.set(False)
		
		### get the full name ####
		prev_full_name_mat_inputs = self.conn.execute('SELECT full_name FROM materials WHERE id = ?', (mat_id_select_result,))
		prev_full_name_mat_inputs_results = prev_full_name_mat_inputs.fetchone()[0]
		if prev_full_name_mat_inputs_results:
			self.full_name_var.set(prev_full_name_mat_inputs_results)
		else:
			self.full_name_var.set(False)
		
		### get the other name ####
		prev_other_name_mat_inputs = self.conn.execute('SELECT other_name FROM materials WHERE id = ?', (mat_id_select_result,))
		prev_other_name_mat_inputs_results = prev_other_name_mat_inputs.fetchone()[0]
		if prev_other_name_mat_inputs_results:
			self.other_name_var.set(prev_other_name_mat_inputs_results)
		else:
			self.other_name_var.set(False)
		
		### get the short name ####
		prev_short_name_mat_inputs = self.conn.execute('SELECT short_name FROM materials WHERE id = ?', (mat_id_select_result,))
		prev_short_name_mat_inputs_results = prev_short_name_mat_inputs.fetchone()[0]
		if prev_short_name_mat_inputs_results:
			self.short_name_var.set(prev_short_name_mat_inputs_results)
		else:
			self.short_name_var.set(False)
		
		### get the formula ####
		prev_formula_mat_inputs = self.conn.execute('SELECT formula FROM materials WHERE id = ?', (mat_id_select_result,))
		prev_formula_inputs_results = prev_formula_mat_inputs.fetchone()[0]
		if prev_formula_inputs_results:
			self.formula_var.set(prev_formula_inputs_results)
		else:
			self.formula_var.set(False)
			
		### get the mol_mass ####
		prev_mol_mass_mat_inputs = self.conn.execute('SELECT mol_mass FROM materials WHERE id = ?', (mat_id_select_result,))
		prev_mol_mass_mat_inputs_results = prev_mol_mass_mat_inputs.fetchone()[0]
		if prev_mol_mass_mat_inputs_results:
			self.mol_spin_var.set(prev_mol_mass_mat_inputs_results)
		else:
			self.mol_spin_var.set(False)
			
		### get the visc ####
		prev_visc_mat_inputs = self.conn.execute('SELECT visc FROM materials WHERE id = ?', (mat_id_select_result,))
		prev_visc_mat_inputs_results = prev_visc_mat_inputs.fetchone()[0]
		if prev_visc_mat_inputs_results:
			self.viscosity_spin_var.set(prev_visc_mat_inputs_results)
		else:
			self.viscosity_spin_var.set(False)
			
		### get the form ####
		prev_form_mat_inputs = self.conn.execute('SELECT form FROM materials WHERE id = ?', (mat_id_select_result,))
		prev_form_mat_inputs_results = prev_form_mat_inputs.fetchone()[0]
		#This should be improved incase something is wrong on database
		if prev_form_mat_inputs_results:
			self.tab_mat_spin_phys_form.current(prev_form_mat_inputs_results)
		else:
			self.tab_mat_spin_phys_form.current(0)
			
		### get the homo ####
		prev_homo_mat_inputs = self.conn.execute('SELECT homo FROM materials WHERE id = ?', (mat_id_select_result,))
		prev_homo_mat_inputs_results = prev_homo_mat_inputs.fetchone()[0]
		if prev_homo_mat_inputs_results:
			self.homo_spin_var.set(prev_homo_mat_inputs_results)
		else:
			self.homo_spin_var.set(False)
		
		### get the lumo ####
		prev_lumo_mat_inputs = self.conn.execute('SELECT lumo FROM materials WHERE id = ?', (mat_id_select_result,))
		prev_lumo_mat_inputs_results = prev_lumo_mat_inputs.fetchone()[0]
		if prev_lumo_mat_inputs_results:
			self.lumo_spin_var.set(prev_lumo_mat_inputs_results)
		else:
			self.lumo_spin_var.set(False)
			
		### get the wf ####
		prev_wf_mat_inputs = self.conn.execute('SELECT work_func FROM materials WHERE id = ?', (mat_id_select_result,))
		prev_wf_mat_inputs_results = prev_wf_mat_inputs.fetchone()[0]
		if prev_wf_mat_inputs_results:
			self.wf_spin_var.set(prev_wf_mat_inputs_results)
		else:
			self.wf_spin_var.set(False)
			
		### get the colour ####
		prev_colour_mat_inputs = self.conn.execute('SELECT colour FROM materials WHERE id = ?', (mat_id_select_result,))
		prev_colour_mat_inputs_results = prev_colour_mat_inputs.fetchone()[0]
		if prev_colour_mat_inputs_results:
			self.colour_var.set(prev_colour_mat_inputs_results)
		else:
			self.colour_var.set(False)
			
		### get the density ####
		prev_density_mat_inputs = self.conn.execute('SELECT density FROM materials WHERE id = ?', (mat_id_select_result,))
		prev_density_mat_inputs_results = prev_density_mat_inputs.fetchone()[0]
		if prev_density_mat_inputs_results:
			self.density_spin_var.set(prev_density_mat_inputs_results)
		else:
			self.density_spin_var.set(False)
			
		### get the pdi ####
		prev_pdi_mat_inputs = self.conn.execute('SELECT pdi FROM materials WHERE id = ?', (mat_id_select_result,))
		prev_pdi_mat_inputs_results = prev_pdi_mat_inputs.fetchone()[0]
		if prev_pdi_mat_inputs_results:
			self.pdi_spin_var.set(prev_pdi_mat_inputs_results)
		else:
			self.pdi_spin_var.set(False)
		
		### get the mw ####
		prev_mw_mat_inputs = self.conn.execute('SELECT mw FROM materials WHERE id = ?', (mat_id_select_result,))
		prev_mw_mat_inputs_results = prev_mw_mat_inputs.fetchone()[0]
		if prev_mw_mat_inputs_results:
			self.mw_spin_var.set(prev_mw_mat_inputs_results)
		else:
			self.mw_spin_var.set(False)	
		
		#get mn
		prev_mn_mat_inputs = self.conn.execute('SELECT mn FROM materials WHERE id = ?', (mat_id_select_result,))
		prev_mn_mat_inputs_results = prev_mn_mat_inputs.fetchone()[0]
		if prev_mn_mat_inputs_results:
			self.mn_spin_var.set(prev_mn_mat_inputs_results)
		else:
			self.mn_spin_var.set(False)
				
		### get the wt perc ####
		prev_wtperc_mat_inputs = self.conn.execute('SELECT wt_perc FROM materials WHERE id = ?', (mat_id_select_result,))
		prev_wtperc_mat_inputs_results = prev_wtperc_mat_inputs.fetchone()[0]
		if prev_wtperc_mat_inputs_results:
			self.wtperc_spin_var.set(prev_wtperc_mat_inputs_results)
		else:
			self.wtperc_spin_var.set(False)
			
		### get the mat_type ####
		prev_mat_type_mat_inputs = self.conn.execute('SELECT mat_type FROM materials WHERE id = ?', (mat_id_select_result,))
		prev_mat_type_mat_inputs_results = prev_mat_type_mat_inputs.fetchone()[0]
		if prev_mat_type_mat_inputs_results:
			self.tab_mat_type.set(prev_mat_type_mat_inputs_results)
		else:
			self.tab_mat_type.set(False)
		
		self.id_update_materials.set(mat_id_select_result)	
		#self.tab_bat_populate_materials_list()
		self.tab_bat_populate_materials_list()
	def tab_mat_clear_all(self,*args):
		###clear the ref to the old picture
		try:
			del self.image_finam
		except:
			pass
		self.com_name_var.set(False)
		self.full_name_var.set(False)
		self.short_name_var.set(False)
		self.other_name_var.set(False)
		self.formula_var.set(False)
		self.mol_spin_var.set(False)
		self.viscosity_spin_var.set(False)
		self.phys_form_spin_var.set(False)
		self.homo_spin_var.set(False)
		self.lumo_spin_var.set(False)
		self.wf_spin_var.set(False)
		self.colour_var.set(False)
		self.density_spin_var.set(False)
		self.pdi_spin_var.set(False)
		self.mw_spin_var.set(False)
		self.mn_spin_var.set(False)
		self.tab_mat_type.set(False)
		
		####
		finam = "blank.gif"
		if platform.system() == "Windows":
			photo = Image.open("..\\..\\_database\\deps\\material_batch_gifs\\%s" % (finam))
			photo = photo.resize((200, 200), Image.ANTIALIAS)
			photo_temp = photo.save("..\\..\\_database\\deps\\material_batch_gifs\\temp\\temp_photo.gif")
			photo = PhotoImage(file="..\\..\\_database\\deps\\material_batch_gifs\\temp\\temp_photo.gif")
		else:
			photo = Image.open("../../_database/deps/material_batch_gifs/%s" % (finam))
			photo = photo.resize((200, 200), Image.ANTIALIAS)
			photo_temp = photo.save("../../_database/deps/material_batch_gifs/temp/temp_photo.gif")
			photo = PhotoImage(file="../../_database/deps/material_batch_gifs/temp/temp_photo.gif")
		
		
		self.tab_bat_pic.configure(image=photo)	
		self.tab_bat_pic.image = photo
		####
	def tab_mat_populate_combo(self, *args):
		self.mat_prev_names_list = []
		mat_prev_mat_exists = self.conn.execute('SELECT common_name FROM materials')
		mat_prev_mat_exists_results = mat_prev_mat_exists.fetchall()
		#check if anything was returned from the search and if so add to the dropdown list
		if str(mat_prev_mat_exists_results) == None:
			pass
		else:	
			for i in mat_prev_mat_exists_results:
				if i[0]:
					self.mat_prev_names_list.append(i[0])
			self.mat_prev_names_list.sort()		
			self.tab_mat_prev_name_box['values'] = list(sorted(self.mat_prev_names_list))
	def commit_material(self, *args):
		#Get the material physical form as an id
		form = self.tab_mat_spin_phys_form.get()
		if form == 'Solid':
			form_id = 0
		elif form == 'Liquid':
			form_id = 1
		elif form == 'Gas':
			form_id = 2
		else: 
			form_id = 0
				
		materials_dict = {
			'common_name': self.com_name_var.get(),
			'full_name': self.full_name_var.get(),
			'short_name': self.short_name_var.get(),
			'other_name': self.other_name_var.get(),
			'formula': self.formula_var.get(), 
			'mol_mass': self.mol_spin_var.get(), 
			'visc': self.viscosity_spin_var.get(), 
			'form': form_id,
			'homo': self.homo_spin_var.get(),
			'lumo': self.lumo_spin_var.get(),  
			'work_func': self.wf_spin_var.get(), 
			'colour': self.colour_var.get(), 
			'density': self.density_spin_var.get(), 
			'pdi': self.pdi_spin_var.get(),
			'mw': self.mw_spin_var.get(),
			'mn': self.mn_spin_var.get(), 
			'mat_type': self.tab_mat_type.get(),
			'wt_perc':self.wtperc_spin_var.get(),
			}
		function_name = 'materials'
		material_results = self.materials_mod(self, materials_dict, function_name, self.conn)
		self.status_update_materials.set(material_results[1])
		self.id_update_materials.set(material_results[0])
		self.tab_mat_populate_combo()
		self.update_form_mat_combo()
		self.tab_bat_populate_materials_list()
		
		self.tab_mat_clear_all()
		
	def formulation_tk(self, *args):
		###########################################################################
		#The Formulations tab
		self.tab_form_frame0 = Frame(self.tab_form, width=1300, height=600)
		self.tab_form_frame0.grid()
		
		self.tab_form_frame_name = Frame(self.tab_form_frame0, width=100, height=8)
		self.tab_form_frame_name.grid(row=1, column=0, columnspan=5, sticky=W)


		self.tab_form_label_prev_name = Label(self.tab_form_frame_name, text="Previous Formulations:")
		self.tab_form_label_prev_name.grid(row=0, column=0, sticky=E)

		self.tab_form_label_prev_name = StringVar()
		self.prev_names = []
		self.tab_form_prev_name_box = Combobox(self.tab_form_frame_name, textvariable=self.tab_form_label_prev_name, width=80)
		self.tab_form_prev_name_box.bind('<<ComboboxSelected>>', self.update_formulation_data)
		self.tab_form_prev_name_box['values'] = self.prev_names
		self.tab_form_prev_name_box.grid(row=0, column=1, sticky=W)
		self.tab_form_prev_name_box.state(['readonly'])
		
		self.tab_form_check_var_complete = IntVar()
		self.tab_form_check_complete = Checkbutton(self.tab_form_frame_name, text="Show Complete", variable=self.tab_form_check_var_complete,command=self.tab_form_update_formulation_names)
		self.tab_form_check_complete.grid(row=0, column=2, sticky=W)
		
		self.tab_form_but_complete = Button(self.tab_form_frame_name, text='Switch Complete / Remaining', command=self.mark_formulation_complete)
		self.tab_form_but_complete.grid(row=0, column=3)
		
		self.tab_form_label_name = Label(self.tab_form_frame_name, text="Formulation Name:")
		self.tab_form_label_name.grid(row=1, column=0, sticky=E)
		
		self.var_form_name = StringVar()
		self.tab_form_entry_name = Entry(self.tab_form_frame_name, textvariable=self.var_form_name, width=100)
		self.tab_form_entry_name.grid(row=1, column=1, columnspan=5, sticky=W)
		
		self.tab_form_frame_date = Frame(self.tab_form_frame0, width=100, height=8)
		self.tab_form_frame_date.grid(row=2, column=0, columnspan=5, sticky=W)



		self.tab_form_frame_selc = Frame(self.tab_form_frame0, width=100, height=8)
		self.tab_form_frame_selc.grid(row=4, column=0, columnspan=10, sticky=W)

		self.tab_form_label_date = Label(self.tab_form_frame_date, text="Date Made:")
		self.tab_form_label_date.grid(row=0, column=0, sticky=E)

		self.var_spin_year = StringVar()
		self.tab_form_spin_year = Spinbox(self.tab_form_frame_date, from_=2000, to=2050, format="%04.0f", textvariable=self.var_spin_year, width=6)
		self.tab_form_spin_year.grid(row=0, column=1, sticky=W)
		self.var_spin_year.set(time.strftime("%Y"))

		self.var_spin_month = StringVar()
		self.tab_form_spin_month = Spinbox(self.tab_form_frame_date, from_=01, to=12, format="%02.0f", textvariable=self.var_spin_month, width=4)
		self.tab_form_spin_month.grid(row=0, column=2, sticky=W)
		self.var_spin_month.set(time.strftime("%m"))

		self.var_spin_day = StringVar()
		self.tab_form_spin_day = Spinbox(self.tab_form_frame_date, from_=01, to=31, format="%02.0f", textvariable=self.var_spin_day, width=4)
		self.tab_form_spin_day.grid(row=0, column=3, sticky=W)
		self.var_spin_day.set(time.strftime("%d"))

		#######
		#######
		#######
		self.tab_form_frame_visc = LabelFrame(self.tab_form_frame0, width=100, height=8,text='Prep:')
		self.tab_form_frame_visc.grid(row=3, column=0, columnspan=5, sticky=W)
		
		self.tab_form_label_prep_atm = Label(self.tab_form_frame_visc, text="Solids Prep Atmosphere:")
		self.tab_form_label_prep_atm.grid(row=0, column=0, sticky=W)
		
		self.atm_list = ["Air","Nitrogen","Argon","Helium","Oxygen"]
		self.prep_atm_var = StringVar()
		self.prep_atm_box = Combobox(self.tab_form_frame_visc, textvariable=self.prep_atm_var)
		#self.prep_atm_box.bind('<<ComboboxSelected>>')
		self.prep_atm_box['values'] = self.atm_list
		self.prep_atm_box.grid(row=0, column=1)
		self.prep_atm_box.state(['readonly'])
				
		self.tab_form_label_liq_prep_atm = Label(self.tab_form_frame_visc, text="Liquids Prep Atmosphere:")
		self.tab_form_label_liq_prep_atm.grid(row=0, column=2, sticky=E)
		
		self.prep_atm_liq_var = StringVar()
		self.prep_atm_liq_box = Combobox(self.tab_form_frame_visc, textvariable=self.prep_atm_liq_var)
		#self.prep_atm_box.bind('<<ComboboxSelected>>')
		self.prep_atm_liq_box['values'] = self.atm_list
		self.prep_atm_liq_box.grid(row=0, column=3, sticky=W)
		self.prep_atm_liq_box.state(['readonly'])
		
		self.tab_form_check_filter_var = IntVar()
		self.tab_form_check_filt = Checkbutton(self.tab_form_frame_visc, text="Filtered?", variable=self.tab_form_check_filter_var)
		self.tab_form_check_filt.grid(row=1, column=0, sticky=W)
		
		self.tab_form_filt_list = ["None","PTFE","PVDF","Cellulose","GF"]
		self.tab_form_filt_var = StringVar()
		self.tab_form_filt_box = Combobox(self.tab_form_frame_visc, textvariable=self.tab_form_filt_var)
		self.tab_form_filt_box['values'] = self.tab_form_filt_list
		self.tab_form_filt_box.grid(row=1, column=1)
		self.tab_form_filt_box.state(['readonly'])
		
		self.tab_form_label_filt = Label(self.tab_form_frame_visc, text="Filter Size (um):")
		self.tab_form_label_filt.grid(row=1, column=2, sticky=E)
		
		self.var_spin_filt = StringVar()
		self.tab_form_spin_filt = Spinbox(self.tab_form_frame_visc, from_=0, to=999999, format="%.3f", increment=0.001, textvariable=self.var_spin_filt, width=10)
		self.tab_form_spin_filt.grid(row=1, column=3, sticky=W)
		

		
		self.tab_form_check_var = IntVar()
		self.tab_form_check_heat = Checkbutton(self.tab_form_frame_visc, text="Heated", variable=self.tab_form_check_var)
		self.tab_form_check_heat.grid(row=3, column=0, sticky=W)
		
		self.tab_form_label_heat_temp = Label(self.tab_form_frame_visc, text="Heat Temp (decC):")
		self.tab_form_label_heat_temp.grid(row=2, column=1, sticky=W)

		self.tab_form_label_heat_time = Label(self.tab_form_frame_visc, text="Heat Time (min):")
		self.tab_form_label_heat_time.grid(row=2, column=2, sticky=W)

		self.var_spin_heat_temp = StringVar()
		self.tab_form_spin_heat_temp = Spinbox(self.tab_form_frame_visc, from_=0, to=999999, textvariable=self.var_spin_heat_temp, width=20)
		self.tab_form_spin_heat_temp.grid(row=3, column=1, sticky=W)
		
		self.var_spin_heat_time = StringVar()
		self.tab_form_spin_heat_time = Spinbox(self.tab_form_frame_visc, from_=0, to=999999, textvariable=self.var_spin_heat_time, width=20)
		self.tab_form_spin_heat_time.grid(row=3, column=2, sticky=W)

		self.tab_form_label_heat_atm = Label(self.tab_form_frame_visc, text="Heat Atmosphere:")
		self.tab_form_label_heat_atm.grid(row=2, column=3, sticky=W)
		
		self.heat_atm_var = StringVar()
		self.heat_atm_box = Combobox(self.tab_form_frame_visc, textvariable=self.heat_atm_var)
		#self.heat_atm_box.bind('<<ComboboxSelected>>')
		self.heat_atm_box['values'] = self.atm_list
		self.heat_atm_box.grid(row=3, column=3)
		self.heat_atm_box.state(['readonly'])

		self.tab_form_check_var_ultra = IntVar()
		self.tab_form_check_ultra = Checkbutton(self.tab_form_frame_visc, text="Sonicated", variable=self.tab_form_check_var_ultra)
		self.tab_form_check_ultra.grid(row=5, column=0, sticky=W)
		
		self.tab_form_label_ultra_temp = Label(self.tab_form_frame_visc, text="Sonication Temp (decC):")
		self.tab_form_label_ultra_temp.grid(row=4, column=1, sticky=W)

		self.tab_form_label_ultra_power = Label(self.tab_form_frame_visc, text="Sonication Power:")
		self.tab_form_label_ultra_power.grid(row=4, column=3, sticky=W)

		self.tab_form_label_ultra_time = Label(self.tab_form_frame_visc, text="Sonication Time (min):")
		self.tab_form_label_ultra_time.grid(row=4, column=2, sticky=W)

		self.var_spin_ultra_temp = StringVar()
		self.tab_form_spin_ultra_temp = Spinbox(self.tab_form_frame_visc, from_=0, to=999999, textvariable=self.var_spin_ultra_temp, width=20)
		self.tab_form_spin_ultra_temp.grid(row=5, column=1, sticky=W)
		
		self.var_spin_ultra_time = StringVar()
		self.tab_form_spin_ultra_time = Spinbox(self.tab_form_frame_visc, from_=0, to=999999, textvariable=self.var_spin_ultra_time, width=20)
		self.tab_form_spin_ultra_time.grid(row=5, column=2, sticky=W)

		self.var_spin_ultra_power = StringVar()
		self.tab_form_spin_ultra_power = Spinbox(self.tab_form_frame_visc, from_=0, to=999999, textvariable=self.var_spin_ultra_power, width=20)
		self.tab_form_spin_ultra_power.grid(row=5, column=3, sticky=W)
		
		self.tab_form_label_visc = Label(self.tab_form_frame_visc, text="Viscosity (mPa.s):")
		self.tab_form_label_visc.grid(row=6, column=0,sticky=E)

		self.var_spin_visc = StringVar()
		self.tab_form_spin_visc = Spinbox(self.tab_form_frame_visc, from_=0, to=999999, format="%.3f", increment=0.001, textvariable=self.var_spin_visc, width=10)
		self.tab_form_spin_visc.grid(row=6, column=1, sticky=W)

		self.tab_form_label_surten = Label(self.tab_form_frame_visc, text='Surface Tension (mN/m):')
		self.tab_form_label_surten.grid(row=6, column=2,sticky=E)
		
		self.var_spin_surten = StringVar()
		self.tab_form_spin_surten = Spinbox(self.tab_form_frame_visc, from_=0, to=999999, format="%.3f", increment=0.001, textvariable=self.var_spin_surten, width=10)
		self.tab_form_spin_surten.grid(row=6, column=3, sticky=W)

		self.tab_form_label_waste = Label(self.tab_form_frame_visc, text='Waste Stream:')
		self.tab_form_label_waste.grid(row=7, column=0,sticky=E)
		
		self.tab_form_waste_list = ["Special","Non-Halogenated","Halogenated","Acid","Base","Aqueous"]
		self.tab_form_waste_var = StringVar()
		self.tab_form_waste_box = Combobox(self.tab_form_frame_visc, textvariable=self.tab_form_waste_var)
		self.tab_form_waste_box['values'] = self.tab_form_waste_list
		self.tab_form_waste_box.grid(row=7, column=1,sticky=W)
		self.tab_form_waste_box.state(['readonly'])
		
		
		self.tab_form_label_notes = Label(self.tab_form_frame_visc, text="Formulation Notes:")
		self.tab_form_label_notes.grid(row=8, column=0, sticky=E)
		
		self.tab_form_text_notes = Text(self.tab_form_frame_visc, width=100, height=8)
		self.tab_form_text_notes.grid(row=8, column=1, columnspan=5, sticky=W)	
		######
		######
		######
				
		self.tab_form_label_mat = Label(self.tab_form_frame_selc, text="Material Common Name")
		self.tab_form_label_mat.grid(row=0, column=0, sticky=W)

		self.tab_form_label_bat = Label(self.tab_form_frame_selc, text="Batch Code")
		self.tab_form_label_bat.grid(row=0, column=1, sticky=W)

		self.tab_form_label_quan = Label(self.tab_form_frame_selc, text="Quantity")
		self.tab_form_label_quan.grid(row=0, column=2, sticky=W)

		self.var_lab_unit = StringVar()
		self.tab_form_label_unit = Label(self.tab_form_frame_selc, textvariable=self.var_lab_unit, width=10)
		self.tab_form_label_unit.grid(row=1, column=3, sticky=W)

		self.tab_form_but_add = Button(self.tab_form_frame_selc, text='Add to formulation', command=self.add_to_formulation)
		self.tab_form_but_add.grid(row=1, column=4)

		#a list for the material common names in the database
		self.material_names = []
		#poll the database for a list of materials
		self.mat_exists = self.conn.execute('SELECT common_name, id FROM materials')
		self.mat_exists_results = self.mat_exists.fetchall()
		#check if anything was returned from the search and if so add to the dropdown list
		if self.mat_exists_results:
			for i in self.mat_exists_results:
				self.material_names.append(i[0])
			self.material_names = list(sorted(self.material_names))
		self.material = StringVar()
		self.material_box = Combobox(self.tab_form_frame_selc, textvariable=self.material)
		self.material_box.bind('<<ComboboxSelected>>', self.mat_batch_update)
		self.material_box['values'] = self.material_names
		self.material_box.grid(row=1, column=0)
		self.material_box.state(['readonly'])
		

		#a list for the material batch names in the database
		self.batch_names = []

		self.batch = StringVar()
		self.batch_box = Combobox(self.tab_form_frame_selc, textvariable=self.batch)
		self.batch_box.bind('<<ComboboxSelected>>', self.mat_unit_update)
		self.batch_box['values'] = self.batch_names
		self.batch_box.grid(row=1, column=1)
		self.batch_box.state(['readonly'])

		self.var_spin_quan = StringVar()
		self.tab_form_spin_quan = Spinbox(self.tab_form_frame_selc, from_=0, to=99999999, format="%.8f", increment=0.00000001, textvariable=self.var_spin_quan, width=20)
		self.tab_form_spin_quan.grid(row=1, column=2, sticky=W)
		self.var_spin_quan.set('0')


		############side by side list boxes to display the materials in the formulation
		self.tab_form_frame_list = Frame(self.tab_form_frame0)	
		self.tab_form_frame_list.grid(row=5, column=0, columnspan=10, sticky=W)
		
		self.tab_form_listbox_vsb = Scrollbar(self.tab_form_frame_list)
		self.tab_form_listbox_vsb.grid(row=1, column=4, sticky=N+S)

		self.tab_form_listbox_mat_name = Label(self.tab_form_frame_list, text='Materials:')
		self.tab_form_listbox_mat_name.grid(row=0, column=0)
		self.tab_form_listbox_mat = Listbox(self.tab_form_frame_list, yscrollcommand=self.tab_form_listbox_vsb.set, exportselection=False)
		self.tab_form_listbox_mat.grid(row=1, column=0)
		self.tab_form_listbox_mat.bind('<<ListboxSelect>>', self.list_box_selection_mat)
		
		self.tab_form_listbox_bat_name = Label(self.tab_form_frame_list, text='Material Batches:')
		self.tab_form_listbox_bat_name.grid(row=0, column=1)
		self.tab_form_listbox_bat = Listbox(self.tab_form_frame_list, yscrollcommand=self.tab_form_listbox_vsb.set, exportselection=False)
		self.tab_form_listbox_bat.grid(row=1, column=1)
		self.tab_form_listbox_bat.bind('<<ListboxSelect>>', self.list_box_selection_bat)

		self.tab_form_listbox_quan_name = Label(self.tab_form_frame_list, text='Quantity:')
		self.tab_form_listbox_quan_name.grid(row=0, column=2)
		self.tab_form_listbox_quan = Listbox(self.tab_form_frame_list, yscrollcommand=self.tab_form_listbox_vsb.set, exportselection=False)
		self.tab_form_listbox_quan.grid(row=1, column=2)
		self.tab_form_listbox_quan.bind('<<ListboxSelect>>', self.list_box_selection_quan)

		self.tab_form_listbox_unit_name = Label(self.tab_form_frame_list, text='Units:')
		self.tab_form_listbox_unit_name.grid(row=0, column=3)
		self.tab_form_listbox_unit = Listbox(self.tab_form_frame_list, yscrollcommand=self.tab_form_listbox_vsb.set, exportselection=False)
		self.tab_form_listbox_unit.grid(row=1, column=3)
		self.tab_form_listbox_unit.bind('<<ListboxSelect>>', self.list_box_selection_unit)

		self.tab_form_listbox_vsb.config(command=self.multi_list_vsb)
	
		##to remove items from a formulation
		self.tab_form_but_remove = Button(self.tab_form_frame0, text='Remove Selection from Formulation', command=self.remove_from_formulation)
		self.tab_form_but_remove.grid(row=6, column=0, sticky=W)
		#commit formulation to database
		self.tab_form_but_commit = Button(self.tab_form_frame0, text='Commit New Formulation', command=self.commit_formulation)
		self.tab_form_but_commit.grid(row=6, column=1, sticky=W)
		
		self.tab_form_label_status = Label(self.tab_form_frame_list, text="Status:")
		self.tab_form_label_status.grid(row=2, column=0, sticky=W)

		self.tab_form_label_status_update_var = StringVar()
		self.tab_form_label_status_update = Label(self.tab_form_frame_list, textvariable=self.tab_form_label_status_update_var)
		self.tab_form_label_status_update.grid(row=2, column=1, sticky=W, columnspan=10)

	
		
		
		self.tab_form_but_print = Button(self.tab_form_frame0, text='Print Label', command=self.tab_form_print)
		self.tab_form_but_print.grid(row=7, column=0, sticky=W)
		
		self.tab_form_update_formulation_names()
		#self.tab_form_but_read = Button(self.tab_form_frame0, text='Read Barcode', command=self.tab_form_read)
		#self.tab_form_but_read.grid(row=7, column=1, sticky=W)
	
	def tab_form_update_formulation_names(self, *args):
		self.tab_form_prev_name_box['values'] = []
		prev_names = []
		#check if to include complete formulations or not
		if self.tab_form_check_var_complete.get() == 1:
			prev_form_exists = self.conn.execute('SELECT form_name FROM formulations WHERE state = 1',)
			prev_form_exists_results = prev_form_exists.fetchall()
			
			if prev_form_exists_results:
				for i in prev_form_exists_results:
					if i[0]:
						prev_names.append(i[0])
				self.tab_form_prev_name_box['values'] = list(reversed(list(sorted(set(i for i in prev_names)))))
			
		else:
			prev_form_exists = self.conn.execute('SELECT form_name FROM formulations WHERE state = 0',)
			prev_form_exists_results = prev_form_exists.fetchall()
			#check if anything was returned from the search and if so add to the dropdown list
			if prev_form_exists_results:
				for i in prev_form_exists_results:
					if i[0]:
						prev_names.append(i[0])
				self.tab_form_prev_name_box['values'] = list(reversed(list(sorted(set(i for i in prev_names)))))
			
	def mark_formulation_complete(self, *args):
		#get the formulation id
		form_id_select = self.conn.execute('SELECT form_id FROM formulations WHERE form_name = ?', (self.tab_form_prev_name_box.get(),))
		form_id_select_result = form_id_select.fetchone()[0]
		#Mark it read in the database
		if str(form_id_select_result):
			#select the state for that form_id, should be set the same for all rows contianing that id so just get the top one
			state_id_select = self.conn.execute('SELECT state FROM formulations WHERE form_id = ?', (form_id_select_result,))
			state_id_select_result = state_id_select.fetchone()[0]
			if state_id_select_result == 1:
				state = 0
			else:
				state = 1
			self.conn.execute('UPDATE formulations SET state = ? WHERE form_id = ?',(state, form_id_select_result,));
			self.conn.commit()
		#Re-show do the selection at start
		self.tab_form_update_formulation_names()
	def tab_form_read(self, *args):
		pass
	def tab_form_print(self, *args):
		#form_name should be unique...
		form_id_select = self.conn.execute('SELECT form_id FROM formulations WHERE form_name = ?', (self.var_form_name.get(),))
		form_id_select_result = form_id_select.fetchone()[0]
		#Does that still give the first result only?
		
		qr = """^XA^FO20,50^BQ,2,2^FDQA,""" + 'ID: %s, Date: %s-%s-%s' % (form_id_select_result,self.tab_form_spin_year.get(), self.tab_form_spin_month.get(), self.tab_form_spin_day.get())+ """^FS"""

		line0 = """^FO10,20^FD"""+"%s" % (str(self.var_form_name.get())[0:25])+"""^FS"""
		line1 = """^FO10,30^FD"""+"%s" % (str(self.var_form_name.get())[25:50])+"""^FS"""
		line2 = """^FO10,40^FD"""+"%s" % (str(self.var_form_name.get())[50:75])+"""^FS"""
		line3 = """^FO90,55^FD"""+"ID %s" % (form_id_select_result)+"""^FS"""
		line4 = """^FO90,65^FD"""+"Date %s%s%s" % (self.tab_form_spin_year.get(), self.tab_form_spin_month.get(), self.tab_form_spin_day.get())+"""^FS"""
		line5 = """^FO90,75^FD"""+"Waste %s" % (str(self.tab_form_waste_box.get())[0:8])+"""^FS"""
		lab_end = """^XZ"""
		
		label = qr+line0+line1+line2+line3+line4+line5+lab_end
		self.print_lab(label,self.printer)
	def update_form_mat_combo(self, *args):
		#a list for the material common names in the database
		self.material_names = []
		#poll the database for a list of materials
		mat_exists = self.conn.execute('SELECT common_name, id FROM materials')
		mat_exists_results = mat_exists.fetchall()
		#check if anything was returned from the search and if so add to the dropdown list
		if mat_exists_results:
			for i in mat_exists_results:
				self.material_names.append(i[0])
		self.material_box['values'] = list(sorted(self.material_names))		
	def commit_formulation(self):
		##The formulation is made up of material batches prepared with certain sets of conditions
		##These are split up over two tables
		##One listing the formulation conditions giving a form_cond_id
		#The other containing the form_id and the corresponding mat_bat_ids with the corresponding form_cond_id
		
		formulation_conds_inputs_dict = {}
		formulation_conds_inputs_dict = {
					'solids_atm' : '%s' % self.prep_atm_var.get(),
					'liquids_atm' : '%s' % self.prep_atm_liq_var.get(),
					}
		
		if self.tab_form_check_filter_var.get():
			formulation_conds_inputs_dict['filter'] = self.tab_form_filt_var.get()
			formulation_conds_inputs_dict['filt_size'] = self.var_spin_filt.get()
		if self.tab_form_check_var.get():
			formulation_conds_inputs_dict['temp'] = self.tab_form_spin_heat_temp.get()
			formulation_conds_inputs_dict['time_temp'] = self.tab_form_spin_heat_time.get()
			formulation_conds_inputs_dict['heat_atm'] = self.heat_atm_var.get()
		if self.tab_form_check_var_ultra.get():
			formulation_conds_inputs_dict['ultra_temp'] = self.tab_form_spin_ultra_temp.get()
			formulation_conds_inputs_dict['ultra_time'] = self.tab_form_spin_ultra_time.get()
			formulation_conds_inputs_dict['ultra_power'] = self.tab_form_spin_ultra_power.get()
		
		#A dict for the properties of the formulaton
		formulation_props_inputs_dict = {}
		formulation_props_inputs_dict = {'form_name' : '%s' % self.var_form_name.get(), 
					'date_made' : '%s-%s-%s' % (self.tab_form_spin_year.get(), self.tab_form_spin_month.get(), self.tab_form_spin_day.get()),
					'visc' : '%s' % self.tab_form_spin_visc.get(),
					'surten' : '%s' % self.tab_form_spin_surten.get(),
					'waste_stream' : '%s' % self.tab_form_waste_box.get(),
					'form_notes' : '%s' % self.tab_form_text_notes.get(1.0,END),
					}
					
		formulation_inputs_dict = {}
		formulation_inputs_dict = {
		'form_name' : '%s' % self.var_form_name.get(),
		'state':'0',
		}
		#Each row from the gui will be a new row in the table with a common form_id
		#Make a list of lists for the mat, bat, quan
		lst_form = []
		for index, i in enumerate(self.tab_form_listbox_mat.get(0, END)):
			lst_form.append([])
			material_id_exists = self.conn.execute('SELECT id FROM materials WHERE common_name = ?', (i,))
			material_id_exists_results = material_id_exists.fetchone()[0] 
			lst_form[index].append(str(material_id_exists_results))

		for index, i in enumerate(self.tab_form_listbox_bat.get(0, END)):
			batch_id_exists = self.conn.execute('SELECT id FROM mat_bat WHERE batch_code = ?', (i,))
			batch_id_exists_results = batch_id_exists.fetchone()[0]
			lst_form[index].append(batch_id_exists_results)

		for index, i in enumerate(self.tab_form_listbox_quan.get(0, END)):
			lst_form[index].append(i)
		
		formulation_inputs_dict['lst'] = lst_form
		form_id = self.formulations_mod(formulation_conds_inputs_dict, formulation_props_inputs_dict, formulation_inputs_dict, self.conn)
		if not form_id:
			self.tab_form_label_status_update_var.set('Formulation name not unique, rename and commit again.')
		else:
			self.tab_form_label_status_update_var.set('New formulation id is %s' % form_id)	
		self.tab_form_box_prev_func()	
		self.tab_layers_get_form_names()
		self.tab_form_update_formulation_names()
	def multi_list_vsb(self, *args):
		self.tab_form_listbox_mat.yview(*args)
		self.tab_form_listbox_bat.yview(*args)
		self.tab_form_listbox_quan.yview(*args)	
		self.tab_form_listbox_unit.yview(*args)

	def mat_batch_update(self, *args):
		self.batch_box.set('')
		self.var_spin_quan.set(0)
		self.var_lab_unit.set(0)
		#empty the batch name list before updating
		self.batch_names = []
		self.batch_box['values'] = []
		#get the material selected from the combobox
		material_selected = self.material_box.get()	
		#poll the database for the id of that material common name
		mat_select = self.conn.execute('SELECT id FROM materials WHERE common_name = ?', (material_selected,))
		mat_select_id = mat_select.fetchone()[0]
		#poll the database for mat_bat batch_codes for that material id. 
		bat_exists = self.conn.execute('SELECT batch_code FROM mat_bat WHERE mat_id = ?', (mat_select_id,))
		bat_exists_results = bat_exists.fetchall()
		#check if anything was returned from the search and if so add to the dropdown list
		if bat_exists_results:
			for i in bat_exists_results:
				self.batch_names.append(i[0])
			self.batch_box['values'] = self.batch_names

	def mat_unit_update(self, *args):	
		#get the batch_code selected from the combobox
		batch_selected = self.batch_box.get()
		com_name = self.material_box.get()
		#get the mat_id from the material common name 
		name_select = self.conn.execute('SELECT id FROM materials WHERE common_name = ?', (com_name,))
		name_select_id = name_select.fetchone()[0]
		#poll the database for the id of that batch_code
		unit_select = self.conn.execute('SELECT id FROM mat_bat WHERE batch_code = ? AND mat_id =?', (batch_selected, name_select_id,))
		unit_select_id = unit_select.fetchone()[0]
		#poll the database for mat_bat units for that material id. 
		units_exists = self.conn.execute('SELECT units FROM mat_bat WHERE id = ?', (unit_select_id,))
		units_exists_results = units_exists.fetchall()
		
		units = str(units_exists_results[0][0])
		if units:
			if units == '0':
				x = '(grams)'
			elif units == '1':
				x = '(millilitres)'
			elif units == '2':
				x = '(units)'
			else:
		 		x = '(error)'
		else:
		 	x = '(error)'	
		self.var_lab_unit.set('%s' % x)
			
	def update_layers_canvas_scroll(self, *args):
		self.tab_layers_canvas.config(scrollregion=self.tab_layers_canvas.bbox(ALL))

	def add_to_formulation(self):
		self.batch_list_name = self.batch_box.get()
		self.material_list_name = self.material_box.get()
		self.unit_list_name = self.var_lab_unit.get()
		self.quan_list_name = self.var_spin_quan.get()
		
		if self.batch_list_name and self.material_list_name and self.unit_list_name and self.quan_list_name:
			self.tab_form_listbox_mat.insert(END, self.material_list_name)
			self.tab_form_listbox_bat.insert(END, self.batch_list_name)
			self.tab_form_listbox_quan.insert(END, self.quan_list_name)
			self.tab_form_listbox_unit.insert(END, self.unit_list_name)
			self.tab_form_label_status_update_var.set('Added to formulation')
		else:
			self.tab_form_label_status_update_var.set('Not added to formulation; not all values entered.')
	
	def remove_from_formulation(self):	
		items = map(int, self.tab_form_listbox_mat.curselection())
		for i in items:
			self.tab_form_listbox_bat.delete(i)
			self.tab_form_listbox_quan.delete(i)
			self.tab_form_listbox_unit.delete(i)
			self.tab_form_listbox_mat.delete(i)
	
	def list_box_selection_mat(self, *args):
		items = map(int, self.tab_form_listbox_mat.curselection())
		self.tab_form_listbox_bat.selection_clear(first=0, last=END)
		self.tab_form_listbox_quan.selection_clear(first=0, last=END)
		self.tab_form_listbox_unit.selection_clear(first=0, last=END)
		for i in items:
			self.tab_form_listbox_bat.select_set(i)
			self.tab_form_listbox_quan.select_set(i)
			self.tab_form_listbox_unit.select_set(i)

	def list_box_selection_bat(self, *args):
		items = map(int, self.tab_form_listbox_bat.curselection())
		self.tab_form_listbox_mat.selection_clear(first=0, last=END)
		self.tab_form_listbox_quan.selection_clear(first=0, last=END)
		self.tab_form_listbox_unit.selection_clear(first=0, last=END)
		for i in items:
			self.tab_form_listbox_mat.select_set(i)
			self.tab_form_listbox_quan.select_set(i)
			self.tab_form_listbox_unit.select_set(i)

	def list_box_selection_quan(self, *args):
		items = map(int, self.tab_form_listbox_quan.curselection())
		self.tab_form_listbox_bat.selection_clear(first=0, last=END)
		self.tab_form_listbox_mat.selection_clear(first=0, last=END)
		self.tab_form_listbox_unit.selection_clear(first=0, last=END)
		for i in items:
			self.tab_form_listbox_bat.select_set(i)
			self.tab_form_listbox_mat.select_set(i)
			self.tab_form_listbox_unit.select_set(i)

	def list_box_selection_unit(self, *args):
		items = map(int, self.tab_form_listbox_unit.curselection())
		self.tab_form_listbox_bat.selection_clear(first=0, last=END)
		self.tab_form_listbox_quan.selection_clear(first=0, last=END)
		self.tab_form_listbox_mat.selection_clear(first=0, last=END)
		for i in items:
			self.tab_form_listbox_bat.select_set(i)
			self.tab_form_listbox_quan.select_set(i)
			self.tab_form_listbox_mat.select_set(i)
	def tab_form_box_prev_func(self, *args):
		prev_names = []
		prev_form_exists = self.conn.execute('SELECT form_name FROM formulations')
		prev_form_exists_results = prev_form_exists.fetchall()
		#check if anything was returned from the search and if so add to the dropdown list

		if prev_form_exists_results:
			for i in prev_form_exists_results:
				if i[0]:
					prev_names.append(i[0])
			#remove the repeats and sort the list
			self.tab_form_prev_name_box['values'] = list(sorted(set(i for i in prev_names)))

	def update_formulation_data(self, *args):
		self.tab_form_check_var.set(False)
		self.tab_form_check_var_ultra.set(False)
		self.tab_form_check_filter_var.set(False)
		self.tab_form_text_notes.delete(1.0,END)
		self.batch_box.set('')
		self.material_box.set('')
		self.var_lab_unit.set('')
		self.var_spin_quan.set(0)
		self.tab_form_waste_box.set('')
		
		self.tab_form_box_prev_func()
		
		form_id_select = self.conn.execute('SELECT form_id FROM formulations WHERE form_name = ?', (self.tab_form_prev_name_box.get(),))
		form_id_select_result = form_id_select.fetchone()[0]
		#That should be ok as the form_name should be unique
		
		prev_name_form_inputs = self.conn.execute('SELECT form_name FROM formulations WHERE form_id = ?', (form_id_select_result,))
		prev_name_form_inputs_results = prev_name_form_inputs.fetchone()[0]
		if prev_name_form_inputs_results:
			self.var_form_name.set(prev_name_form_inputs_results)
		else:
			self.var_form_name.set(False)

		###Get the conds_id too...
		#If there are multiple conds this will need updating
		conds_id_select = self.conn.execute('SELECT conds_id FROM formulations WHERE form_id = ?', (form_id_select_result,))
		conds_id_select_results = conds_id_select.fetchone()[0]
		
		self.tab_form_listbox_mat.delete(0,END)
		self.tab_form_listbox_bat.delete(0,END)
		self.tab_form_listbox_quan.delete(0,END)
		self.tab_form_listbox_unit.delete(0,END)
		
		
		####This needs changing, now each form_id has multiple rows that need to be selected and the mat, mat_bat and quantity selected.
		
		#####
		#first get the rows for the form_id
		form_rows_select = self.conn.execute('SELECT id FROM formulations WHERE form_id = ?', (form_id_select_result,))
		form_rows_select_result = form_rows_select.fetchall()

		#Select the lst of the things for each id
		for index, row in enumerate(form_rows_select_result):
			row = row[0]
			#Get the material id
			#Then use that to get the common name
			form_mat_id_select = self.conn.execute('SELECT mat_id FROM formulations WHERE id = ?', (row,))
			form_mat_id_select_result = form_mat_id_select.fetchone()[0]
			mat_id_result = str(form_mat_id_select_result)
			
			if mat_id_result == 'None':
				pass
			else:	
				#Now get the names of the material
				mat_com = self.conn.execute('SELECT common_name FROM materials WHERE id = ?', (form_mat_id_select_result,))
				mat_com_results = mat_com.fetchone()[0]	
				#Should check if anything is there...
				self.tab_form_listbox_mat.insert(index, mat_com_results)
				
			#Get the bat_id
			#Then use that to get the batch name and the units...
			form_bat_id_select = self.conn.execute('SELECT mat_bat_id FROM formulations WHERE id = ?', (row,))
			form_bat_id_select_result = form_bat_id_select.fetchone()[0]
			bat_id_result = str(form_bat_id_select_result)
			
			if bat_id_result == 'None':
				pass
			else:
	
				bat_com = self.conn.execute('SELECT batch_code FROM mat_bat WHERE id = ?', (form_bat_id_select_result,))
				bat_com_results = bat_com.fetchone()[0]	
				self.tab_form_listbox_bat.insert(index, bat_com_results)
				#### sort out the units ########

				units_exists = self.conn.execute('SELECT units FROM mat_bat WHERE id = ?', (form_bat_id_select_result,))
				units_exists_results = units_exists.fetchall()
		
				units = str(units_exists_results[0][0])
				if units:
					if units == '0':
						x = '(grams)'
					elif units == '1':
						x = '(millilitres)'
					elif units == '2':
						x = '(units)'
					else:
				 		x = '(error)'
				else:
				 	x = '(error)'	
				self.tab_form_listbox_unit.insert(index, x)

			quan = self.conn.execute('SELECT quantity FROM formulations WHERE id = ?', (row,))
			quan_results = quan.fetchone()[0]
			quan_results = str(quan_results)
			if quan_results== 'None':
				pass
			else:
				self.tab_form_listbox_quan.insert(index, quan_results)
				
		##########################
		##########################
		##########################
		##########################
		##########################
		#For the form_props table
		##########################
		prev_date = self.conn.execute('SELECT date_made FROM form_props WHERE id = ?', (form_id_select_result,))
		prev_date_results = prev_date.fetchone()[0]
		if prev_date_results:
			self.var_spin_year.set(prev_date_results[:4])
			self.var_spin_month.set(prev_date_results[5:7])
			self.var_spin_day.set(prev_date_results[8:10])
			
		else:
			self.var_spin_year.set(False)
			self.var_spin_month.set(False)
			self.var_spin_day.set(False)
		
		prev_visc = self.conn.execute('SELECT visc FROM form_props WHERE id = ?', (form_id_select_result,))
		prev_visc_results = prev_visc.fetchone()[0]
		
		if prev_visc_results:		
			self.var_spin_visc.set(prev_visc_results)
		else:
			self.var_spin_visc.set(False)

		prev_surten = self.conn.execute('SELECT surten FROM form_props WHERE id = ?', (form_id_select_result,))
		prev_surten_results = prev_surten.fetchone()[0]
		if prev_surten_results:		
			self.var_spin_surten.set(prev_surten_results)
		else:
			self.var_spin_surten.set(False)
			
		prev_waste = self.conn.execute('SELECT waste_stream FROM form_props WHERE id = ?', (form_id_select_result,))
		prev_waste_results = prev_waste.fetchone()[0]
		
		if prev_waste_results:
			self.tab_form_waste_var.set(prev_waste_results)
		else:
			self.tab_form_waste_var.set(False)
			
		prev_notes = self.conn.execute('SELECT form_notes FROM form_props WHERE id = ?', (form_id_select_result,))
		prev_notes_results = prev_notes.fetchone()[0]

		if prev_notes_results:	 	
			self.tab_form_text_notes.insert(END, prev_notes_results)
		else:
			self.tab_form_text_notes.insert(END, 'No notes available.')
		
		#########################
		#########################
		#########################
		#########################
		#For the form_conds table	
		prev_temp = self.conn.execute('SELECT temp FROM form_conds WHERE id = ?', (conds_id_select_results,))
		prev_temp_results = prev_temp.fetchone()[0]
		if prev_temp_results:
			self.var_spin_heat_temp.set(prev_temp_results)
			self.tab_form_check_var.set(True)
		else:
			self.var_spin_heat_temp.set(False)
			self.tab_form_check_var.set(False)

		prev_time_temp = self.conn.execute('SELECT time_temp FROM form_conds WHERE id = ?', (conds_id_select_results,))
		prev_time_temp_results = prev_time_temp.fetchone()[0]
		if prev_time_temp_results:
			self.var_spin_heat_time.set(prev_time_temp_results)
			self.tab_form_check_var.set(True)
		else:
			self.var_spin_heat_time.set(False)
			self.tab_form_check_var.set(False)

		prev_ultra_temp = self.conn.execute('SELECT ultra_temp FROM form_conds WHERE id = ?', (conds_id_select_results,))
		prev_ultra_temp_results = prev_ultra_temp.fetchone()[0]
		if prev_ultra_temp_results:
			self.var_spin_ultra_temp.set(prev_ultra_temp_results)
			self.tab_form_check_var_ultra.set(True)
		else:
			self.var_spin_ultra_temp.set(False)
			self.tab_form_check_var_ultra.set(False)

		prev_ultra_time = self.conn.execute('SELECT ultra_time FROM form_conds WHERE id = ?', (conds_id_select_results,))
		prev_ultra_time_results = prev_ultra_time.fetchone()[0]
		if prev_ultra_time_results:
			self.var_spin_ultra_time.set(prev_ultra_time_results)
			self.tab_form_check_var_ultra.set(True)
		else:
			self.var_spin_ultra_time.set(False)
			self.tab_form_check_var_ultra.set(False)

		prev_ultra_power = self.conn.execute('SELECT ultra_power FROM form_conds WHERE id = ?', (conds_id_select_results,))
		prev_ultra_power_results = prev_ultra_power.fetchone()[0]
		if prev_ultra_power_results:
			self.var_spin_ultra_power.set(prev_ultra_power_results)
			self.tab_form_check_var_ultra.set(True)
		else:
			self.var_spin_ultra_power.set(False)
			self.tab_form_check_var_ultra.set(False)
			
		prev_sol_atm = self.conn.execute('SELECT solids_atm FROM form_conds WHERE id = ?', (conds_id_select_results,))
		prev_sol_atm_results = prev_sol_atm.fetchone()[0]
		if prev_sol_atm_results:		
			self.prep_atm_var.set(prev_sol_atm_results)
		else:
			self.prep_atm_var.set(False)
			
		prev_liq_atm = self.conn.execute('SELECT liquids_atm FROM form_conds WHERE id = ?', (conds_id_select_results,))
		prev_liq_atm_results = prev_liq_atm.fetchone()[0]
		if prev_liq_atm_results:		
			self.prep_atm_liq_var.set(prev_liq_atm_results)
		else:
			self.prep_atm_liq_var.set(False)	
		
		prev_heat_atm = self.conn.execute('SELECT heat_atm FROM form_conds WHERE id = ?', (conds_id_select_results,))
		prev_heat_atm_results = prev_heat_atm.fetchone()[0]
		if prev_heat_atm_results:		
			self.heat_atm_var.set(prev_heat_atm_results)
		else:
			self.heat_atm_var.set(False)
				
			
		prev_filt = self.conn.execute('SELECT filter FROM form_conds WHERE id = ?', (conds_id_select_results,))
		prev_filt_results = prev_filt.fetchone()[0]

		if prev_filt_results:	
			self.tab_form_filt_var.set(prev_filt_results)
			self.tab_form_check_filter_var.set(True)
		else:
			self.tab_form_filt_var.set(False)
			self.tab_form_check_filter_var.set(False)


		prev_filt_si = self.conn.execute('SELECT filt_size FROM form_conds WHERE id = ?', (conds_id_select_results,))
		prev_filt_si_results = prev_filt_si.fetchone()[0]
		if prev_filt_si_results:		
			self.var_spin_filt.set(prev_filt_si_results)
		else:
			self.var_spin_filt.set(False)
		
		#Not sure this is really needed but updates the box
		self.tab_form_update_formulation_names()	
				
	def quit(self):
		if tkMessageBox.askokcancel("Quit", "Exit Program"):
			root.destroy()
			sys.exit()	
	   
root=Tk()	
def xquit():
		root.destroy()
		sys.exit()
			
root.wm_title("SolPyBase V0.02")
if platform.system() == "Windows":
	root.iconbitmap(r'..\\..\\_database\\deps\\solpybas.ico')
else:
	img = PhotoImage(file='../../_database/deps/solpybas.gif')
	root.tk.call('wm', 'iconphoto', root._w, img)

app = Plotter(root)

root.protocol('WM_DELETE_WINDOW', xquit)
root.mainloop()

root.destroy() # optional
