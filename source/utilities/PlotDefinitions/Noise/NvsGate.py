from utilities.MatplotlibUtility import *
import numpy as np


plotDescription = {
	'plotCategory': 'device',
	'priority': 540,
	'dataFileDependencies': ['NoiseCollection.json'],
	'plotDefaults': {
		'figsize':(2,2.5),
		'includeOriginOnYaxis':True,
		'automaticAxisLabels':False,
		'includeFiltered': False,
		'colorMap':'white_purple_black',
		'colorDefault': ['#7363af'],
		'xlabel':'$V_{{GS}}^{{Sweep}}$ (V)',
		'ylabel':'$I_{{D}}$ (A)',
		'micro_ylabel':'$I_{{D}}$ ($\\mu$A)',
		'nano_ylabel':'$I_{{D}}$ (nA)',
		'pico_ylabel':'$I_{{D}}$ (pA)',
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	
	# Get noise magnitude vs. VGS and VDS
	gateVoltages, drainVoltages, unfilteredNoise, filteredNoise = extractNoiseMagnitude(deviceHistory, groupBy='drain')
	
	# Adjust y-scale and y-axis labels 
	max_current = np.max(np.abs(np.array(unfilteredNoise)))
	current_scale, ylabel = (1, plotDescription['plotDefaults']['ylabel']) if(max_current >= 1e-3) else ((1e6, plotDescription['plotDefaults']['micro_ylabel']) if(max_current >= 1e-6) else ((1e9, plotDescription['plotDefaults']['nano_ylabel']) if(max_current >= 1e-9) else (1e12, plotDescription['plotDefaults']['pico_ylabel'])))		
	
	# Build Color Map and Color Bar
	colors = setupColors(fig, len(drainVoltages), colorOverride=mode_parameters['colorsOverride'], colorDefault=plotDescription['plotDefaults']['colorDefault'], colorMapName=plotDescription['plotDefaults']['colorMap'], colorMapStart=0.8, colorMapEnd=0.1, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=['', '', '$t_0$'], colorBarAxisLabel='')

	# Plot	
	for i in range(len(drainVoltages)):
		line 	 = ax.plot(gateVoltages[i], np.array(unfilteredNoise[i]) * current_scale, color=colors[i], marker='o', markersize=4, linewidth=1, linestyle=None, label='$V_{{DS}}$ = {:.2f} V'.format(drainVoltages[i]))
		if(plotDescription['plotDefaults']['includeFiltered']):
			line = ax.plot(gateVoltages[i], np.array(filteredNoise[i]) * current_scale, color=colors[i], marker='o', markersize=4, linewidth=1, linestyle=None)

	# Set Axis Labels
	axisLabels(ax, x_label=plotDescription['plotDefaults']['xlabel'], y_label=ylabel)
	
	# Legend
	ax.legend()
	
	return (fig, (ax,))
	
def noiseFromData(data):
	return np.percentile(data, 99.5)-np.percentile(data, 0.5) # peak-to-peak noise

def filter60HzAndHarmonics(id_data, timestamps):
	id_filtered = id_data
	return id_filtered	# TODO: given id_data and timestamps, return the data after filtering 60 Hz and harmonic noise
	
def extractNoiseMagnitude(deviceHistory, groupBy=None):
	# === Extract noise magnitude from data ===
	gateVoltages = []
	drainVoltages = []
	unfilteredNoise = []
	filteredNoise = []
	for i in range(len(deviceHistory)):
		vgs = deviceHistory[i]['runConfigs']['NoiseCollection']['gateVoltage']
		vds = deviceHistory[i]['runConfigs']['NoiseCollection']['drainVoltage']
		timestamps = deviceHistory[i]['Results']['timestamps']
		id_unfiltered = deviceHistory[i]['Results']['id_data']
		id_filtered = filter60HzAndHarmonics(id_unfiltered, timestamps) 
		
		gateVoltages.append(vgs)
		drainVoltages.append(vds)
		unfilteredNoise.append(noiseFromData(id_unfiltered))
		filteredNoise.append(noiseFromData(id_filtered))
		
	# === Group data into sub-arrays ===
	gateVoltages_sorted = []
	drainVoltages_sorted = []
	unfilteredNoise_sorted = []
	filteredNoise_sorted = []
	if(groupBy == 'drain'):
		# Get a set of unique drainVoltages, and group other arrays accordingly
		for i in range(len(gateVoltages)):	
			if(drainVoltages[i] in drainVoltages_sorted):
				index = drainVoltages_sorted.index(drainVoltages[i])
				gateVoltages_sorted[index].append(gateVoltages[i])
				unfilteredNoise_sorted[index].append(unfilteredNoise[i])
				filteredNoise_sorted[index].append(filteredNoise[i])
			else:
				drainVoltages_sorted.append(drainVoltages[i])
				gateVoltages_sorted.append([gateVoltages[i]])
				unfilteredNoise_sorted.append([unfilteredNoise[i]])
				filteredNoise_sorted.append([filteredNoise[i]])
		
		# Sort outer-level arrays by V_DS
		drainVoltages_sorted, gateVoltages_sorted, unfilteredNoise_sorted, filteredNoise_sorted = (list(elem) for elem in zip(*sorted(zip(drainVoltages_sorted, gateVoltages_sorted, unfilteredNoise_sorted, filteredNoise_sorted))))	
		for i in range(len(gateVoltages_sorted)):
			# Sort inner-level arrays by V_GS
			gateVoltages_sorted[i], unfilteredNoise_sorted[i], filteredNoise_sorted[i] = (list(elem) for elem in zip(*sorted(zip(gateVoltages_sorted[i], unfilteredNoise_sorted[i], filteredNoise_sorted[i]))))	
	elif(groupBy == 'gate'):	
		# Get a set of unique gateVoltages, and group other arrays accordingly
		for i in range(len(gateVoltages)):	
			if(gateVoltages[i] in gateVoltages_sorted):
				index = gateVoltages_sorted.index(gateVoltages[i])
				drainVoltages_sorted[index].append(drainVoltages[i])
				unfilteredNoise_sorted[index].append(unfilteredNoise[i])
				filteredNoise_sorted[index].append(filteredNoise[i])
			else:
				gateVoltages_sorted.append(gateVoltages[i])
				drainVoltages_sorted.append([drainVoltages[i]])
				unfilteredNoise_sorted.append([unfilteredNoise[i]])
				filteredNoise_sorted.append([filteredNoise[i]])
		
		# Sort outer-level arrays by V_GS
		gateVoltages_sorted, drainVoltages_sorted, unfilteredNoise_sorted, filteredNoise_sorted = (list(elem) for elem in zip(*sorted(zip(gateVoltages_sorted, drainVoltages_sorted, unfilteredNoise_sorted, filteredNoise_sorted))))	
		for i in range(len(gateVoltages_sorted)):
			# Sort inner-level arrays by V_DS
			drainVoltages_sorted[i], unfilteredNoise_sorted[i], filteredNoise_sorted[i] = (list(elem) for elem in zip(*sorted(zip(drainVoltages_sorted[i], unfilteredNoise_sorted[i], filteredNoise_sorted[i]))))	
	else:
		# Don't group into sub-arrays
		gateVoltages_sorted = gateVoltages
		drainVoltages_sorted = drainVoltages
		unfilteredNoise_sorted = unfilteredNoise
		filteredNoise_sorted = filteredNoise
		
	return gateVoltages_sorted, drainVoltages_sorted, unfilteredNoise_sorted, filteredNoise_sorted
	
