# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
import pdb

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
    
    np.random.seed(84)

    rtd_path = "C:\\Users\\Administrator\\Desktop\\毕业论文\\汇报-第十二周\\RTDMD_2016"

    rtd_files = [file for file in os.listdir(rtd_path) if ".csv" in file]


    typical_df = pd.read_csv("typical_ts_of_2nd_clustering.csv")

    risk_dict = dict().fromkeys(typical_df.columns.tolist(),0)

    counter = 1
    num_file = len(rtd_files)

    for file in rtd_files:
        print("Processing %s of %s files..."%(counter,num_file))
        
        this_day = pd.read_csv(rtd_path+"\\"+file,engine="python",index_col=[0],parse_dates=[0])
        
        if counter == 1: # 初始化serialno list
            serial_list = this_day.SERIALNO.unique().tolist()
        
        sampling_ind = np.random.rand(len(serial_list))
        ser_chose = serial_list[np.argmax(sampling_ind)] # 被选中的测点序列号
        print("Select serialno is: ",ser_chose)
        
        this_ts = this_day.loc[this_day.SERIALNO == ser_chose].PRESSURE
        this_ts = this_ts.resample("H").first().fillna(method="ffill")
        
        this_ts_norm = (this_ts - this_ts.mean())/this_ts.std()
        
        
        dist_list = []
        col_list = typical_df.columns.tolist()
        for col in typical_df.columns: # 依次匹配典型线
            typi_ts = typical_df[col].copy()
            
            typi_ts_norm = (typi_ts - typi_ts.mean())/typi_ts.std()
            
            dist_list.append(dtw(typi_ts,this_ts_norm))
        
        min_col = col_list[np.argmin(np.array(dist_list))]
        risk_dict[min_col] += 1
        
        counter += 1
        
    pdb.set_trace()
    
    '''
    risk_dict = {'13300000039_1': 27, '13300000020_0': 0, '13300000011_7': 190, 
    '13300000061_3':0, '13300000002_2': 0, '13300000039_6': 0, '13300000039_3': 0,
    '13300000050_3':0, '13300000007_4': 0, '13300000061_7': 0}
    '''
    
    
    
    

