# -*- coding: utf-8 -*- 

import pandas as pd
import numpy as np
import re
import pdb

if __name__ == "__main__":
    
    report = pd.read_csv("failure_report.csv")

    serialno_df = pd.read_csv("lon_lat_serialno.csv")

    lng_ts = report["经纬度"].apply(lambda x:re.findall("\d+.\d+",x)[0]).astype(np.float32)
    lat_ts = report["经纬度"].apply(lambda x:re.findall("\d+.\d+",x)[1]).astype(np.float32)
        
    report_ser_list = []
    counter = 1
    num_reports = len(report)
    for ind_ in report.index:
        print("processing the %s of %s reports:"%(counter,num_reports),report.loc[ind_]["编号"])
        diff_lng = serialno_df["LON"]-lng_ts[ind_]
        diff_lat = serialno_df["LAT"]-lat_ts[ind_]
        dist_ = abs(diff_lng)+abs(diff_lat)
        report_ser_list.append(int(serialno_df.loc[dist_.argmin()]["SERIALNO"]))
        counter += 1
    
    report["SERIALNO"] = report_ser_list
    pdb.set_trace()
    report.to_csv("failure_report.csv",index=False,encoding="utf_8_sig")
    
    
    
    
    