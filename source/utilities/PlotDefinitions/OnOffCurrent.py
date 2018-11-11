from utilities.MatplotlibUtility import *



plotDescription = {
	'plotCategory': 'device',
	'dataFileDependencies': ['GateSweep.json'],
	'plotDefaults': {
		'figsize':(3.1,2.4),#(2*2.2,2*1.7),#(5,4),
		'time_label':'Time [{:}]',
		'index_label':'Time Index of Gate Sweep [#]',
		'ylabel':'$I_{{ON}}$ [$\\mu$A]',
		'ylabel_dual_axis':'$I_{{OFF}}$ [nA]',
		'vds_label': '$V_{{DS}}^{{Hold}}$ [V]',
		'vgs_label': '$V_{{GS}}^{{Hold}}$ [V]',
		'subplot_height_ratio':[3,1],
		'subplot_width_ratio': [1],
		'subplot_spacing': 0.03
	},
}

def plot(deviceHistory, identifiers, mode_parameters=None):
	timescale = mode_parameters['timescale']
	plotInRealTime = mode_parameters['plotInRealTime']
	includeDualAxis = mode_parameters['includeDualAxis']
	
	# Check if V_DS or V_GS are changing during this experiment
	vds_setpoint_values = [jsonData['runConfigs']['StaticBias']['drainVoltageSetPoint'] for jsonData in deviceHistory]
	vgs_setpoint_values = [jsonData['runConfigs']['StaticBias']['gateVoltageSetPoint'] for jsonData in deviceHistory]
	vds_setpoint_changes = min(vds_setpoint_values) != max(vds_setpoint_values)
	vgs_setpoint_changes = min(vgs_setpoint_values) != max(vgs_setpoint_values)
	if(not (vds_setpoint_changes or vgs_setpoint_changes)):
		includeDualAxis = False
	
	# Init Figure
	if(includeDualAxis):
		fig, (ax1, ax3) = initFigure(2, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'], shareX=True, subplotWidthRatio=plotDescription['plotDefaults']['subplot_width_ratio'], subplotHeightRatio=plotDescription['plotDefaults']['subplot_height_ratio'])
		ax4 = ax3.twinx() if(vds_setpoint_changes and vgs_setpoint_changes) else None

		vds_ax = ax3
		vgs_ax = ax4 if(vds_setpoint_changes) else ax3
	else:
		fig, ax1 = initFigure(1, 1, plotDescription['plotDefaults']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
		ax3, ax4 = None, None
	ax2 = ax1.twinx() if(mode_parameters['includeOffCurrent']) else None
	if(not mode_parameters['publication_mode']):
		ax1.set_title(getTestLabel(deviceHistory, identifiers))
	
	# If timescale is unspecified, choose an appropriate one based on the data range
	if(timescale == ''):
		timescale = bestTimeScaleFor(flatten(deviceHistory[-1]['Results']['timestamps'])[-1] - flatten(deviceHistory[0]['Results']['timestamps'])[0])
	
	# Rescale timestamp data by factor related to the time scale
	deviceHistory = scaledData(deviceHistory, 'Results', 'timestamps', 1/secondsPer(timescale))
	
	# Build On/Off Current lists
	onCurrents = []
	offCurrents = []
	timestamps = []
	blacklisted = []
	for i, deviceRun in enumerate(deviceHistory):
		if(abs(deviceRun['runConfigs']['GateSweep']['drainVoltageSetPoint']) > 0):
			onCurrents.append(deviceRun['Computed']['onCurrent'] * 10**6)
			offCurrents.append(deviceRun['Computed']['offCurrent'] * 10**9)
			timestamps.append(flatten(deviceRun['Results']['timestamps'])[0])
		else:
			blacklisted.append(i)
	# Get rid of V_DS = 0 sweeps (not meaningful)
	for i in blacklisted:
		del deviceHistory[i]
	
	if(len(deviceHistory) <= 0):
		return 
	
	# Plot On Current
	if(plotInRealTime):
		line = plotOverTime(ax1, timestamps, onCurrents, plt.rcParams['axes.prop_cycle'].by_key()['color'][3], offset=0, markerSize=3, lineWidth=0)
	else:
		line = ax1.plot(range(len(onCurrents)), onCurrents, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][3], marker='o', markersize=3, linewidth=0, linestyle=None)[0]
	setLabel(line, 'On-Currents')
	ax1.set_ylim(bottom=0)
	axisLabels(ax1, y_label=plotDescription['plotDefaults']['ylabel'])
	
	# Plot Off Current
	if(mode_parameters['includeOffCurrent']):
		if(plotInRealTime):
			line = plotOverTime(ax2, timestamps, offCurrents, plt.rcParams['axes.prop_cycle'].by_key()['color'][1], offset=0, markerSize=2, lineWidth=0)
		else:
			line = ax2.plot(range(len(offCurrents)), offCurrents, color=plt.rcParams['axes.prop_cycle'].by_key()['color'][1], marker='o', markersize=2, linewidth=0, linestyle=None)
		setLabel(line, 'Off-Currents')
		ax2.set_ylim(top=max(10, max(offCurrents)))
		axisLabels(ax2, y_label=plotDescription['plotDefaults']['ylabel_dual_axis'])
	
	# Plot in Dual Axis
	if(includeDualAxis):
		time_offset = 0
		for i in range(len(deviceHistory)):
			t_0 = timestamps[0]
			t_i = timestamps[i]
			time_offset = (t_i - t_0)
			t_i_next = timestamps[i] + deviceHistory[i]['runConfigs']['StaticBias']['totalBiasTime']/secondsPer(timescale)

			if(vds_setpoint_changes):
				vds_line = plotOverTime(vds_ax, [timestamps[i], t_i_next], [deviceHistory[i]['runConfigs']['StaticBias']['drainVoltageSetPoint']]*2, plt.rcParams['axes.prop_cycle'].by_key()['color'][0], offset=time_offset)
			if(vgs_setpoint_changes):
				vgs_line = plotOverTime(vgs_ax, [timestamps[i], t_i_next], [deviceHistory[i]['runConfigs']['StaticBias']['gateVoltageSetPoint']]*2, plt.rcParams['axes.prop_cycle'].by_key()['color'][3], offset=time_offset)
	
	# Add Legend
	lines1, labels1 = ax1.get_legend_handles_labels()
	lines2, labels2 = [],[]
	legendax = ax1
	if(mode_parameters['includeOffCurrent']):
		lines2, labels2 = ax2.get_legend_handles_labels()
		legendax = ax2
	legendax.legend(lines1 + lines2, labels1 + labels2, loc=mode_parameters['legendLoc'])

	if(includeDualAxis):
		if(plotInRealTime):
			ax3.set_xlabel(plotDescription['plotDefaults']['time_label'].format(timescale))
		else:
			ax3.set_xlabel(plotDescription['plotDefaults']['index_label'])
		if(vds_setpoint_changes):
			vds_ax.set_ylabel(plotDescription['plotDefaults']['vds_label'])
		if(vgs_setpoint_changes):
			vgs_ax.set_ylabel(plotDescription['plotDefaults']['vgs_label'])
		adjustAndSaveFigure(fig, 'OnAndOffCurrents', mode_parameters, subplotHeightPad=plotDescription['plotDefaults']['subplot_spacing'])
	else:
		if(plotInRealTime):
			ax1.set_xlabel(plotDescription['plotDefaults']['time_label'].format(timescale))
		else:
			ax1.set_xlabel(plotDescription['plotDefaults']['index_label'])
		adjustAndSaveFigure(fig, 'OnAndOffCurrents', mode_parameters)
	
	return (fig, (ax1, ax2, ax3, ax4))
	
	