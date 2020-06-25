# Weekly Summary of Performance
## Trend Plot:
Plots trends of mentioned variable and its average over two consecutive weeks, thus helping the user to visually compare performance with previous week.

* **URL** 
 	`/trend.png`
* **URL Params**
    - Required:
        - datafile  - CSV and JSON formats are accepted
        - label - data label on which report is to be generated
    - Optional:
        - execspeed = [alphabet]      Speed of graph generation. 
            - “slow” 
            - “fast” are allowed options.  _default_ 
        - trendtype = [alphabet]            Smoothness of trend plot. 
            - “smooth”  _default_
            - “rough” are allowed values.
        - zoom = [integer]           Zoom feature for the graph
            - 0 _default_ - normal graph
            - 1 - graph supporting zoom  
![plot with trendtype = "smooth"](images/sm1_2.png)
![plot with trendtype = "rough"](images/ro1_2.png)
