from flask import Flask, jsonify, request
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

@app.route('/trend/<int:smooth>/',methods = ['GET'])
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
      
      temp = df[label].values
      tm = [i for i in range(len(temp))]
      """pd.date_range('1-1-2013', periods=len(temp), freq='D')"""
      temp = pd.Series(temp, index=tm , name = 'TIME')
      series = np.array(temp.values)
      season = int(smooth/(1.5))
      if(season%2==0):
            season = season+1
      
      stl = STL(temp, trend=smooth,seasonal=season,robust=True)
      res = stl.fit()
      tt = res.trend
      fig = Figure()
      plt = fig.add_subplot(1, 1, 1)
      plt.grid(True)
      plt.plot(tt,color='red')
      plt.set_title("Trend graph")
      plt.set_ylabel(label)
      plt.set_xlabel("Time(seconds)")
      output = io.BytesIO()
      FigureCanvas(fig).print_png(output)
      return Response(output.getvalue(), mimetype='image/png')
  
@app.route('/summary',methods = ['GET'])
def print_summary():
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
      c = (df.corr(method='spearman'))
      carr = np.array(c)
      label_list = list(c.index)
      if(label not in label_list):
            return "Wrong label name entered!"
      label_ind = label_list.index(label)
      affectors = []
      for i in range(len(label_list)):
            if(not math.isnan(carr[label_ind][i]) and abs(carr[label_ind][i])>=0.4):
                  affectors.append((label_list[i],carr[label_ind][i]))
      answer = ("THE FOLLOWING VARIABLES MAY HAVE AFFECTED THE %s! - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - - - - - - - - - - - - - - - - -  - - - -  - -  - - - -  - -"%(label))
      for i in range(len(affectors)):
            name,num = affectors[i][0],affectors[i][1]
            if(name==label):
                  continue
            answer+=(name+" -> ("+str(float("%.2f"%num))+") ") 
            answer+="\n"
      return answer

if __name__ == '__main__': 
	app.run(debug = True) 
