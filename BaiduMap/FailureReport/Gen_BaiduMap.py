# -*- coding: utf-8 -*-

import pandas as pd
import re

if __name__ == "__main__":

    df = pd.read_csv("failure_report.csv")
    lng_ts = df["经纬度"].apply(lambda x: re.findall("\d+.\d+",x)[0])
    lat_ts = df["经纬度"].apply(lambda x: re.findall("\d+.\d+",x)[1])
    #打开HTML页面模版代码
    with open("Map_module.txt",'r',encoding='utf-8') as f:
        html = f.read()
        f.close()
        
    f = open("lng_lat.json","w")
    for ind_ in df.index:
        
        title_ = df.loc[ind_]["编号"]
        date_ = df.loc[ind_]["日期"][:-5]
        lat_,lng_ = lat_ts.loc[ind_], lng_ts.loc[ind_]
        
        str_temp = '{"lat_":' + str(lat_) + ',"lng_":' + str(lng_) + \
                    ',"title_":'+ '"' + str(title_)+'"' +',"date_":' + '"' + date_ + '"' +  '},'
        f.write(str_temp)
    
    f.close()
    
    #打开经纬度数据的json文件
    with open("Map_Report.html","w",encoding='utf-8') as f:
        with open("lng_lat.json","r") as f1:
            #置换HTML代码中的地图点参数部分以及标题部分
            points = f1.read()
            points = 'var points = [' + points + ']'
            f1.close()
            html = html.replace("__VARPOINTS",points)
            html = html.replace("__VARTITLE","管道事故记录地点分布示意图")
            print(html)
            f.write(html)
            f.close()
        