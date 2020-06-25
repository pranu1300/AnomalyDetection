# Weekly Summary of Performance
## Trend Plot:
* **URL** 
 	`/trend.png`
* **URL Params**
    - Required:
        - datafile  - CSV and JSON formats are accepted
        - label - data label on which report is to be generated
    - Optional:
        - execspeed : _default: “fast”_ . 
      Speed of graph generation. “slow”, “fast” are allowed options.  
        - trendtype : _default: "smooth"_
       Smoothness of trend plot. “smooth” “rough” are allowed values.
        - zoom = [integer] - 
          Zoom feature for the graph
            - 0 _default_ - normal graph
            - 1 - graph supporting zoom  
