##########################################################
#
# name : checkSS.py
# usage : checkSteadyState for ALPS based on ALPS wiki, 
# http://comp-phys.org/mediawiki/index.php/Documentation:Monte_Carlo_Equilibration
# edit : potass
# Last Update : 2014-10-19
#
##########################################################

import sys, os

#argparse setting
import argparse
parser = argparse.ArgumentParser(description='Use pyalps.checkSteadyState() by ALPS application.')
parser.add_argument('-g', '--gamma', default='0.6827', help='Confidence coefficient. (default: 0.6827)')
parser.add_argument('-y', default='Susceptibility', help='The error of physical quantity you want to check. (default: Susceptibility)')
parser.add_argument('--debug', action='store_true', help='debug mode if this flag is set. (default: false)')
parser.add_argument('-l', '--label', default='T', help='The label of the data. (default: T)')
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
from scipy.stats import norm

import csv
from itertools import chain

cmd = sys.__stderr__

def conv_val(in_val):
	in_val = str(in_val)
	val = in_val.capitalize()
	
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

if args.debug:
	cmd.write(str(args))
	
try:
	if args.debug and (not os.path.exists(args.path_drc_xml)):
		cmd.write('path_drc_xml(' + str(args.path_drc_xml) + ') do not exist.\n')
		sys.exit(1)
	os.chdir(args.path_drc_xml)
	
	#get result files
	read_file = pyalps.getResultFiles(prefix=args.prefix)
	
	#define physical quantity
	pq = conv_val(args.y)
	
	val_list = pyalps.loadObservableList(read_file)
	val_list = list(set(list(chain.from_iterable(val_list))))
	no_error_val = ['T', 'h', 'L', 'N', 'local_S', 'THERMALIZATION', 'SEED', 'SWEEPS']
	val_list = val_list + no_error_val
	
	label = args.label
	
	if not pq in val_list:
		cmd.write('The physical quantity you inputted do not exist.\n')
		cmd.write('You should choose this list, ' + str(val_list) + '\n')
		sys.exit(1)
	
	if not label in no_error_val:
		cmd.write('The label you inputted do not exist or cannot use.\n')
		cmd.write('You should choose this list, ' + str(no_error_val) + '\n')
		sys.exit(1)
	
	cmd.write('Start Z-Hypothesis for beta_1 written in ALPS wiki.\n')
	data = pyalps.loadMeasurements(read_file, args.y)
	css = pyalps.checkSteadyState(data, confidenceInterval=args.gamma)
	if args.debug:
		cmd.write(str(css))
	stat_list = []
	tf = 0
	lb = ['# ' + label]
	i = 0
	z0_wiki = norm.ppf(0.5+0.5*args.gamma)
	
	for ds in css:
		qs = ds.props['checkSteadyState']
		qs = qs['statistics']
		if qs['z'] <= z0_wiki:
			tf = 1
		else:
			tf = 0
		stat_list.append([ds.props[label], qs['z'], qs['z0'], z0_wiki, qs['confidenceInterval'], tf])
		if i == 0:
			lb.append('z')
			lb.append('z0_pyalps')
			lb.append('z0_wiki')
			lb.append('confidenceCoefficient')
			lb.append('T_or_F_wiki')
		i += 1
	cmd.write('Z-Hypothesis is finished.\nStart to output a file as cvs format.\n')
	print '# XML file : ' + args.prefix + '.in.xml'
	
	temp_file = '__tmp_checkSS__.dat'
	f = open(temp_file, 'w')
	cw = csv.writer(f, lineterminator='\n')
	cw.writerow(lb)
	cw.writerows(stat_list)
	f.close()
	ff = open(temp_file, 'r')
	css = ff.read()
	ff.close()
	os.remove(temp_file)
	css = css.replace('\nNone\n','\n')
	print css
	
	cmd.write('Finish to output a file as cvs format.\n')
except:
	cmd.write('\nError occurs!!\n')
