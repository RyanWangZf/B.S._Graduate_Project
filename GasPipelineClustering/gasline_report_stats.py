# -*- coding:utf-8 -*-
'''

Get risk ranking of clustering results of gas pipelines.

'''
import pandas as pd
import numpy as np
import re
import pdb
from sklearn.decomposition import PCA

if __name__ == "__main__":
    
    df_label = pd.read_csv("gasline_labeled.csv")
    
    report = pd.read_csv("failure_report.csv")
    
    report_lon = report["经纬度"].apply(lambda x:re.findall("\d+.\d+",x)[0]).astype(np.float32)
    report_lat = report["经纬度"].apply(lambda x:re.findall("\d+.\d+",x)[1]).astype(np.float32)
    
    dict_report = dict().fromkeys(np.arange(1,7),0)
    
    for ind_ in report_lon.index:
        
        lon_ = report_lon[ind_]
        lat_ = report_lat[ind_]
        
        df_label.LON.apply(lambda x: abs(x-lon_))
        
        diff_lat =  df_label.LAT.apply(lambda x: abs(x-lat_))
        diff_lon =  df_label.LON.apply(lambda x: abs(x-lon_))
        
        dist_sum = diff_lat + diff_lon
        print(ind_," min_dist: ",dist_sum.min())
        if dist_sum.min() < 0.001: # 只有在距离比较小的时候才能算到管道头上
            label = int(df_label.loc[dist_sum.argmin()].label+1)
            dict_report[label] += 1
    
    print(dict_report)
    # pdb.set_trace()

    
''' Results:

    label/report value_counts(min_dist):
         label    report    report/label
    1    5572       295         0.0529
    3    2719       204         0.0753
    5    1953       95          0.0486
    2    1517       94          0.0620
    6    1390       44          0.0316
    4      32       3           0.0937

    label/report value_counts(<0.001 min_dist):
        label    report    report/label
    1    5572       186         0.0334
    3    2719       122         0.0449
    5    1953       42          0.0215
    2    1517       73          0.0481
    6    1390       40          0.0288
    4      32       0           0.0000
    
    Conclusion:
    safe: 4,5
    normal: 6,1 
    risky: 2,3
    
    risky----->safe
    2,3,1,6,(5,4)
    
'''   
        
        
        