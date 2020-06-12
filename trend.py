import pandas as pd
import numpy as np
from pandas import Series
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import STL

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

