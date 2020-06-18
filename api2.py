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

app = Flask(__name__)

def plot_trends(data, period, nPeriods, trendSmoother, seasonalSmoother):
	if len(data) < period*nPeriods:
		print("Error: Data size mismatch")
		print("data size ", len(data), " period*nPeriods ", period*nPeriods)
		return
	
	length = len(data)
	fig = Figure()
	ax = fig.add_subplot(111)

	stl = STL(data, trend=trendSmoother,seasonal=seasonalSmoother,period = period, robust=True)
	res = stl.fit()
	trend = res.trend
	
	color = ['g', 'b', 'm', 'c', 'y', 'r','olivedrab', 'indigo', 'darkblue']
	for i in range(0, nPeriods):
		name = 'current' if i==0 else 'previous'
		curPeriodTrend = trend[length-1*(i+1)*period:length-i*period]
		ax.plot(curPeriodTrend, label = name, color = color[i])
		
		trendAvg = sum(curPeriodTrend)/period
		trendAvg = np.full(period, trendAvg)
		ax.plot(trendAvg, label = name+' trend avg', color=color[i], linestyle=':')

		curData = data[length-1*(i+1)*period:length-i*period]
		avg = sum(curData)/len(curData)
		avg = np.full(len(curData), avg)
		ax.plot(avg, label = name+' data avg', color=color[i], linestyle='--')
	
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
  	
	columns = df.columns
	label_list = list(columns)
	if(requestedLabel not in label_list):
		return "Wrong label name entered!" 

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
	currPeriodData = labelData[dataSize-period:dataSize]
	prevPeriodData = labelData[dataSize-2*period:dataSize-period]

	currPeriodAvg = helper.avg(currPeriodData)
	prevPeriodAvg = helper.avg(prevPeriodData)

	currPeriodMax = helper.avg(currPeriodData)
	prevPeriodMax = helper.avg(prevPeriodData)

	currPeriodMin = helper.avg(currPeriodData)
	prevPeriodMin = helper.avg(prevPeriodData)

	values = {	'Maximum value':{'This': currPeriodMax, 'Last': prevPeriodMax},
				'Minimum value':{'This': currPeriodMin, 'Last': prevPeriodMin},
				'Average value':{'This': currPeriodAvg, 'Last':prevPeriodAvg}}
	return render_template("summary.html",label=requestedLabel,trendGraph=pngImageB64String, values=values)
	# return Response(output.getvalue(), mimetype='image/png')

if __name__ == "__main__":
	app.run(debug=True)