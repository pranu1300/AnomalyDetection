from flask import Flask, request
import pandas as pd
import numpy as np
import math
from pandas import Series

import matplotlib.pyplot as plt,mpld3
app = Flask(__name__)

import io
from pandas import Series
import random
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from statsmodels.tsa.seasonal import STL
import os

@app.route('/trendslow.png/<int:smooth>/',methods = ['GET'])
def plotpng1(smooth):
      if(smooth%2==0 or smooth<50):
            return "Error:smooth parameter must be odd! and greater than 50!"
      datafile = ""
      if('datafile' in request.args):      
            datafile = request.args['datafile']
      else:
            return "Error:Datafile not provided!"
      if(not (os.path.exists(datafile) and os.path.isfile(datafile))):
            return ("ERROR:File not found!!PLEASE ENTER CORRECT FILE NAME")
      if(datafile.endswith("json")):
            dfold = pd.read_json(datafile)
      elif(datafile.endswith("csv")):
            dfold = pd.read_csv(datafile)
      label = ""
      if('label' in request.args):      
            label = request.args['label']
      else:
            return "label not provided!"      
      if(label not in list(dfold.columns)):
            return "Wrong label name entered!"

      if('period' in request.args):      
            freq = int(request.args['period'])
      else:
            return "period not provided!"
      if(freq>smooth):
            return "ERROR:period should be less than trend parameter!"
      
      if('zoom' in request.args):
            zoom=int(request.args['zoom'])
            if(zoom!=0 and zoom!=1):
                  return "Error:Please enter either 0 or 1 in zoom"

      timdiv = 24*7*3600
      df = dfold.iloc[-2*timdiv:]
      strtingValue = int(2.5*timdiv)
      temp = dfold[label].iloc[-strtingValue:].values
      avgValue = df[label].iloc[-2*timdiv:-timdiv].mean()
      oldavg = [avgValue for i in range(timdiv)]
      avgValue = df[label].iloc[-timdiv:].mean()
      newavg = [avgValue for i in range(timdiv)]
      tm = [i for i in range(len(temp))]
      temp = pd.Series(temp, index=tm , name = 'TIME')
      season = int(smooth/(1.5))
      if(season%2==0):
            season = season+1
      season = 25
      tjump = int(0.10*smooth)
      sjump = int(0.10*season)
      stl = STL(temp,period=freq,trend=smooth,seasonal=season,trend_jump=tjump,seasonal_jump=sjump,robust=True)
      res = stl.fit()
      tt = res.trend
      sea = res.seasonal
      last = list(tt[-2*timdiv:-timdiv])
      cur = list(tt[-timdiv:])
      tm = [i for i in range(timdiv)]
      cur = pd.Series(cur, index=tm , name = 'TIME')
      
      fig = Figure()
      plt = fig.add_subplot(1, 1, 1)
      plt.grid(True)
      plt.plot(oldavg,color='red')
      plt.plot(newavg,color='yellow')
      plt.plot(last,color='blue')
      plt.plot(cur,color='green')
      plt.set_title("Trend graph")
      plt.set_ylabel(label)
      plt.set_xlabel("Time(seconds)")
      plt.legend(['LastWeekMean','CurWeekMean','LASTWEEK','CURWEEK'])
      output = io.BytesIO()
      FigureCanvas(fig).print_png(output)
      if(zoom==1):
            mpld3.show(fig)
      return Response(output.getvalue(), mimetype='image/png')

