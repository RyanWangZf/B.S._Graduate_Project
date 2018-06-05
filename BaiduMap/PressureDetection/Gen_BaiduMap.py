# -*- coding: utf-8 -*-

import pandas as pd




if __name__ == "__main__":

    df = pd.read_csv("lon_lat_serialno.csv")
    #打开HTML页面模版代码
    with open("Map_module.txt",'r',encoding='utf-8') as f:
        html = f.read()
        f.close()
        
    f = open("lng_lat.json","w")
    for ind_ in df.index:
        
        title_ = df.loc[ind_].SERIALNO
        title_ = int(title_)
        lat_,lng_ = df.loc[ind_].LAT, df.loc[ind_].LON
        
        str_temp = '{"lat_":' + str(lat_) + ',"lng_":' + str(lng_) + \
                    ',"title_":'+ '"'+ str(title_)+'"' + '},'
        f.write(str_temp)
    
    f.close()
    
    #打开经纬度数据的json文件
    with open("Map_Serialno.html","w",encoding='utf-8') as f:
        with open("lng_lat.json","r") as f1:
            #置换HTML代码中的地图点参数部分以及标题部分
            points = f1.read()
            points = 'var points = [' + points + ']'
            f1.close()
            html = html.replace("__VARPOINTS",points)
            html = html.replace("__VARTITLE","SCADA测点分布示意图")
            print(html)
            f.write(html)
            f.close()
        