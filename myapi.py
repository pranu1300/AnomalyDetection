from flask import Flask, request, Response, render_template
import pandas as pd, numpy as np
import math, random
import io, os
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from statsmodels.tsa.seasonal import STL
import matplotlib.pyplot as plt, mpld3
import json

app = Flask(__name__)

@app.errorhandler(404)
def page_not_found(e):
      errorMsg = "<h1>404</h1><p>The requested page/resource not found. Recheck URL and try again...</p>"
      errorMsg += "<p>"+ str(e) + "</p>"
      return errorMsg, 404

def moving_avg(y, n, centeredMean = True):
    y = np.insert(y, 0, 0)
    if centeredMean:
        y = np.concatenate((np.zeros((n-1)//2), y), axis = 0)
        y = np.concatenate((y, np.zeros(n//2)), axis = 0)
    y = np.nan_to_num(y)
    cumsum = np.cumsum(y)#cummulative sum
    mvgAvg = (cumsum[n:] - cumsum[:-n])/float(n)
    return mvgAvg

def sample(a, n):
    a = np.array(a)
    aPadded = np.pad(a.astype(float), (0, n - a.size%n), mode='constant', constant_values=0)
    aSampled = np.nanmean(aPadded.reshape(-1, n), axis = 1)
    return aSampled

@app.route('/trend.png',methods = ['GET'])
def plotpng():
      timdiv = 24*7*3600
      #default values
      period=60
      execSpeed="fast"
      trendType="smooth"
      smooth=2299#trend smoother length 
      freq = 1440
      zoom=0
      datafile = ""
      queriedLabel = ""
      
      if('datafile' in request.args):      
            datafile = request.args['datafile']
      else:
            return "Error: Datafile not provided!"
      
      if('label' in request.args):      
            queriedLabel = request.args['label']
      else:
            return "Error: label not provided!"      
      
      if('execspeed' in request.args):
            execSpeed=request.args['execspeed']
            if(execSpeed!="slow" and execSpeed!="fast" ):
                  return "Error: Invalid input to parameter 'execspeed'. Please enter fast or slow in execspeed"            
      
      if('trendtype' in request.args):
            trendType=request.args['trendtype']
            if(trendType!="smooth" and trendType!="rough" ):
                  return "Error: Invalid input to parameter 'trendtype'.Please enter rough or smooth in trendtype"
      
      if('zoom' in request.args):
            zoom=request.args['zoom']
            if(zoom!='0' and zoom!='1'):
                  return "Error: Invalid input to parameter 'zoom'. Please enter either 0 or 1 in zoom"
            zoom = int(zoom)

      if(not (os.path.exists(datafile) and os.path.isfile(datafile))):
            return ("ERROR:File not found!!PLEASE ENTER CORRECT FILE NAME")
      
      if(datafile.endswith("json")):
            dfComplete = pd.read_json(datafile)
      elif(datafile.endswith("csv")):
            dfComplete = pd.read_csv(datafile)
      
      if(queriedLabel not in list(dfComplete.columns)):
            return "Wrong label name entered!"

      if(trendType=="rough"):
            freq=120
            smooth=201
      elif(execSpeed == "slow"):
            freq=86400
            smooth = 1.5*freq*25
            smooth = int(smooth/23.5)+1
      
      df = dfComplete.iloc[-2*timdiv:]
      lastWeekMeanValue = df[queriedLabel].iloc[-2*timdiv:-timdiv].mean()
      curWeekMeanValue = df[queriedLabel].iloc[-timdiv:].mean()
      if execSpeed == "fast":
            curWeekMean = np.full(timdiv//period, curWeekMeanValue)
            lastWeekMean = np.full(timdiv//period, lastWeekMeanValue)
      else:
            curWeekMean = np.full(timdiv, curWeekMeanValue)
            lastWeekMean = np.full(timdiv, lastWeekMeanValue)

      strtingValue = int(2.5*timdiv)
      queriedLabelData = dfComplete[queriedLabel].iloc[-strtingValue:].values
      if execSpeed == "fast":
            queriedLabelData = sample(queriedLabelData, period)
            # queriedLabelData = moving_avg(queriedLabelData, period, True)
      queriedLabelData = pd.Series(queriedLabelData, index=range(len(queriedLabelData)) , name = 'Data')
      
      season = 25
      if execSpeed == "fast":
            trendJump = int(0.15*smooth)
            seasonalJump = int(0.15*season)
      else: 
            trendJump = int(0.1*smooth)
            seasonalJump = int(0.1*season)
      stl = STL(queriedLabelData,period=freq,trend=smooth,seasonal=season,trend_jump=trendJump,seasonal_jump=seasonalJump,robust=True)
      res = stl.fit()
      trendCurve = res.trend
      
      if execSpeed == "fast":
            timdiv = timdiv//period
      lastWeekTrend = list(trendCurve[-2*timdiv:-timdiv])
      curWeekTrend = list(trendCurve[-timdiv:])
      curWeekTrend = pd.Series(curWeekTrend, index=range(timdiv) , name = 'CurWeekTrend')
      
      fig = Figure()
      plt = fig.add_subplot(1, 1, 1)
      plt.plot(curWeekTrend, color='green', label='Current Week Trend')
      plt.plot(lastWeekTrend, color='blue', label='Last Week Trend')
      plt.plot(curWeekMean, color='darkgreen', label='Current Week Mean', linestyle="--")
      plt.plot(lastWeekMean, color='darkblue', label='Last Week Mean', linestyle="--")
      plt.legend()
      plt.set_title("Trend graph")
      plt.set_ylabel(queriedLabel)
      if(period==60 and execSpeed=="fast"):
            plt.set_xlabel("Time(minutes)")
      else:      
            plt.set_xlabel("Time(seconds)")
      output = io.BytesIO()
      FigureCanvas(fig).print_png(output)
      if(zoom==1):
            mpld3.show(fig)
      return Response(output.getvalue(), mimetype='image/png')

@app.route('/summary',methods = ['GET'])
def print_summary():
      datafile = ""
      if('datafile' in request.args):      
            datafile = request.args['datafile']
      else:
            return "Error:Datafile not provided!"
      
      if(not (os.path.exists(datafile) and os.path.isfile(datafile))):
            return ("ERROR:File not found!! PLEASE ENTER CORRECT FILE NAME")
      
      execSpeed = None
      if('execspeed' in request.args):
            execSpeed=request.args['execspeed']

      trendType = None      
      if('trendtype' in request.args):
            trendType=request.args['trendtype']
      
      zoom = None
      if('zoom' in request.args):
            zoom=int(request.args['zoom'])
      
      if(datafile.endswith("json")):
            dfTotal = pd.read_json(datafile)
      elif(datafile.endswith("csv")):
            dfTotal = pd.read_csv(datafile)
      
      queriedLabel = ""#name of data label on which weekly summary is requested
      if('label' in request.args):      
            queriedLabel = request.args['label']
      else:
            return "label not provided!"
      
      timdiv = 24*7*3600
      df = dfTotal.iloc[-2*timdiv:]
      dfLastWeek = df.iloc[0:timdiv]
      dfCurWeek = df.iloc[timdiv:2*timdiv]
      
      lastWeekStat = dfLastWeek[queriedLabel].describe()
      curWeekStat = dfCurWeek[queriedLabel].describe()
      lastWeekCorr = dfLastWeek.corr(method='spearman')[queriedLabel]
      curWeekCorr = dfCurWeek.corr(method='spearman')[queriedLabel]
      curMaxValIndex = list(dfCurWeek[queriedLabel].values).index(curWeekStat['max'])
      curMinValIndex = list(dfCurWeek[queriedLabel].values).index(curWeekStat['min'])

      labelList = list(curWeekCorr.index)
      if(queriedLabel not in labelList):
            return "Wrong label name entered!"
      
      posaffectors = []
      negaffectors=[]
      for label in labelList:
            if(label == queriedLabel):
                  continue
            if math.isnan(curWeekCorr[label]):#variable values aren't numeric
                  continue
            if abs(curWeekCorr[label])>=0.4 or abs(curWeekCorr[label]-lastWeekCorr[label])>=0.2:
                  if(curWeekCorr[label]>0):
                        posaffectors.append([label,curWeekCorr[label],lastWeekCorr[label]])
                  else:
                        negaffectors.append([label,curWeekCorr[label],lastWeekCorr[label]])

      return render_template("summary.html", datafile = json.dumps(datafile), label=json.dumps(queriedLabel), posaffectors = posaffectors, 
            negaffectors = negaffectors, lastWeekStat=lastWeekStat, curWeekStat = curWeekStat, maxValIndex = curMaxValIndex+1+timdiv, minValIndex = curMinValIndex+1+timdiv, 
            execSpeed = json.dumps(execSpeed), trendType = json.dumps(trendType), zoom = json.dumps(zoom))
      
if __name__ == '__main__': 
	app.run(debug = True) 
