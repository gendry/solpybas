import numpy as np

#import matplotlib.pyplot as plt
#import matplotlib.patches as mpatches
#import matplotlib.ticker as ticker
#from matplotlib.ticker import AutoMinorLocator

import itertools

def sort_data(datafile):
	#Sort the data into the splits and forward and reverse scans held in a dict using the split as key
	#The splits are in the second column

	#Get the data, as the type is mixed the array is a a list of tuple for each row
	#data = np.genfromtxt(datafile, skip_header=1, delimiter='\t', dtype=None)
	data = datafile
	#Sort the scans into forward and reverse
	forward_scans = []
	reverse_scans = []
	for row in data:
		if str(row[7]) == 'forward':
			forward_scans.append(row)
		else:
			reverse_scans.append(row)

	#find the split numbers and make a dict using number as key
	#Only works if one batch in file
	all_splits = [i[1] for i in data]
	all_splits = np.unique(np.asarray(all_splits))
	#print all_splits
	splits = [int(i) for i in all_splits]

	forward_splits_dict = {}
	reverse_splits_dict = {}

	#Sort the data into the dicts
	for split in splits:
		forward_splits_dict[split] = []
		for row in forward_scans:
			row_num = int(row[1])
			if row_num == split:
				forward_splits_dict[split].append(row)

	for split in splits:
		reverse_splits_dict[split] = []
		for row in reverse_scans:
			row_num = int(row[1])
			if row_num == split:
				reverse_splits_dict[split].append(row)   

	#data is in dicts with list of tuples containing the data
	return forward_splits_dict, reverse_splits_dict, splits


def split_pos(rev_data_to_plot):
	num_splits = len(rev_data_to_plot)    
	rev_pos = np.arange(0.9,num_splits+0.9,1)
	for_pos = np.arange(1.1,num_splits+1.1,1)
	return rev_pos, for_pos

def bp_cols(bp,hex_colour):
	## change outline color, fill color and linewidth of the boxes
	for index, box in enumerate(bp['boxes']):
		facecolour = hex_colour
		# change outline color
		box.set( color='#000000', linewidth=1)
		# change fill color
		box.set( facecolor = facecolour, alpha=0.6)
		#box.set(zorder=0)
	## change color and linewidth of the whiskers
	for whisker in bp['whiskers']:
		whisker.set(color='#000000', linewidth=1)
		#whisker.set(zorder=0)
	## change color and linewidth of the caps
	for cap in bp['caps']:
		cap.set(color='#000000', linewidth=1)
		#cap.set(zorder=0)
	## change color and linewidth of the medians
	for median in bp['medians']:
		median.set(color='#000000', linewidth=1)
		#median.set(zorder=0)
	## change the style of fliers and their fill
	for flier in bp['fliers']:
		flier.set(marker='o', markeredgecolor='k',markersize=3,markerfacecolor="None")
	for mean in bp['means']:
			mean.set(marker='s',color='green',markersize=3)
		#flier.set(zorder=0)
	#pces are in column
def plot_list(thing,index,splits,reverse_splits_dict,forward_splits_dict,split_names):
	rev_x_to_plot = []
	for_x_to_plot = []
	for split in splits:
		para = []
		for row in reverse_splits_dict[split]:
			para.append(row[index])
		rev_x_to_plot.append(para)
		para = []
		for row in forward_splits_dict[split]:
			para.append(row[index])
		for_x_to_plot.append(para)
	return rev_x_to_plot, for_x_to_plot