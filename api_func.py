import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import STL
import helper

def plot_analysis(data, period, trendSmoother, seasonalSmoother):
	color = ['g', 'b', 'm', 'c', 'y', 'r','olivedrab', 'indigo', 'darkblue']
	length = len(data)

	fig = plt.figure()

	n = 3
	ax1 = fig.add_subplot(str(n)+ "11")
	dataCur = np.array(data[length-period:length])
	dataPrev = np.array(data[length-2*period:length-period])
	# plt.plot(dataCur, label = 'data cur', color = color[0])
	# plt.plot(dataPrev, label = 'data prev')
	
	diffData = dataCur-dataPrev
	relativeData = diffData/dataPrev
	ax1.plot(diffData, label = 'diff data', color = color[1], linestyle=':')
	ax1.plot(relativeData, label = 'relative data', color = 'r', linestyle='--')
	
	ax2 = fig.add_subplot(str(n)+"12")

	stl = STL(data, trend=trendSmoother,seasonal=seasonalSmoother,period = period, robust=True)
	res = stl.fit()
	trend = res.trend

	stl = STL(dataPrev, trend=trendSmoother,seasonal=seasonalSmoother,period = period, robust=True)
	res = stl.fit()
	# prevTrend = res.trend
	prevTrend = trend[length-2*period:length-period]

	stl = STL(dataCur, trend=trendSmoother,seasonal=seasonalSmoother,period = period, robust=True)
	res = stl.fit()
	# curTrend = res.trend
	curTrend = trend[length-period:length]

	ax2.plot(prevTrend, label = 'prevTrend', color = color[0])
	ax2.plot(curTrend, label = 'curTrend', color = color[1])

	ax3 = fig.add_subplot(str(n)+"13")
	diffWrtPrevTrend = dataCur - prevTrend
	relativeWrtPrevTrend = diffWrtPrevTrend/prevTrend

	diffWrtCurTrend = dataCur - curTrend
	relativeWrtCurTrend = diffWrtCurTrend/curTrend

	ax3.plot(diffWrtPrevTrend, label = 'diffWrtPrevTrend', color = color[2])
	ax3.plot(relativeWrtPrevTrend, label = 'relativeWrtPrevTrend', color = color[3])
	ax3.plot(diffWrtCurTrend, label = 'diffWrtCurTrend', color = color[4])
	ax3.plot(relativeWrtCurTrend, label = 'relativeWrtCurTrend', color = color[5])

	fig.set_size_inches(18.5, 10.5)
	fig.legend()
	title = datasetName + " analysis2" 
	plt.savefig(title+".png")
	# plt.close()
	print(title, " done")

def plot_trendOld(data, period, nPeriods, trendSmoother, seasonalSmoother):
	if not len(data) == period*nPeriods:
		print("Error: Data size mismatch")
		return 
	color = ['g', 'b', 'm', 'c', 'y', 'r','olivedrab', 'indigo', 'darkblue']
	length = len(data)

	fig = plt.figure()
	for i in range(0, nPeriods):
		name = 'current' if i==0 else 'previous'
		miniDataSet = data[length-(i+1)*period:length-i*period]
		stl = STL(miniDataSet, trend=trendSmoother,seasonal=seasonalSmoother,period = period, robust=True)
		res = stl.fit()
		trend = res.trend
		plt.plot(trend, color=color[i], label=name)
	title = datasetName + " learning on current period"
	plt.title(title)
	fig.legend()
	plt.savefig("plots/"+title+".png")
	plt.close()
	print(title+ " done")

	fig = plt.figure()
	for i in range(0, nPeriods):
		name = 'current' if i==0 else 'previous'
		curData = data[length-(i+1)*period:length-i*period]
		plt.plot(curData, label = name+' data', color=color[i], linestyle=":")
	title = datasetName + " data of current period"
	plt.title(title)
	fig.legend()
	plt.savefig("plots/"+title+".png")
	plt.close()
	print(title+ " done")

def plot_trends(data, period, nPeriods, trendSmoother, seasonalSmoother):
	if len(data) < period*nPeriods:
		print("Error: Data size mismatch")
		print("data size ", len(data), " period*nPeriods ", period*nPeriods)
		return
	
	length = len(data)
	fig = plt.figure()
	stl = STL(data, trend=trendSmoother,seasonal=seasonalSmoother,period = period, robust=True)
	res = stl.fit()
	trend = res.trend
	
	color = ['g', 'b', 'm', 'c', 'y', 'r','olivedrab', 'indigo', 'darkblue']
	for i in range(0, nPeriods):
		name = 'current' if i==0 else 'previous'
		curPeriodTrend = trend[length-1*(i+1)*period:length-i*period]
		plt.plot(curPeriodTrend, label = name, color = color[i])
		
		trendAvg = sum(curPeriodTrend)/period
		trendAvg = np.full(period, trendAvg)
		plt.plot(trendAvg, label = name+' trendAvg avg', color=color[i], linestyle=':')

		curData = data[length-1*(i+1)*period:length-i*period]
		avg = sum(curData)/len(curData)
		avg = np.full(len(curData), avg)
		plt.plot(avg, label = name+' data avg', color=color[i], linestyle='--')
		
	title = datasetName + "_"+ str(length//period) 
	plt.title(title)
	fig.legend()
	plt.savefig("plots/"+title+".png")
	plt.close()
	print(title+ " done")


datasets = [
	{'filename':"data-praneeth.csv",
	 'id':"cpu usage", 
	 'observedlabel':'%usr',
	 'period': 3},
	{'filename':"DailyDelhiClimate.csv",
	 'id':"temperature", 
	 'observedlabel':"meantemp",
	 'period': 366},
	{'filename':"testset.csv",
	 'id':"hourlyTemp", 
	 'observedlabel':" _tempm"},
	{'filename':"minTemp.csv",
	 'id':"minTemp", 
	 'observedlabel':"Temp",
	 'period': 365}
	]#{'filename':, 'id':, 'observedlabel':}

if __name__ == "__main__":
	datasetIt = 3
	df = pd.read_csv("data/"+datasets[datasetIt]["filename"])
	datasetName = datasets[datasetIt]["id"]
	observedLabel = datasets[datasetIt]["observedlabel"]

	# print(list(df.columns))
	length = len(df.index)
	print("data size: ", length)
	periodExtracted = helper.period(df[observedLabel].values)
	print("period: ", periodExtracted)
	factors = helper.influencingFactors(observedLabel, df) 
	print("dependent factors: ", factors)
	
	# # plt.plot(df[observedLabel].values)
	# plt.show()
	
	#ask if it is to be determined by data or should be fixed by developers knowledge
	period = datasets[datasetIt]['period']
	nPeriods = 2 #number of periods analysed
	periodId = None #var to determine which periods data is to be analysed
	
	trendSmoother = 367
	seasonalSmoother = int(trendSmoother/(1.5))
	seasonalSmoother += (seasonalSmoother+1)%2

	dataTotal = df[observedLabel].values
	plot_analysis(dataTotal, period, trendSmoother, seasonalSmoother)
	plot_trends(dataTotal[-1*nPeriods*period:], period, nPeriods, trendSmoother, seasonalSmoother)
	for i in range(1, 4):
		x = pow(2, i)
		plot_trends2(dataTotal[-1*x*period:], period, nPeriods, trendSmoother, seasonalSmoother)
	plot_trends2(dataTotal, period, nPeriods, trendSmoother, seasonalSmoother)

	# plt.show()
