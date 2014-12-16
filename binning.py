##########################################################
#
# name : binning.py
# usage : binnig analysis for ALPS
# edit : potass 
# Last Update : 2014-10-18
#
##########################################################

import sys, os

#argparse setting
import argparse
parser = argparse.ArgumentParser(description='Binning analiysis used for XML files produced by ALPS application.')
parser.add_argument('--fig', action='store_true', help='Figure is outputted by matplotlib if this flag is set. (defalt: false)') 
parser.add_argument('-y', default='Susceptibility', help='The error of physical quantity you want to check whether the data is converged or not. (default: Susceptibility)')
parser.add_argument('-l', '--label', default='task', help='The label of the data. (default: task number)')
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

import csv
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
	
	if args.debug and (not os.path.exists(args.path_drc_xml)):
		cmd.write('path_drc_xml(' + str(args.path_drc_xml) + ') do not exist.\n')
		sys.exit(1)
	os.chdir(args.path_drc_xml)
	
	#get result files
	read_file = pyalps.getResultFiles(prefix=args.prefix)
	
	#define physical quantity
	pq = args.y
	pq = conv_val(pq)
	
	obs_list = pyalps.loadObservableList(read_file)
	obs_list = list(set(list(chain.from_iterable(obs_list))))
	
	if not pq in obs_list:
		cmd.write('The physical quantity you inputted do not exist.\n')
		cmd.write('You should choose this list, ' + str(obs_list) + '\n')
		sys.exit(1)
	
	#load the binning analysis for the absolute value of the magnetization
	if args.debug:
		cmd.write('pyalps.loadBinningAnalysis() is started.\n')
	binning = pyalps.loadBinningAnalysis(read_file, pq)
	if args.debug:
		cmd.write('pyalps.loadBinningAnalysis() is finished.\n')
	binning = pyalps.flatten(binning)
	
	if args.debug:
		cmd.write(str(binning))
	
	#get plot data as csv and creat label
	x = []
	y = []
	lb = ['# binning_level']
	i = 0
	maxlen = 0
	for ds in binning:
		try:
			xx = [float(vvv) for vvv in ds.x]
			yy = [float(www) for www in ds.y]
		except:
			xx = [ds.x]
			yy = [ds.y]
		y.append(yy)
		
		if len(xx) > maxlen:
			maxlen = len(xx)
			x = xx
		
		if ds.props.has_key(args.label):
			ds.props['label'] = args.label + '=' + str(ds.props[args.label])
		else:
			ds.props['label'] = 'task' + str(i+1)
		lb.append(ds.props['label'])
		i += 1
	
	#output plot data as csv
	csv_matrix = [x]
	for l in range(0, len(binning)):
		while(len(y[l]) < maxlen):
			y[l].append('')
		csv_matrix.append(y[l])
	
	csv_matrix = map(list, zip(*csv_matrix)) #transpose
	
	cmd.write('\nOutput file as cvs format.\n')
	print '# XML file : ' + args.prefix + '.in.xml'
	
	temp_file = '__tmp_binnig__.dat'
	f = open(temp_file, 'w')
	cw = csv.writer(f, lineterminator='\n')
	cw.writerow(lb)
	cw.writerows(csv_matrix)
	f.close()
	ff = open(temp_file, 'r')
	str = ff.read()
	ff.close()
	os.remove(temp_file)
	str = str.replace('\nNone\n','\n')
	print str
	
	#make one plot with all data
	if args.fig:
		plt.figure()
		plt.title('Binning analysis')
		plt.xlabel('binning level')
		plt.ylabel('Error of ' + pq)
		pyalps.plot.plot(binning)
		plt.legend()
		plt.show()

except:
	cmd.write('\nError occurs!!\n')
