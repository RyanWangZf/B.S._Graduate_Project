# -*- coding: utf-8 -*-

# Python 3.6.2 AMD64
# 通过百度云麻点服务生成地图标点
# URL: http://lbsyun.baidu.com/jsdemo.htm#g0_4

import pandas as pd
import numpy as np

if __name__ == "__main__":

    #打开HTML页面模版代码
    with open("Map_module.txt",'r',encoding='utf-8') as f:
        html = f.read()
        f.close()
        
    #由管道文件 gasline_labeled.csv 获得数据点文件 lng_lat.json.
    f = open("lng_lat.json","w")
    df = pd.read_csv("gasline_labeled.csv")
    df = df.dropna()
    counter = 0
    for ind_ in df.index:
        if counter > 1000: # 最大上线的点个数，太大会导致html无法打开或加载极慢！
            break
        lng_,lat_ = df.loc[ind_].LON,df.loc[ind_].LAT
        title_ = df.loc[ind_].G3E_FID.astype(int)
        label_ = df.loc[ind_].label.astype(int)
        
        
        str_temp = '{"lat_":' + str(lat_) + ',"lng_":' + str(lng_) + \
                    ',"title_":'+ '"'+ str(title_)+'"'+ ',"label_":' +'"'+str(label_)+'"'+ '},'
        
        f.write(str_temp)
        counter += 1
    f.close()
        
    #打开经纬度数据的json文件
    with open("Map_Clustering.html","w",encoding='utf-8') as f:
        with open("lng_lat.json","r") as f1:
            #置换HTML代码中的地图点参数部分以及标题部分
            points = f1.read()
            points = 'var points = [' + points + ']'
            f1.close()
            html = html.replace("__VARPOINTS",points)
            html = html.replace("__VARTITLE","燃气管道聚类结果展示")
            print(html)
            f.write(html)
            f.close()