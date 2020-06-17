from flask import Flask, request
import pandas as pd
import numpy as np
import math
from pandas import Series

import matplotlib.pyplot as plt
app = Flask(__name__)

import io
from pandas import Series
import random
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from statsmodels.tsa.seasonal import STL
import os


@app.route('/summary/trend.png/<int:smooth>/',methods = ['GET'])
def plotpng(smooth):
      if(smooth%2==0 or smooth<50):
            return "Error:smooth parameter must be odd! and greater than 50!"
      datafile = ""
      if('datafile' in request.args):      
            datafile = request.args['datafile']
      else:
            return "Error:Datafile not provided!"
      if(not (os.path.exists(datafile) and os.path.isfile(datafile))):
            return ("ERROR:File not found!!PLEASE ENTER CORRECT FILE NAME")
      df = pd.read_csv(datafile)
      label = ""
      if('label' in request.args):      
            label = request.args['label']
      else:
            return "label not provided!"      
      if(label not in list(df.columns)):
            return "Wrong label name entered!"

      if('period' in request.args):      
            freq = int(request.args['period'])
      else:
            return "period not provided!"
      if(freq>smooth):
            return "ERROR:period should be less than trend parameter!"
      timdiv = 3600 #1hour
      temp = df[label].values
      avgValue = df[label].iloc[0:2*timdiv].mean()
      avg = [avgValue for i in range(2*timdiv)]
      tm = [i for i in range(len(temp))]
      temp = pd.Series(temp, index=tm , name = 'TIME')
      series = np.array(temp.values)
      season = int(smooth/(1.5))
      if(season%2==0):
            season = season+1
      stl = STL(temp, trend=smooth,seasonal=season,period = freq,robust=True)
      res = stl.fit()
      tt = res.trend
      last = [tt[i] for i in range(timdiv)]
      cur = [tt[i] for i in range(timdiv,2*timdiv)]
      tm = [i for i in range(timdiv,2*timdiv)]
      cur = pd.Series(cur, index=tm , name = 'TIME')
      
      fig = Figure()
      plt = fig.add_subplot(1, 1, 1)
      plt.grid(True)
      plt.plot(avg,color='red')
      plt.plot(last,color='blue')
      plt.plot(cur,color='green')
      plt.set_title("Trend graph")
      plt.set_ylabel(label)
      plt.set_xlabel("Time(seconds)")
      plt.legend(['Mean','LASTWEEK','CURRWEEK'])
      output = io.BytesIO()
      FigureCanvas(fig).print_png(output)
      return Response(output.getvalue(), mimetype='image/png')#render_template('mpld3 plot.html',plot=fig_html)

@app.route('/summary/<int:smooth>',methods = ['GET'])
def print_summary(smooth):
      datafile = ""
      if('datafile' in request.args):      
            datafile = request.args['datafile']
      else:
            return "Error:Datafile not provided!"
      
      df = pd.read_csv(datafile)
      label = ""
      if('label' in request.args):      
            label = request.args['label']
      else:
            return "label not provided!"
      timdiv = 3600 #1hour
      dflastweek = df.iloc[0:timdiv]
      dfcurweek = df.iloc[timdiv:2*timdiv]
      
      c = (dflastweek.corr(method='spearman'))
      lastweek = np.array(c)
      
      c = (dfcurweek.corr(method='spearman'))
      curweek = np.array(c)
      label_list = list(c.index)
      
      if(label not in label_list):
            return "Wrong label name entered!"
      if('period' in request.args):      
            freq = int(request.args['period'])
      else:
            return "period not provided!"
      if(freq>smooth):
            return "ERROR:period should be less than trend parameter!"
      
      label_ind = label_list.index(label)
      posaffectors = []
      negaffectors=[]
      for i in range(len(label_list)):
            if(i==label_ind):
                  continue
            if(not math.isnan(curweek[label_ind][i])):
                  if(abs(curweek[label_ind][i])>=0.4):
                        if(curweek[label_ind][i]>0):
                              posaffectors.append((label_list[i],curweek[label_ind][i],lastweek[label_ind][i]))
                        else:
                              negaffectors.append((label_list[i],curweek[label_ind][i],lastweek[label_ind][i]))
                  elif(abs(curweek[label_ind][i]-lastweek[label_ind][i])>=0.2):
                        if(curweek[label_ind][i]>0):
                              posaffectors.append((label_list[i],curweek[label_ind][i],lastweek[label_ind][i]))
                        else:
                              negaffectors.append((label_list[i],curweek[label_ind][i],lastweek[label_ind][i]))
      answer="<h1 style=\"text-align:center;\">SUMMARY OF %s</h1>"%(label)
      answer+="<p><img src=\"trend.png\\"
      answer+=str(smooth)
      answer+="?label="
      answer+=label
      answer+="&datafile="
      answer+=datafile
      answer+="&period="
      answer+=str(freq)
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
                  answer+="INCREASED!! Last Week: ("+str(float("%.2f"%lastnum))+") "
            elif(curnum!=lastnum):
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
                  answer+="INCREASED!! Last Week: ("+str(float("%.2f"%lastnum))+") "
            elif(curnum!=lastnum):
                  answer+="DECREASED!! Last Week: ("+str(float("%.2f"%lastnum))+") "
            
            answer+="</p>"
      return answer

if __name__ == '__main__': 
	app.run(debug = True) 
