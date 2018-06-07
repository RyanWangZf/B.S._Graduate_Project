# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import datetime
import pdb
import os
import re
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
    
if __name__ == "__main__":
    
    fig_path = ".\\figs"
    
    ts_path = ".\\RTDMD_processed"
    ts_files = os.listdir(ts_path)
    
    failure_report = pd.read_csv("failure_report.csv",parse_dates=[2])
    
    ts_df = pd.read_csv("typical_ts_of_2nd_clustering.csv")
    risk_dict = dict().fromkeys(ts_df.columns.tolist(),0)
    
    
    point_lng_lat = pd.read_csv("lon_lat_serialno.csv")
    
    
    lng_ts = failure_report["经纬度"].apply(lambda x:re.findall("\d+.\d+",x)[0])
    lat_ts = failure_report["经纬度"].apply(lambda x:re.findall("\d+.\d+",x)[1])
    
    counter = 1
    num_report = len(failure_report)
    for ind_ in failure_report.index:
        
        lng_,lat_ = np.float32(lng_ts[ind_]),np.float32(lat_ts[ind_])
        
        dist_ts = abs(point_lng_lat.LAT - lat_) + abs(point_lng_lat.LON-lng_)
        
        # 得到和事故地点最近的测点,后续可能要对最小距离确定一个threshold
        mean_dist = dist_ts.mean()
        ser_ = int(point_lng_lat.loc[dist_ts.argmin()].SERIALNO)
        
        # 得到事故发生的日期
        try:
            date_ = failure_report.loc[ind_]["日期"]
            date_ = datetime.datetime.strptime(date_,"%Y/%m/%d %H:%M")
        except:
            print(date_,"failed in processing, skip it.")
            counter += 1
            continue
        
        # 找到对应测点当日的日线，比较其与每个典型日线的dtw距离，找到最小距离的典型线
        ser_ts_ = str(ser_)+".csv"
        ser_ts_ = pd.read_csv(ts_path+"\\"+ser_ts_,index_col=[0],parse_dates=[0],engine="python")
        ser_ts_ = ser_ts_.resample("H").last().fillna(method="ffill")
        try: # 测试发生日期是否在2015年内
            this_ts = ser_ts_.loc[date_.strftime("%Y%m%d")].PRESSURE.copy()
        except:
            print("failure dates not found, skip it.",date_.strftime("%Y%m%d"))
            counter += 1
            continue
        this_ts_norm = (this_ts - this_ts.mean())/this_ts.std()
        
        dist_list = []
        col_list = ts_df.columns.tolist()
        for col in ts_df.columns:
            typical_ts = ts_df[col].copy()
            typical_ts = (typical_ts-typical_ts.mean())/typical_ts.std()
            
            dist_list.append(dtw(this_ts_norm,typical_ts))
        
        dist_ar = np.array(dist_list)
        min_col = col_list[np.argmin(dist_ar)]
        print("(%s of %s)find the minimum dtw dist point name: "%(counter,num_report),min_col)
        
        ax = plt.figure()
        typical_ts_ = (ts_df[min_col] - ts_df[min_col].mean())/(ts_df[min_col].std())
        plt.plot(typical_ts_.values,label="typical time-series")
        plt.plot(this_ts_norm.values,label="this day time-series")
        plt.legend()
        ax.savefig(fig_path+"\\"+failure_report.loc[ind_]["编号"],dpi=300)
        # plt.show()
        plt.close()
        risk_dict[min_col] += 1    
        counter += 1
    print(risk_dict)
    # pdb.set_trace()
            
    '''
        risk_dict = {'13300000039_1': 5, '13300000020_0': 68, '13300000011_7': 5, 
        '13300000061_3': 7, '13300000002_2': 0, '13300000039_6': 0, '13300000039_3': 0, 
        '13300000050_3': 87, '13300000007_4': 2, '13300000061_7': 3}
    
    '''
            
            
            
            
            
            
        
        
        
    
    















    
    