# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import re
import pdb
import datetime
import matplotlib.pyplot as plt

def dtw(ts1,ts2):
    # ts1 : m , ts2 : n
    # get raw cross distance matrix D(n,m), d[i,j] = (ts1[i]-ts2[j])**2 or abs()
    # if need to compare 2 sequences with different unit or range, normalize both between input.
    m,n = len(ts1),len(ts2)
    
    d = np.zeros([n,m])
    for j in range(n):
        for i in range(m):
            d[j,i] = abs(ts1[i] - ts2[j])
     
    # get minimum sum length of warping path
    D = np.zeros([n+1,m+1])
    D[0,:] = np.inf
    D[:,0] = np.inf
    D[0,0] = 0
    for j in range(1,n+1):
        for i in range(1,m+1):
            D[j,i] = d[j-1,i-1]+min(D[j-1,i],D[j,i-1],D[j-1,i-1])
    
    return D[n,m]
    
def _split_MID(x):
    try:
        y = re.findall("133000000\d{2}",x)[0]
    except:
        y = np.nan
    return y
    

if __name__ == "__main__":
    
    rtd_path = ".\\RTDMD_2016"
    ts_path = ".\\report_ts_2016"
    fig_path = ".\\report_ts_figs"
    
    typical_ts = pd.read_csv("typical_ts_of_2nd_clustering.csv")
    
    report = pd.read_csv("failure_report.csv")
    report = report.loc[report["日期"]!="10月14日"].reset_index(drop=True)
    
    date_report = report["日期"].apply(lambda x:datetime.datetime.strptime(x,"%Y/%m/%d %H:%M"))
    report["日期"] = date_report
    
    report_2016 = report.loc[(report["日期"]>"20160101")&(report["日期"]<"20160801")].reset_index(drop=True)
    # pdb.set_trace()
    
    counter = 1
    num_report = len(report_2016)
    
    report_count_dict = dict().fromkeys(typical_ts.columns.tolist(),0) # 记录每一条模版线被匹配的次数
    
    for ind_ in report_2016.index:
        print("processing %s of %s"%(counter,num_report))
        date_ = report_2016.loc[ind_]["日期"]
        ser_ = report_2016.loc[ind_]["SERIALNO"]
        rtd_file = "RTDMD_" + date_.strftime("%Y%m%d")[2:] + ".csv"
        rtd_df = pd.read_csv(rtd_path+"\\"+rtd_file,index_col=[0],parse_dates=[0],engine="python")
        
        
        if ser_ not in rtd_df["SERIALNO"].unique():
            print("cannot find serialno %s in rtdmd file, skip it."%(ser_))
            counter += 1
            continue
        
        this_day = rtd_df.loc[rtd_df.SERIALNO == ser_].sort_index()
        ts_ = this_day.resample("H").first().fillna(method="ffill").PRESSURE
        ts_norm = (ts_ - ts_.mean())/ts_.std()
        
        dtw_dict = dict().fromkeys(typical_ts.columns.tolist(),0.0)
        for col in typical_ts.columns:
            typ_ts_norm = (typical_ts[col] - typical_ts[col].mean())/typical_ts[col].std()
            dtw_dict[col] = dtw(ts_norm,typ_ts_norm)
            
        min_col = min(dtw_dict,key=dtw_dict.get)
        report_count_dict[min_col] += 1 # 模版线与事故线匹配统计
        
        typ_ts_norm = (typical_ts[min_col]-typical_ts[min_col].mean())/typical_ts[min_col].std()
        plt.plot(ts_norm.values,label="this day time-series")
        plt.plot(typ_ts_norm,label="typical time-series")
        plt.legend()
        plt.savefig(fig_path+"\\"+report_2016.loc[ind_]["编号"],dpi=300)
        # plt.show()
        plt.close()
        
        # pdb.set_trace()   
        counter += 1
        
    print(report_count_dict)
    # pdb.set_trace()
    '''
    
report_count_dict = {'13300000039_1': 8, '13300000020_0': 127, '13300000011_7': 4, '13300000061_3':0,
    '13300000002_2': 0, '13300000039_6': 2, '13300000039_3': 3, '13300000050_3':43, '13300000007_4': 0,
    '13300000061_7': 10}
    
    '''
    
    
    
    
    
    
    
    
    
    