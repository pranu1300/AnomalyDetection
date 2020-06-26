# Weekly Summary of Performance
## Trend Plot:
Plots trends of mentioned variable and its average over two consecutive weeks, thus helping the user to visually compare performance with previous week.

* **URL** 
 	`/trend.png`
* **URL Params**
    - Required:
        - datafile  : CSV and JSON formats are accepted
        - label : Data label on which report is to be generated
    - Optional:
        - execspeed = [alphabet]  :  Speed of graph generation
            - “slow” 
            - “fast”  _default_ 
        - trendtype = [alphabet]  :      Smoothness of trend plot 
            - “smooth”  _default_
            - “rough”
        - zoom = [integer]   :  Zoom feature for the graph
            - 0 _default_ - simple plot
            - 1 - plot supporting zoom  

>Example URL : <br>
>http://127.0.0.1:5000/summary?label=%sys&datafile=cpudata1.csv&zoom=0&output=html&execspeed=fast&trendtype=smooth

**Smooth vs Rough trend plots**<br>
![plot with trendtype = "smooth"](images/smooth400pixel.png) ![plot with trendtype = "rough"](images/rough400pixel.png)

## Weekly Performance Report:
* **URL** 
 	`/summary`
* **URL Params**
    - Required:
        - datafile  : CSV and JSON formats are accepted
        - label : Data label on which report is to be generated
    - Optional:
        - execspeed = [alphabet]  :  Speed of graph generation
            - “slow” 
            - “fast”  _default_ 
        - trendtype = [alphabet]  :      Smoothness of trend plot
            - “smooth”  _default_
            - “rough”
        - zoom = [integer]   :  Zoom feature for the graph
            - 0 _default_ - simple plot
            - 1 - plot supporting zoom  
        - output = [alphabet]  :      Format in which report is to be outputted
            - “html”  _default_
            - “json”

>Example URL :<br> 
>http://127.0.0.1:5000/summary?label=%sys&datafile=cpudata1.csv&zoom=0&output=html&execspeed=fast&trendtype=smooth

 #### Sample Output
 ##### html format
 ![html output](images/output.png)
 ##### **json format**<br>
 {<br>
            "curWeekStat": { <br>
                  "25%": 1.99,   "50%": 13.37,   "75%": 18.41,   "count": 4800.0,   "max": 77.41,   "maxIndex": 342.0,   "mean": 12.479,   <br>
                  "min": 0.0,   "minIndex": 4079.0,   "std": 10.7312 <br> 
            },  <br>
            "label":  "%usr", <br>
            "lastWeekStat": {<br> 
                  "25%": 1.99,  "50%": 13.75,   "75%": 18.41,   "count": 4800.0,   "max": 77.41,  "mean": 12.52,  "min": 0.0,   "std": 10.685<br>
           },  <br>
            "negAffectors":   [["%idle", -0.920078059280334, -0.9198306067804806 ]],  <br>
            "posAffectors":    [["%sys", 0.8597380031704872, 0.8576699089279437]], <br> 
            "trendPlotURL":   "/trend.png?label=%idle&datafile=cpudata1.csv"<br>
}<br>
>The variables negAffectors and posAffectors contains details of label which exhibit negative and positive correlations with the queried label. They are a list of lists containing label name, its correlation coeeficients with respect to queried label current week and last week in order. <br>

## Implementation:
Trend of data over weeks is extracted using Robust Seasonal Trend Decomposition method which is widely in use. The parameters for trend extraction are fixed based on the input to "trendtype" and "execspeed" variables i.e.
>period = 86400 for slow, smooth<br>
>period = 1440  for fast, smooth<br>
>period = 120 for rough (for both fast and slow )<br>
>seasonal=25 (doesn't matter much for trend graph)<br>
>trend = 1.5*(period)/(1-1.5/seasonal)<br>

_Note: The api requires the total input data to be of more than 2.5 weeks._

Correlation between different variables is extraced using Spearman’s rank correlation coefficient method, which is a better approach for a non-gaussian data. Also this is superior to regular pearson’s method in terms of sensitivity to outliers.<br>

The variables whose correlation coefficient with queried variable is greater than 0.4 (below which is weak correlation) and the ones whose coefficient value differed by more than 0.2 from that of last week are identified to be the primary contributors for the requested variables trend difference from previous week.<br>
