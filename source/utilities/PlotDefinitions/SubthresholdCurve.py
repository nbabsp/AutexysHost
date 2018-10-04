from ..MatplotlibUtility import *



plotDescription = {
	'plotDefaults': {
		'figsize':(2.8,3.2),
		'colorMap':'hot',
		'colorDefault': plt.rcParams['axes.prop_cycle'].by_key()['color'][0],
		'xlabel':'$V_{{GS}}^{{Sweep}}$ [V]',
		'ylabel':'$I_{{D}}$ [A]',
		'leg_vds_label':'$V_{{DS}}^{{Sweep}}$\n  = {:}V',
		'leg_vds_range_label':'$V_{{DS}}^{{min}} = $ {:}V\n'+'$V_{{DS}}^{{max}} = $ {:}V'
	}
}


def plot(deviceHistory, identifiers, mode_parameters=None):
	# Init Figure
	fig, ax = initFigure(1, 1, plot_parameters['SubthresholdCurve']['figsize'], figsizeOverride=mode_parameters['figureSizeOverride'])
	if(not mode_parameters['publication_mode']):
		ax.set_title(getTestLabel(deviceHistory, identifiers))
	
	# Build Color Map and Color Bar
	totalTime = timeWithUnits(deviceHistory[-1]['Results']['timestamps'][0][0] - deviceHistory[0]['Results']['timestamps'][-1][-1])
	holdTime = '[$t_{{Hold}}$ = {}]'.format(timeWithUnits(deviceHistory[1]['Results']['timestamps'][-1][-1] - deviceHistory[0]['Results']['timestamps'][0][0])) if(len(deviceHistory) >= 2) else ('[$t_{{Hold}}$ = 0]')
	colors = setupColors(fig, len(deviceHistory), colorOverride=mode_parameters['colorsOverride'], colorDefault=plot_parameters['SubthresholdCurve']['colorDefault'], colorMapName=plot_parameters['SubthresholdCurve']['colorMap'], colorMapStart=0.7, colorMapEnd=0, enableColorBar=mode_parameters['enableColorBar'], colorBarTicks=[0,0.6,1], colorBarTickLabels=[totalTime, holdTime, '$t_0$'], colorBarAxisLabel='')		

	# Plot
	for i in range(len(deviceHistory)):
		line = plotSubthresholdCurve(ax, deviceHistory[i], colors[i], direction=mode_parameters['sweepDirection'], fitSubthresholdSwing=False, includeLabel=False, lineStyle=None, errorBars=mode_parameters['enableErrorBars'])			
		if(len(deviceHistory) == len(mode_parameters['legendLabels'])):
			setLabel(line, mode_parameters['legendLabels'][i])

	axisLabels(ax, x_label=plot_parameters['SubthresholdCurve']['xlabel'], y_label=plot_parameters['SubthresholdCurve']['ylabel'])
	ax.yaxis.set_major_locator(matplotlib.ticker.LogLocator(numticks=10))
	
	# Add Legend and save figure
	addLegend(ax, loc=mode_parameters['legendLoc'], title=getLegendTitle(deviceHistory, identifiers, plot_parameters['SubthresholdCurve'], 'runConfigs', 'GateSweep', mode_parameters, includeVdsSweep=True, includeSubthresholdSwing=False))
	adjustAndSaveFigure(fig, 'FullSubthresholdCurves', mode_parameters)

	return (fig, ax)



