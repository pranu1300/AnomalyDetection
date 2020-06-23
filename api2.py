from flask import Flask, jsonify, request, Response, render_template
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from statsmodels.tsa.seasonal import STL
import io
import base64
import helper
import json

app = Flask(__name__)

def plot_trends(data, period, nPeriods, trendSmoother, seasonalSmoother):
	if len(data) < period*nPeriods:
		print("Error: Data size mismatch")
		print("data size ", len(data), " period*nPeriods ", period*nPeriods)
		return
	
	length = len(data)
	fig = Figure()
	ax = fig.add_subplot(111)

	# stl = STL(data, trend=trendSmoother,seasonal=seasonalSmoother,period = period, robust=True)
	# res = stl.fit()
	# trend = res.trend
	
	color = ['g', 'b', 'm', 'c', 'y', 'r','olivedrab', 'indigo', 'darkblue']
	# for i in range(0, nPeriods):
	# 	name = 'current' if i==0 else 'previous'
	# 	curPeriodTrend = trend[length-1*(i+1)*period:length-i*period]
	# 	ax.plot(curPeriodTrend, label = name, color = color[i])
		
	# 	trendAvg = sum(curPeriodTrend)/period
	# 	trendAvg = np.full(period, trendAvg)
	# 	ax.plot(trendAvg, label = name+' trend avg', color=color[i], linestyle=':')

	# 	curData = data[length-1*(i+1)*period:length-i*period]
	# 	avg = sum(curData)/len(curData)
	# 	avg = np.full(len(curData), avg)
	# 	ax.plot(avg, label = name+' data avg', color=color[i], linestyle='--')
	
	ax.set_xlabel("time")
	ax.set_ylabel("")
	ax.set_title("Summary")
	fig.legend()
	return fig	

#add sub directories or query parameters to specify 
#weekly/bi weekly/monthly etc  
#which week/month summary is to be provided
@app.route('/summary', methods=['GET'])
def generate_summary():
	datafile = ""
	if('datafile' in request.args):      
		datafile = request.args['datafile']
	else:
		return "Error:Datafile not provided!"
  
	df = pd.read_csv("data/"+datafile)
	requestedLabel = ""
	if('label' in request.args):
		requestedLabel = request.args['label']
	else:
		return "label not provided!"
  	
	label_list = list(df.columns)
	if(requestedLabel not in label_list):
		return "Wrong label name entered!" 

	timdiv = 3600 #1hour
	dflastweek = df.iloc[0:timdiv]
	dfcurweek = df.iloc[timdiv:2*timdiv]
      
	lastweek = dflastweek.corr(method='spearman')
      
	curweek = dfcurweek.corr(method='spearman')
	label_list = list(curweek.columns)

	dataSize = len(df.index)
	nPeriods = 2 
	# periodId = None #period for which summary is printed

	# observationWindow
	period = helper.period(df[requestedLabel].values)
	trendSmoother = period + 1 + (period)%2
	print(trendSmoother, period)
	seasonalSmoother = int(trendSmoother/(1.5))
	seasonalSmoother += (seasonalSmoother+1)%2

	labelData = df[requestedLabel].values
	nLearningPeriods = 4
	
	#trend graph
	fig = plot_trends(labelData[-1*nLearningPeriods*period:], period, nPeriods, trendSmoother, seasonalSmoother)
	
	output = io.BytesIO()
	FigureCanvas(fig).print_png(output)
	pngImageB64String = "data:image/png;base64,"
	pngImageB64String += base64.b64encode(output.getvalue()).decode('utf8')
    
    #performance report
	
	posaffectors = []
	negaffectors=[]
	for i in label_list:
		if(i==requestedLabel):
			continue
		if not np.isnan(curweek[requestedLabel][i]) and not np.isnan(lastweek[requestedLabel][i]):
			if (abs(curweek[requestedLabel][i])>=0.4) or (abs(curweek[requestedLabel][i]-lastweek[requestedLabel][i])>=0.2):
				if(curweek[requestedLabel][i]>0):
					posaffectors.append([i,curweek[requestedLabel][i],lastweek[requestedLabel][i]])
				else:
					negaffectors.append([i,curweek[requestedLabel][i],lastweek[requestedLabel][i]])
	
	dataCurWeek = dfcurweek[requestedLabel].values
	dataLasWeek = dflastweek[requestedLabel].values

	avgCurWeek = sum(dataCurWeek)/len(dataCurWeek)	
	avgLasWeek = sum(dataLasWeek)/len(dataCurWeek)

	minCurWeek = min(dataCurWeek)
	minLasWeek = min(dataLasWeek)

	maxCurWeek = max(dataCurWeek)
	maxLasWeek = max(dataLasWeek)

	# negaffectors = []
	# posaffectors = []
	values = {	'Maximum value':{'This': maxCurWeek, 'Last': maxLasWeek},
				'Minimum value':{'This': minCurWeek, 'Last': minLasWeek},
				'Average value':{'This': avgCurWeek, 'Last': avgLasWeek}}
	return render_template("summary.html",label=requestedLabel,trendGraph=pngImageB64String, posaffectors = posaffectors, negaffectors = negaffectors, values=values)
	# return Response(output.getvalue(), mimetype='image/png')

if __name__ == "__main__":
	app.run(debug=True)