@app.route('/trendfast.png/<int:smooth>/',methods = ['GET'])
def plotpng2(smooth):
      if(smooth%2==0 or smooth<50):
            return "Error:smooth parameter must be odd! and greater than 50!"
      datafile = ""
      if('datafile' in request.args):      
            datafile = request.args['datafile']
      else:
            return "Error:Datafile not provided!"
      if(not (os.path.exists(datafile) and os.path.isfile(datafile))):
            return ("ERROR:File not found!!PLEASE ENTER CORRECT FILE NAME")
      if(datafile.endswith("json")):
            dfold = pd.read_json(datafile)
      elif(datafile.endswith("csv")):
            dfold = pd.read_csv(datafile)
      label = ""
      if('label' in request.args):      
            label = request.args['label']
      else:
            return "label not provided!"      
      if(label not in list(dfold.columns)):
            return "Wrong label name entered!"

      if('period' in request.args):      
            freq = int(request.args['period'])
      else:
            return "period not provided!"
      if(freq>smooth):
            return "ERROR:period should be less than trend parameter!"
      if('zoom' in request.args):
            zoom=int(request.args['zoom'])
            if(zoom!=0 and zoom!=1):
                  return "Error:Please enter either 0 or 1 in zoom"
      
      timdiv = 24*7*3600
      period=60
      df = dfold.iloc[-2*timdiv:]
      strtingValue = int(2.5*timdiv)
      temp=[]
      temp1 = dfold[label].iloc[-strtingValue:].values
      for i in range(0,len(temp1),period):
            sum=0.0
            for j in range(i,i+period):
                 sum+=temp1[j]
            sum = sum/period
            temp.append(sum)
      avgValue = df[label].iloc[-2*timdiv:-timdiv].mean()
      oldavg = [avgValue for i in range(timdiv//period)]
      avgValue = df[label].iloc[-timdiv:].mean()
      newavg = [avgValue for i in range(timdiv//period)]
      tm = [i for i in range(len(temp))]
      temp = pd.Series(temp, index=tm , name = 'TIME')
      season = int(smooth/(1.5))
      if(season%2==0):
            season = season+1
      season = 25
      tjump = int(0.15*smooth)
      sjump = int(0.15*season)
      stl = STL(temp,period=freq,trend=smooth,seasonal=season,trend_jump=tjump,seasonal_jump=sjump,robust=True)
      res = stl.fit()
      tt = res.trend
      timdiv = timdiv//period
      last = list(tt[-2*timdiv:-timdiv])#[tt[i] for i in range(timdiv)]
      cur = list(tt[-timdiv:])#[tt[i] for i in range(timdiv,2*timdiv)]
      tm = [i for i in range(timdiv)]
      cur = pd.Series(cur, index=tm , name = 'TIME')
      fig = Figure()
      plt = fig.add_subplot(1, 1, 1)
      plt.plot(oldavg,color='red')
      plt.plot(newavg,color='yellow')
      plt.plot(last,color='blue')
      plt.plot(cur,color='green')
      plt.set_title("Trend graph")
      plt.set_ylabel(label)
      if(period==60):
            plt.set_xlabel("Time(minutes)")
      else:      
            plt.set_xlabel("Time(seconds)")
      plt.legend(['LastWeekMean','CurWeekMean','LASTWEEK','CURWEEK'])
      output = io.BytesIO()
      FigureCanvas(fig).print_png(output)
      if(zoom==1):
            mpld3.show(fig)
      return Response(output.getvalue(), mimetype='image/png')

@app.route('/summary',methods = ['GET'])
def print_summary():
      execspeed="fast"
      trendtype="smooth"
      smooth=2299
      zoom=0
      datafile = ""
      if('datafile' in request.args):      
            datafile = request.args['datafile']
      else:
            return "Error:Datafile not provided!"
      
      if(not (os.path.exists(datafile) and os.path.isfile(datafile))):
            return ("ERROR:File not found!!PLEASE ENTER CORRECT FILE NAME")
      
      
      if('execspeed' in request.args):
            execspeed=request.args['execspeed']
            if(execspeed!="slow" and execspeed!="fast" ):
                  return "Error:Please enter fast or slow in execspeed"            
      
      if('trendtype' in request.args):
            trendtype=request.args['trendtype']
            if(trendtype!="smooth" and trendtype!="rough" ):
                  return "Error:Please enter rough or smooth in trendtype"
      if(trendtype=="rough"):
            freq=120
            smooth=201
      else:
            if(execspeed=="fast"):
                  freq=1440
                  smooth=2229
            else:
                  freq=86400
                  smooth = 1.5*freq*25
                  smooth = int(smooth/23.5)+1

      if('zoom' in request.args):
            zoom=int(request.args['zoom'])
            if(zoom!=0 and zoom!=1):
                  return "Error:Please enter either 0 or 1 in zoom"
      
      if(datafile.endswith("json")):
            dfold = pd.read_json(datafile)
      elif(datafile.endswith("csv")):
            dfold = pd.read_csv(datafile)
      label = ""
      if('label' in request.args):      
            label = request.args['label']
      else:
            return "label not provided!"
      timdiv = 24*7*3600#3600
      df = dfold.iloc[-2*timdiv:]
      dflastweek = df.iloc[0:timdiv]
      dfcurweek = df.iloc[timdiv:2*timdiv]
      lastweekstat = dflastweek[label].describe()
      curweekstat = dfcurweek[label].describe()
      lastweek = (dflastweek.corr(method='spearman'))
      curweek = (dfcurweek.corr(method='spearman'))
      label_list = list(curweek.index)      
      if(label not in label_list):
            return "Wrong label name entered!"
      
      if(freq>smooth):
            return "ERROR:period should be less than trend parameter!"
      
      posaffectors = []
      negaffectors=[]
      for i in range(len(label_list)):
            if(label_list[i]==label):
                  continue
            if(not math.isnan(curweek[label][i])):
                  if(abs(curweek[label][i])>=0.4):
                        if(curweek[label][i]>0):
                              posaffectors.append((label_list[i],curweek[label][i],lastweek[label][i]))
                        else:
                              negaffectors.append((label_list[i],curweek[label][i],lastweek[label][i]))
                  elif(abs(curweek[label][i]-lastweek[label][i])>=0.2):
                        if(curweek[label][i]>0):
                              posaffectors.append((label_list[i],curweek[label][i],lastweek[label][i]))
                        else:
                              negaffectors.append((label_list[i],curweek[label][i],lastweek[label][i]))
      answer="<h1 style=\"text-align:center;\">SUMMARY OF %s</h1>"%(label)
      answer+="<h2 style=\"color:violet;\">"
      answer+="STATS(CURWEEK vs LASTWEEK):"
      answer+="</h2>"
      answer+="<p style=\"font-size:120%;color:FireBrick;\">"
      answer+="MEAN: "+str(float("%.3f"%curweekstat[1]))+" , Last Week: "+str(float("%.3f"%lastweekstat[1]))
      answer+="</p>"
      answer+="<p style=\"font-size:120%;color:FireBrick;\">"
      maxind = list(dfcurweek[label].values).index(curweekstat[7])
      answer+="MAX: "+str(float("%.3f"%curweekstat[7]))+" at "+str(maxind+1+timdiv)+" seconds, Last Week: "+str(float("%.3f"%lastweekstat[7]))
      answer+="</p>"
      minind = list(dfcurweek[label].values).index(curweekstat[3])
      answer+="<p style=\"font-size:120%;color:FireBrick;\">"
      answer+="MIN: "+str(float("%.3f"%curweekstat[3]))+" at "+str(minind+1+timdiv)+" seconds, Last Week: "+str(float("%.3f"%lastweekstat[3]))
      answer+="</p>"
      if(execspeed=="slow"):
            answer+="<p><img src=\"trendslow.png\\"
      else:      
            answer+="<p><img src=\"trendfast.png\\"
      answer+=str(smooth)
      answer+="?label="
      answer+=label
      answer+="&datafile="
      answer+=datafile
      answer+="&period="
      answer+=str(freq)
      answer+="&zoom="
      answer+=str(zoom)
      answer+= "\"align=\"right\" /></p>"
      
      answer+= ("<h2>THE FOLLOWING VARIABLES MAY HAVE AFFECTED THE %s!</h1>"%(label))
      answer+="<h3 style=\"color:blue;\">POSITIVE EFFECT</h3>"
      if(len(posaffectors)==0):
            answer+="<p style=\"color:blue;\">"
            answer+="<--- NO POSTIVE AFFECTING VARIABLE FOUND! -->"
            answer+="</p>"
      for i in range(len(posaffectors)):
            name,curnum,lastnum = posaffectors[i][0],posaffectors[i][1],posaffectors[i][2]
            if(name==label):
                  continue
            answer+="<p style=\"font-size:140%;color:blue;\">"
            answer+=(name+":  ("+str(float("%.2f"%curnum))+") ")
            if(curnum>lastnum):
                  if(curnum-lastnum<0.1):
                        answer+="SLIGHTLY "
                  answer+="INCREASED!! Last Week: ("+str(float("%.2f"%lastnum))+") "
            elif(curnum!=lastnum):
                  if(curnum-lastnum<0.1):
                        answer+="SLIGHTLY "
                  answer+="DECREASED!! Last Week: ("+str(float("%.2f"%lastnum))+") "
            answer+="</p>"
      answer+="<h3 style=\"color:red;\">NEGATIVE EFFECT</h3>"
      if(len(negaffectors)==0):
            answer+="<p style=\"color:red;\">"
            answer+="<--- NO NEGATIVE AFFECTING VARIABLE FOUND! -->"
            answer+="</p>"
      for i in range(len(negaffectors)):
            name,curnum,lastnum = negaffectors[i][0],negaffectors[i][1],negaffectors[i][2]
            if(name==label):
                  continue
            answer+="<p style=\"font-size:140%;color:red;\">"
            answer+=(name+":  ("+str(float("%.2f"%curnum))+") ")
            if(curnum<lastnum):
                  if(abs(curnum-lastnum)<0.1):
                        answer+="SLIGHTLY "
                  answer+="INCREASED!! Last Week: ("+str(float("%.2f"%lastnum))+") "
            elif(curnum!=lastnum):
                  if(abs(curnum-lastnum)<0.1):
                        answer+="SLIGHTLY "
                  answer+="DECREASED!! Last Week: ("+str(float("%.2f"%lastnum))+") "
            
            answer+="</p>"
      return answer

if __name__ == '__main__': 
	app.run(debug = True) 
