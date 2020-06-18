import numpy as np
import pandas as pd

class Feature:
    observedFeature = 'Observed-feature'
    contributingFeature = 'Contibuting-feature'
    
    def __init__(self,  data = None, trend=None, seasonal=None, variableType = contributingFeature):
        self.variableType = variableType
        # self.cache = None
        self.data  = data#cache of data points of the variable
        self.trend = None
        self.period = 60
        self.trendSmoother = 61
        self.seasonalSmoother = 61 #
        self.trendCur = None
        self.trendCurSummary = None
        self.trendSummary = None
        
    def fit(self, data = None):
        if data is None:
            data = self.data
        series = np.array(data)
        stl = STL(series, trend=self.trendSmoother,seasonal=self.seasonalSmoother,period = self.period,robust=True)
        res = stl.fit()
        return res.trend

#-------------------------------------------#        
def period(series):# outputs period as an integer
    dft = np.fft.fft(series)
    dftAbs = np.absolute(dft)
    dftAbs = np.delete(dftAbs, 0)
    index = np.argmax(dftAbs)
    index = index + 1
    period = len(series)/index
    return int(round(period))

def firstDerivative(y):
    y = np.array(y)
    return np.diff(y)

#returns list of variables dependent with input variable
def influencingFactors(keyLabel: str, data :pd.DataFrame) -> list:
    correlationCoeffTreshold = 0.4
    cor = (data.corr(method='spearman'))#square matrix of correlations between any two variables
    label_list = list(cor.index)
    dependentLabels = []
    for label in label_list:
        if label == keyLabel:
            continue
        if abs(cor[label][keyLabel]) >= correlationCoeffTreshold:
            dependentLabels.append(label)
    return dependentLabels

