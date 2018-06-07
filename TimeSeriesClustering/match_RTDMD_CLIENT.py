# -*- coding: utf-8 -*-

'''

主键对应关系为：
rtdmd.mid -> meterinfo.oid , meterinfo.cid -> clientinfo.oid
测点坐标在clientinfo表的GPSLON/GPSLAT字段中，
这样就可以通过对应关系提取RTDMD的测点坐标。

得到的RTDMD_LOCATION表中有四个字段，
RTDMD_MID：对应RTDMD表中的MID
CLIENT_OID：对应ICG_CLIENTINFO表中的OID
GPSLAT/GPSLON：经纬度坐标
'''

import pandas as pd
import numpy as np
import pdb
import os
import gc

if __name__ == "__main__":

    rtdmd_list = [file for file in os.listdir() if "RTDMD" in file and "HT" not in file]
    client = pd.read_csv("ICG_CLIENTINFO.csv",engine="python").dropna(how="all")
    meter = pd.read_csv("ICG_METERINFO.csv",engine="python").dropna(how="all")
           
    rtdmd_serialno = []    
    
    "由于测点数目在增加和减少，从所有RTDMD表中汇总所有的测点序列号及其对应位置关系"
    counter = 1
    for rtd in rtdmd_list:
        print("processing the %s of %s RTDMD."%(counter,len(rtdmd_list)))
        rtd_df = pd.read_csv(rtd)
        rtd_mid = rtd_df.MID.unique().tolist()
        rtdmd_serialno = list(set(rtdmd_serialno).union(set(rtd_mid))) # 取并集
        counter += 1
    
    ser_ts = pd.Series(rtdmd_serialno)
    ser_ts.to_csv("RTDMD_MID.csv",encoding="utf_8_sig",index=False)
    
    gc.collect()
    pdb.set_trace()
    
    
    # rtdmd_serialno = pd.read_csv("RTDMD_MID.csv")
    # rtdmd_serialno = rtdmd_serialno.SERIALNO.values.tolist()
    
    meter_oid = meter.OID.unique().tolist()
    rtdmd_serialno = list(set(rtdmd_serialno).intersection(set(meter_oid))) # 取交集
    rtdmd_ser_df = pd.DataFrame({"OID":rtdmd_serialno})
    
    rtdmd_met = pd.merge(rtdmd_ser_df,meter,on="OID") # 取交集
    rtdmd_met = rtdmd_met.rename(columns={"OID":"RTDMD_MID"})
    rtdmd_met = rtdmd_met.rename(columns={"CID":"OID"})
     
    rtdmd_client = pd.merge(rtdmd_met,client,on="OID") # 取交集
    rtdmd_client = rtdmd_client.rename(columns={"OID":"CLIENT_OID"})
    
    feature_list = ["RTDMD_MID","CLIENT_OID","GPSLON","GPSLAT"]
    rtdmd_client = rtdmd_client[feature_list]
    
    rtdmd_client.to_csv("RTDMD_LOCATION.csv",index=False,encoding="utf_8_sig")
    # pdb.set_trace()
    
    
    
    
    
    
    
    
    
    
    
    
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    

