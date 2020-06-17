from flask import Flask, jsonify
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import STL
import helper

app = Flask(__name__)


def plot_trends(data, period, nPeriods, trendSmoother, seasonalSmoother):
	if not len(data) == period*nPeriods:
		print("Error: Data size mismatch")
		return 
	fig = plt.figure()
	for i in range(0, nPeriods):
		miniDataSet = data[i*period: (i+1)*period]
		stl = STL(miniDataSet, trend=trendSmoother,seasonal=seasonalSmoother,period = period, robust=True)
		res = stl.fit()
		trend = res.trend
		plt.plot(trend, label = str(i))
	title = "learning on current week"
	plt.title(title)
	fig.legend()
	plt.savefig(title+".png")
	plt.close()
	print(title+ " done")

def plot_trends2(data, period, nPeriods, trendSmoother, seasonalSmoother):
	if len(data) < period*nPeriods:
		print("Error: Data size mismatch")
		print("data size ", len(data), " period*nPeriods ", period*nPeriods)
		return
	
	length = len(data)
	fig = plt.figure()
	stl = STL(data, trend=trendSmoother,seasonal=seasonalSmoother,period = period, robust=True)
	res = stl.fit()
	trend = res.trend
	
	for i in range(0, nPeriods):
		curPeriodTrend = trend[length-1*(i+1)*period:length-i*period]
		plt.plot(curPeriodTrend, label = str(i))
	title = "learning data set size : "+ str(length//period)
	plt.title(title)
	fig.legend()
	plt.savefig(title+".png")
	plt.close()
	print(title+ " done")



if __name__ == "__main__":
	df = pd.read_csv("data-praneeth.csv")#DailyDelhiClimate.csv
	observedLabel = '%usr'
	
	# factors = helper.influencingFactors(observedLabel, df) 
	# print("dependent factors: ", factors)
	
	#ask if it is to be determined by data or should be fixed by developers knowledge
	period = 60
	nPeriods = 2 #number of periods analysed
	periodId = None #var to determine which periods data is to be analysed
	
	trendSmoother = 61
	seasonalSmoother = int(trendSmoother/(1.5))
	seasonalSmoother += (seasonalSmoother+1)%2

	dataTotal = df[observedLabel].values
	plot_trends(dataTotal[-1*nPeriods*period:], period, nPeriods, 61, 21)
	for i in range(1, 7):
		x = pow(2, i)
		plot_trends2(dataTotal[-1*x*period:], period, nPeriods, trendSmoother, seasonalSmoother)
	plot_trends2(dataTotal, period, nPeriods, trendSmoother, seasonalSmoother)

	plt.show()


# data = range(1, period*nPeriods+1)
	# length = len(data)
	# print(length, data[-1])
	# for i in range(0, nPeriods):
	# 	# print(-1*(i+1)*period, -1*i*period)
	# 	# print(data[-1*(i+1)*period:-1*i*period])
	# 	print(length-1*(i+1)*period, length-i*period)
	# 	print(data[length-1*(i+1)*period:length-i*period])
