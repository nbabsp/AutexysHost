import glob
import os
import sys
import numpy as np

if(__name__ == '__main__'):
	sys.path.append(sys.path[0] + '/..')
import DataLoggerUtility as dlu

load_directory = '../../data_to_reformat/C139'
save_directory = '../../data_reformatted/C139'

def reformat_wafer(load_directory, save_directory):
	for chipSubdirectory in [name for name in os.listdir(load_directory) if os.path.isdir(os.path.join(load_directory, name))]:
		chipLoadDirectory = os.path.join(load_directory, chipSubdirectory)
		chipSaveDirectory = os.path.join(save_directory, chipSubdirectory)
		reformat_chip(chipLoadDirectory, chipSaveDirectory)

	# Copy wafer.json
	try:
		waferData = dlu.loadJSON(load_directory, 'wafer.json')[0]
		dlu.saveJSON(save_directory, 'wafer', waferData, incrementIndex=False)
	except:
		print('no wafer.json')
	


def reformat_chip(load_directory, save_directory):
	for deviceSubdirectory in [name for name in os.listdir(load_directory) if os.path.isdir(os.path.join(load_directory, name))]:
		deviceLoadDirectory = os.path.join(load_directory, deviceSubdirectory)
		deviceSaveDirectory = os.path.join(save_directory, deviceSubdirectory)
		reformat_device(deviceLoadDirectory, deviceSaveDirectory)

def reformat_device(load_directory, save_directory):
		device = load_directory.split('/')[-1]

		# Load device history for GateSweep, BurnOut, and StaticBias
		gateSweepHistory = dlu.loadJSON(load_directory, 'GateSweep.json')
		try:
			burnOutHistory = dlu.loadJSON(load_directory, 'BurnOut.json')
			burnedout = True
		except:
			print('Device: ' + device + ' no burn-out')
			burnedout = False
		try:
			staticBiasHistory = dlu.loadJSON(load_directory, 'StaticBias.json')
			staticed = True
		except:
			print('Device: ' + device + ' no static bias')
			staticed = False
		try:
			parametersHistory = dlu.loadJSON(load_directory, 'ParametersHistory.json')
			paramhist = True
		except:
			print('Device: ' + device + ' no ParametersHistory.json')
			paramhist = False
		# *************************************************************


		

		# *************************************************************
		# ****************** BEGIN DATA MODIFICATION ******************
		# *************************************************************

		# GATE SWEEP
		for deviceRun in gateSweepHistory:
			if(deviceRun['ParametersFormatVersion'] > 4):
				continue

			deviceRun['MeasurementSystem']['systemType'] = 'single' if(deviceRun['MeasurementSystem']['systems']['default']['type'] == 'B2912A') else 'standalone'
			if(deviceRun['MeasurementSystem']['systemType'] == 'single'):
				deviceRun['MeasurementSystem']['systems']['SMU'] = deviceRun['MeasurementSystem']['systems']['default']
			if(deviceRun['MeasurementSystem']['systemType'] == 'standalone'):
				deviceRun['MeasurementSystem']['systems']['PCB'] = deviceRun['MeasurementSystem']['systems']['default']
			del deviceRun['MeasurementSystem']['systems']['default']

		# BURN OUT
		if(burnedout):
			for deviceRun in burnOutHistory:
				if(deviceRun['ParametersFormatVersion'] > 4):
					continue

				deviceRun['MeasurementSystem']['systemType'] = 'single' if(deviceRun['MeasurementSystem']['systems']['default']['type'] == 'B2912A') else 'standalone'
				if(deviceRun['MeasurementSystem']['systemType'] == 'single'):
					deviceRun['MeasurementSystem']['systems']['SMU'] = deviceRun['MeasurementSystem']['systems']['default']
				if(deviceRun['MeasurementSystem']['systemType'] == 'standalone'):
					deviceRun['MeasurementSystem']['systems']['PCB'] = deviceRun['MeasurementSystem']['systems']['default']
				del deviceRun['MeasurementSystem']['systems']['default']

		# STATIC BIAS
		if(staticed):			
			for deviceRun in staticBiasHistory:
				if(deviceRun['ParametersFormatVersion'] > 4):
					continue

				deviceRun['MeasurementSystem']['systemType'] = 'single' if(deviceRun['MeasurementSystem']['systems']['default']['type'] == 'B2912A') else 'standalone'
				if(deviceRun['MeasurementSystem']['systemType'] == 'single'):
					deviceRun['MeasurementSystem']['systems']['SMU'] = deviceRun['MeasurementSystem']['systems']['default']
				if(deviceRun['MeasurementSystem']['systemType'] == 'standalone'):
					deviceRun['MeasurementSystem']['systems']['PCB'] = deviceRun['MeasurementSystem']['systems']['default']
				del deviceRun['MeasurementSystem']['systems']['default']

		# PARAMETERS HISTORY
		if(paramhist):
			for deviceRun in parametersHistory:

				deviceRun['MeasurementSystem']['systemType'] = 'single' if(deviceRun['MeasurementSystem']['systems']['default']['type'] == 'B2912A') else 'standalone'
				if(deviceRun['MeasurementSystem']['systemType'] == 'single'):
					deviceRun['MeasurementSystem']['systems']['SMU'] = deviceRun['MeasurementSystem']['systems']['default']
				if(deviceRun['MeasurementSystem']['systemType'] == 'standalone'):
					deviceRun['MeasurementSystem']['systems']['PCB'] = deviceRun['MeasurementSystem']['systems']['default']
				del deviceRun['MeasurementSystem']['systems']['default']



		# *************************************************************
		# ******************  END DATA MODIFICATION  ******************
		# *************************************************************



		# Save device history for GateSweep, BurnOut, and StaticBias
		for deviceRun in gateSweepHistory:
			dlu.saveJSON(save_directory, 'GateSweep', deviceRun, incrementIndex=False)
		if(burnedout):
			for deviceRun in burnOutHistory:
				dlu.saveJSON(save_directory, 'BurnOut', deviceRun, incrementIndex=False)
		if(staticed):
			for deviceRun in staticBiasHistory:
				dlu.saveJSON(save_directory, 'StaticBias', deviceRun, incrementIndex=False)
		if(paramhist):
			for deviceRun in parametersHistory:
				dlu.saveJSON(save_directory, 'ParametersHistory', deviceRun, incrementIndex=False)

		# Copy index.json
		try:
			indexData = dlu.loadJSON(load_directory, 'index.json')[0]
			dlu.saveJSON(save_directory, 'index', indexData, incrementIndex=False)
		except:
			print('Device: ' + device + ' no index.json')
		# *************************************************************


if(__name__ == '__main__'):
	reformat_wafer(load_directory, save_directory)




