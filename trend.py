import pandas as pd
import numpy as np
from pandas import Series
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import STL

def period(s):
    w = np.fft.fft(s)
    wabs = np.absolute(w)
    wabs = np.delete(wabs, 0)
    index = np.argmax(wabs)
    index = index + 1
    period = len(s)/index
    return int(round(period))

df = pd.read_csv("DailyDelhiClimate.csv")
temp = df['meantemp'].values
temp = pd.Series(temp, index=pd.date_range('1-1-2013', periods=len(temp), freq='D'), name = 'TMP')
series = np.array(temp.values)
stl = STL(series, trend=951,seasonal=31,period = 30,robust=True)
res = stl.fit()
tt = res.trend
plt.plot(tt,color='red')
plt.title("Trend graph")
plt.ylabel("Temperature")
plt.xlabel("Days")
plt.show()