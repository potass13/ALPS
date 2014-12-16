##########################################################
# 
# name : replace.py
# usage : xml to csv for ALPS
# edit : potass 
# Last Update : 2014-10-18
#
##########################################################

import sys, os

#argparse setting
import argparse
parser = argparse.ArgumentParser(description='Convert XML files produced by ALPS application to CSV file.')
parser.add_argument('--fig', action='store_true', help='Figure is outputted by matplotlib if this flag is set. (defalt: false)') 
parser.add_argument('-t', '--title', default='Graph Title', help='Figure title outputted by matplotlib. (defalt: Graph Title)') 
parser.add_argument('-x', default='T', help='X-value of outputted data. (default: T)')
parser.add_argument('-y', default='Susceptibility', help='Y-value of outputted data. (default: Susceptibility)')
parser.add_argument('--debug', action='store_true', help='debug mode if this flag is set. (default: false)')
parser.add_argument('--lab', action='store_true', help='Lab PC ONLY. (default: false)') 
parser.add_argument('-p', '--prefix', required=True, help='The prefix of XML files. (Required)')
parser.add_argument('path_drc_xml', nargs=None, help='Directly path where XML files produced by ALPS are included.')
args = parser.parse_args()

#Lab PC only#######
if args.lab:
	sys.path.append('C:\Program Files\VisTrails\Python27\Lib\site-packages')
###################

import pyalps
import matplotlib.pyplot as plt
import pyalps.plot

from itertools import chain

cmd = sys.__stderr__

def conv_val(in_val):
	val = str(in_val)
	val = val.capitalize()
	
	if val in ['T', 'Temp', 'Tmp', 'Temperature']:
		val = 'T'
	elif val in ['H', 'B', 'Field' 'Magnetic_field','External_field']:
		val = 'h'
	elif val in ['M', 'Mag', 'Magnetization', 'Magnetizationdensity', 'Magnetization_density']:
		val = 'Magnetization Density'
	elif val in ['C', 'Cap', 'Capacity', 'Specific_heat', 'Specificheat', 'Heat_capacity', 'Heatcapacity']:
		val = 'Specific Heat'
	elif val in ['Sus', 'Susceptibility']:
		val = 'Susceptibility'
	elif val in ['S', 'Local_s']:
		val = 'local_S'
	elif val in ['Seed', 'Seeds']:
		val = 'SEED'
	elif val in ['Sweep', 'Sweeps']:
		val = 'SWEEPS'
	elif val in ['Thermalization']:
		val = 'THERMALIZATION'
	else:
		val = in_val.replace('_', ' ')
	
	return(val)
	
try:
	if args.debug:
		cmd.write(str(args))
	
	#define x-value and y-value 
	read_file = pyalps.getResultFiles(prefix=args.prefix)
	
	x_val = conv_val(args.x)
	y_val = conv_val(args.y)
	
	val_list = pyalps.loadObservableList(read_file)
	val_list = list(set(list(chain.from_iterable(val_list))))
	no_error_val = ['T', 'h', 'L', 'N', 'local_S', 'THERMALIZATION', 'SEED', 'SWEEPS']
	val_list = val_list + no_error_val
	
	if args.debug:
		cmd.write('\nval_list is ' + str(val_list) + '\n')
		cmd.write('no_error_val is ' + str(no_error_val) + '\n')
		cmd.write('x_val is ' + x_val + '\n')
		cmd.write('y_val is ' + y_val + '\n')
	
	if not x_val in val_list:
		cmd.write('The X-value you inputted do not exist.\n')
		cmd.write('You should choose this list, ' + str(val_list) + '\n')
		sys.exit(1)
	elif not y_val in val_list:
		cmd.write('The Y-value you inputted do not exist.\n')
		cmd.write('You should choose this list, ' + str(val_list) + '\n')
		sys.exit(1)
	
	#XML data file -> gnuplot-form text
	cmd.write('Start to convert the files XML to gnuplot-form.\n')
	data = pyalps.loadMeasurements(read_file, y_val)
	data = pyalps.flatten(data)
	xy_data = pyalps.collectXY(data, x_val, y_val)
	gnu_xy_data = pyalps.plot.makeGnuplotPlot(xy_data)
	if args.debug:
		cmd.write(str(gnu_xy_data))
	cmd.write('Finish to convert the files XML to gnuplot-form.\n')
	
	#gnuplot-form text -> csv-form text
	cmd.write('Start to convert the files gnuplot-form to CSV.\n')
	temp_file = '__tmp_replace__.dat'
	f = open(temp_file, 'w')
	f.write(gnu_xy_data)
	f.close()
	
	head_x = x_val
	head_y = y_val
	if not x_val in no_error_val:
		head_x = head_x + ', err_' + x_val
	if not y_val in no_error_val:
		head_y = head_y + ', err_' + y_val
	
	temp_file = '__tmp_replace__.dat'
	f = open(temp_file, 'w')
	f.write(gnu_xy_data)
	f.close()
	
	ff = open(temp_file, 'r')
	i = 0
	csv_str = '# ' + head_x + ', ' + head_y + '\n'
	
	for line in ff:
		i += 1
		if i <= 5:
			continue
		elif line.find('end') != -1:
			break
		else:
			csv_str = csv_str + line.replace('\t', ', ')
	
	ff.close()
	os.remove(temp_file)
	
	cmd.write('Finish to convert the files gnuplot-form to CSV.\n')
	print csv_str
	cmd.write('Outputted a data-file with x:' + x_val + ' vs y:' + y_val + '.\n')
	
	#make one plot with all data
	if args.fig:
		plt.figure() 
		plt.title(args.title)
		plt.xlabel(x_val)
		plt.ylabel(y_val)
		pyalps.plot.plot(xy_data) 
		plt.show()
		
except:
	 cmd.write('\nError occurs!!\n')
