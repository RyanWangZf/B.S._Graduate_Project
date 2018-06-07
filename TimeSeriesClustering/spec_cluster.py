# -*- coding: utf-8 -*-
'''
get typical time series of every detecting points, save file as serialno + .csv 
把每个测点的八条典型日线存入Typical_TS目录下，每个文件名为测点序列号serialno + .csv
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pdb
import os
import gc

from sklearn.cluster import SpectralClustering
from multiprocessing import Pool


def proc_(df,dist_path,typical_ts_path):

    dist_file = str(int(df.SERIALNO[0])) + "_D.csv"
    # print("now",dist_file)
    dist = pd.read_csv(dist_path+"\\"+dist_file,engine="python")
    # print(dist.head())
    typ_name = str(int(df.SERIALNO[0])) + ".csv"
    typ_files_ = os.listdir(typical_ts_path)
    # print("now ",typ_name)
    if typ_name in typ_files_:
        print(typ_name," exists, skip it.")
        
    else:
        print(typ_name," processing...wait")
        date_list = df.index.normalize().unique().strftime("%Y%m%d")
        
        D = dist.fillna(50.0).values
        D = np.exp(-D**2/(2*10**2)) # gaussian kernel
        
        n_clusters = 8
        sc = SpectralClustering(n_clusters=n_clusters,affinity="precomputed")
        sc.fit(D)
        y = sc.labels_
        
        typ_df = pd.DataFrame()
        
        for i in range(n_clusters):
            
            dates_ = date_list[np.where(y==i)]
            D_part = D[np.where(y==i)]
            sum_list = [D_part[:,np.where(y==i)][j].sum() for j in range(len(dates_))]
            sum_ar = np.array(sum_list)
            for ind in np.argsort(sum_ar):
                ts_ = df.loc[dates_[ind]].PRESSURE
                if ts_.count() < 24: # NaN in timeseries
                    print("find NaN in timeseries %s, skip it"%(ts_.index[0].strftime("%Y%m%d")))
                    continue
                else:
                    typ_df[str(int(i))] = ts_.values
                    break
        
        
        typ_df.to_csv(typical_ts_path+"\\"+typ_name,index=False,encoding="utf_8_sig")
        
        print(typ_name," processed.")
    

if __name__ == "__main__":
    
    "把每个测点的八条典型日线存入Typical_TS目录下，每个文件名为测点序列号serialno + .csv"
    # global variables
    origin_path = ".\\RTDMD_processed"
    dist_path = ".\\DistMatrix"
    typical_ts_path = ".\\Typical_TS"
    
    origin_file = os.listdir(origin_path)
    
    file_counter = 0
    num_files = len(origin_file)
    files_ = []
    for file in origin_file:
        file_counter += 1
        files_.append(file)
        if np.mod(file_counter,4) == 0 and file_counter > 0:
            p = Pool(4)
            for p_num in range(4):
                file = files_[p_num]
                df = pd.read_csv(origin_path+"\\"+file,index_col=[0],parse_dates=[0],engine="python") # read csv with CN characters in path
                df = df.resample("H").last() # attention: some timeseries contain NaN
                p.apply_async(proc_,args=(df,dist_path,typical_ts_path))
            p.close()
            p.join()
            files_ = []
            print("%s of %s multiprocessing completed."%(file_counter,num_files))
            
        elif file_counter >= num_files: #处理剩下不到4个文件
            n_process = np.mod(file_counter,4)
            p = Pool(n_process)
            for p_num in range(n_process):
                file = files_[p_num]
                df = pd.read_csv(origin_path+"\\"+file,index_col=[0],parse_dates=[0],engine="python") # read csv with CN characters in path
                df = df.resample("H").last() # attention: some timeseries contain NaN
                p.apply_async(proc_,args=(df,dist_path,typical_ts_path))
            p.close()
            p.join()
            files_ = []
            print("%s of %s multiprocessing completed."%(file_counter,num_files))
            break
        

''' 
    dist = pd.read_csv("13300000002_D.csv")
    df = pd.read_csv("13300000002.csv",index_col=[0],parse_dates=[0])
    df = df.resample("H").last() # 有些日线存在缺失值，不能作为典型日线
    date_list = df.index.normalize().unique().strftime("%Y%m%d")
    
    D = dist.fillna(50.0).values
    D = np.exp(-D**2/(2*10**2)) # gaussian transformation
    
    n_clusters = 8
    sc = SpectralClustering(n_clusters=n_clusters,affinity="precomputed")
    # pdb.set_trace()
    sc.fit(D)
    y = sc.labels_
    subfig = n_clusters * 100 + 10
    "画距类内所有其他线距离最小的那条线，作为类的代表走势"
    for i in range(n_clusters):
        subfig += 1
        plt.subplot(subfig)
        dates_ = date_list[np.where(y==i)]
        D_part = D[np.where(y==i)]
        sum_list = [D_part[:,np.where(y==i)][j].sum() for j in range(len(dates_))]
        sum_ar = np.array(sum_list)
        for ind in np.argsort(sum_ar): # 检测典型日线是否有缺失,np.argsort升序，从小到大
            ts_ = df.loc[dates_[ind]].PRESSURE
            if ts_.count() < 24: # 日线存在缺失
                print("find missed data in day time series, skip it")
                continue
            else:
                plt.plot(ts_)
                break
        # pdb.set_trace()
    # plt.legend()
    plt.savefig("ts_clustering",dpi=300)
    plt.show()
'''

