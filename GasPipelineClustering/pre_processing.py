# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pdb
import logging
import gc,os
import re

logging.basicConfig(level=logging.DEBUG)

np.random.seed(84) # set random seed

# params of matplotlib
plt.rc("font",family="SimHei",size=10) # 解决图像中文不显示的问题
plt.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题


def preprocessing():

    logging.debug("data preprocessing start...")
    # read excel and transform it to csv
    excel = pd.read_excel("GASLINE.xls")
    excel.to_csv("gasline.csv",index=False,encoding="utf_8_sig")
    
    # read csv
    gasline = pd.read_csv("gasline.csv")
    
    # drop anomaly data
    gasline = gasline.drop(gasline.JJSIZE == 0)
    
    # drop void date_build
    space_re = re.compile("\s+")
    for ind in gasline.index:
        tag = space_re.match(gasline.loc[ind].DATE_BUILD)
        if tag: # contains void date
            logging.debug("find void DATE_BUILD in %s, drop row"%ind)
            gasline = gasline.drop(ind)
    
    # fill zero length pipelines with median
    gasline.LENGTH.loc[gasline.LENGTH <= 0] = gasline.LENGTH.median()
    
    # select features
    selected_ft = ["G3E_FID","WARN_TAPE","JJSIZE","MATL",\
                    "PRESS_D","PRESS_O","DATE_BUILD","CONTRACTOR","SUPERVISOR",\
                    "SHAPE","LENGTH"]
                    
    gasline = gasline[selected_ft]
    
    # split col SHAPE , get coordinates x & y
    re_ = re.compile("\d{5}.\d{1,}")
    coord_x = []
    coord_y = []
    ts = gasline.SHAPE
    for ind in ts.index:
        res = re_.findall(ts[ind])
        coord_x.append(res[0])
        coord_y.append(res[1])
    gasline["coord_x"] = coord_x
    gasline["coord_y"] = coord_y
    
    # save gasline_attr.csv
    gasline.to_csv("gasline_attr.csv",index=False,encoding="utf_8_sig")
    logging.debug("data preprocessing complete")
    
def diameter(df):

    ts = df.JJSIZE.copy()
    weight = [0.54,0.256,0.119,0.092]
    thres = [127.0,279.4,431.8,584.2]
    ts.loc[ts<=thres[0]] = weight[0]
    ts.loc[(ts>thres[0]) & (ts<=thres[1])] = weight[1]
    ts.loc[(ts>thres[1]) & (ts<=thres[2])] = weight[2]
    ts.loc[ts>thres[2]] = weight[3]
    
    df["WEIGHTED_DIAMETER"] = ts.values

    return df
    
def material(df):
    
    ts = df.MATL.copy()
    ts.loc[ts == "G   钢管"] = "钢管"
    ts.loc[(ts == "PE   PE管") | (ts == "PES  PE塑料管")] = "PE管"
    ts.loc[(ts == "Z    铸铁管") | (ts == "QZ  球墨铸铁管") | (ts == "Z    灰口铸铁管") | \
            (ts == "QZ/G  球墨铸铁管/钢管") | (ts == "Q    球墨管")] = "铸铁管"
    ts.loc[(ts == "D   镀锌管")] = "镀锌管"
    
    # weighted_matl
    weight = [30,60,50,40]
    ts1 = pd.Series(np.zeros_like(ts))
    ts1.loc[ts == "钢管"] = 30.0
    ts1.loc[ts == "铸铁管"] = 60.0
    ts1.loc[ts == "PE管"] = 50.0
    ts1.loc[ts == "镀锌管"] = 40.0
    df["WEIGHTED_MATL"] = ts1
    return df
    
def warn_tape(df):
    "是否有警示标志，有为1，无为0"
    ts = df.WARN_TAPE.copy()
    ts.loc[(ts == " ") | (ts == "不适合") | (ts == "无")] = 0
    ts.loc[(ts == "有")] = 1
    df["WARN_TAPE"] = ts
    return df
    
def coord_to_lon_lat(df):
    "管道的局部坐标"
    cx = df.coord_x.copy()
    cy = df.coord_y.copy()
    lon,lat = [],[]
    # set basic coordinate data
    coord_a  = np.array([60618.433,42951.090])
    coord_b  = np.array([69029.179,54739.700])
    det_c = coord_b - coord_a
    lon_lat_a = np.array([120.69803,31.302065])
    lon_lat_b = np.array([120.786671,31.407982])
    det_l = lon_lat_b - lon_lat_a
    grad = det_l / det_c
    # calculate longitude and latitude of every point
    for ind in df.index:
        det = np.array([cx[ind] - coord_a[0],cy[ind] - coord_a[1]])
        lon.append((lon_lat_a + det*grad)[0])
        lat.append((lon_lat_a + det*grad)[1])
    df["LON"] = lon # longitude
    df["LAT"] = lat # latitude
    
    return df
    
def pressure(df):
    "处理压力特征，赋权"
    dataset = df.copy()
    
    weight_df = pd.DataFrame({"PRESS_O":["LP","MPB1","MPB2","MPA","IHP","HP"],"PRESS_O_WEIGHT":[0.01,0.07,0.2,0.4,0.8,2.5,]})
    dataset = pd.merge(dataset.reset_index(),weight_df,on="PRESS_O").sort_values(by="index").drop(["index"],axis=1).reset_index(drop=True)
    
    weight_df = pd.DataFrame({"PRESS_D":["LP","MPB1","MPB2","MPA","IHP","HP"],"PRESS_D_WEIGHT":[0.01,0.07,0.2,0.4,0.8,2.5,]})
    dataset = pd.merge(dataset.reset_index(),weight_df,on="PRESS_D").sort_values(by="index").drop(["index"],axis=1).reset_index(drop=True)
    
    return dataset
    
def date(df):

    import datetime
    "处理安装日期指标，分离为年、月、管龄、季节等指标"
    gasline = df.copy()
    
    get_date_1 = lambda x: datetime.datetime.strptime(x,"%Y-%m-%d %H:%M:%S")
    get_date_2 = lambda x: datetime.datetime.strptime(x,"%Y-%m-%d")
    date_build = gasline.DATE_BUILD
    date_build_age,date_build_season,date_build_month,date_build_year= [],[],[],[]
    season_dict = {"spring":[3,4,5],"summer":[6,7,8],"fall":[9,10,11],"winter":[12,1,2]}
    for ind in date_build.index:
        try: # cope with 2 different format of raw dates
            split_date = get_date_1(date_build[ind])
        except:
            split_date = get_date_2(date_build[ind])
        # new sample
        date_build_age.append((datetime.datetime(2018,1,1) - split_date).days) # age count untill 2018/1/1
        date_build_month.append(split_date.month)
        date_build_year.append(split_date.year)
        season = [k for k,v in season_dict.items() if split_date.month in v][0]
        date_build_season.append(season)

    gasline["date_build_age"] = date_build_age
    gasline["date_build_month"] = date_build_month
    gasline["date_build_season"] = date_build_season
    gasline["date_build_year"] = date_build_year
    
    return gasline
    
def contractor(df):
    "处理管道安装乙方的指标"
    dataset = df.copy()
    
    # 注册资本 单位: 万元， 0.0 是缺失或不详数据，中位值为6080
    con_cap = {'园区市政': 0.0,'园区配套供气':0.0 ,'泰兴机电':5312.9 ,' ': 0.0,'燃气集团': 2000.0,'天津管道': 13225.9,'天津众元':7075.5 ,
               '上海煤气第二管线':20000.0 ,'宏泰市政':2100.0 ,'南京煤气管线工程':2200.0 ,'潥阳市政': 2000.0,'江苏天力': 50218.0 ,
               '江苏华能': 3000.0, '南京燃气输配':2000.0 ,'江苏天目':30000.0 ,'华东勘察':5002.0 ,'管线工程公司': 0.0,'江苏中天市政':6080,
               '苏州四通':12100 ,'园区公用事业':0.0,'广西佳讯管道':2100.0,'苏州港华':20000.0,'苏州工业设备安装有限公司':6500.0,
               '河北建设':130000.0 ,'中油管道二公司':7200.0,'江苏石油勘探局':14228.0,'上海浦川水利':2000.0,'上海工业设备安装集团公司':1200.0}
               
    con = [k for k,v in con_cap.items()]
    capital = [v for k,v in con_cap.items()]
    
    cap = np.array(capital)
    cap[cap == 0] = 6080.0   # fill NaN with median
    capital = cap.tolist()
    
    
    weight_df = pd.DataFrame({"CONTRACTOR":con,"CONTRACTOR_WEIGHT":capital})
    
    dataset = pd.merge(dataset.reset_index(),weight_df,on="CONTRACTOR").sort_values(by="index").drop(["index"],axis=1).reset_index(drop=True)
    
    return dataset
    
def supervisor(df):
    "处理管道安装监理方指标"
    dataset = df.copy()
    # 注册资本 单位 万元，0.0为缺失值，将用中值填充
    sup_cap = {' ': 0.0, '裕廊环境工程':2773.908, '金陵石化监理':406.32, '新乡方圆建设监理':300.0, '南京长江监理':800.0, 
            '江苏国信':600.0, '园区监理':0.0,'园区中科院四方监理':0.0, '仪征化纤工程监理':500.0}
    sup = [k for k,v in sup_cap.items()]
    
    # fill NaN with median
    capital = [v for k,v in sup_cap.items()]
    cap = np.array(capital)
    cap[cap==0] = 550
    capital = cap.tolist()
    
    weight_df = pd.DataFrame({"SUPERVISOR":sup,"SUPERVISOR_WEIGHT":capital})
    
    dataset = pd.merge(dataset.reset_index(),weight_df,on="SUPERVISOR").sort_values(by="index").drop(["index"],axis=1).reset_index(drop=True)
    
    return dataset
    
def create_lon_lat():
    '''用于生成测点序列号及其经纬度位置的表格，
    因需与HT_RTDMD表和ICG_CLIENT表一一对照，无法直接运行'''
     
    file_path = "C:\\Users\\Administrator\\Desktop\毕业论文\\汇报-第十周\\HT_RTDMD"
    file_list = os.listdir(file_path)
    lon_lat_df = pd.DataFrame()
    
    icg = pd.read_csv("E:\\oracle_data\\ICG_CLIENTINFO.csv").dropna(how="all")
    counter = 1
    for file in file_list:
        logging.debug("processing %s which is %s of %s "%(file,counter,len(file_list)))
        path = file_path + "\\" + file
        rtd = pd.read_csv(path,encoding="utf_8_sig",engine="python")
        ser = rtd.SERIALNO[0]
        lon = icg.loc[icg.OID == str(ser)].GPSLON.values[0]
        lat = icg.loc[icg.OID == str(ser)].GPSLAT.values[0]
        rtd["LON"] = [lon] * len(rtd)
        rtd["LAT"] = [lat] * len(rtd)
        rtd.to_csv(path,index=False,encoding="utf_8_sig")
        lon_lat_df = pd.concat([lon_lat_df, pd.DataFrame({"serialno":[ser],"lon":[lon],"lat":[lat]})],axis=0).reset_index(drop=True)
        counter += 1
        del rtd; gc.collect()
    lon_lat_df.to_csv("lon_lat.csv",index=False,encoding="utf_8_sig")
    
def nearest_serialno(df):

    '''
    找到距每根管段最近的测点序列号，并存入gasline表格中
    lon_lat.csv由create_lon_lat函数生成
    '''
    lon_lat = pd.read_csv("lon_lat.csv")
    lon_lat_ar = lon_lat[["lon","lat"]].values
    
    ser_list = []
    counter = 0
    len_df = len(df)
    min_dist_list = []
    for ind in df.index:
        logging.debug("now processing the %s of %s"%(counter,len_df))
        ar_ = np.array([df.loc[ind].LON,df.loc[ind].LAT])
        dist = (ar_ - lon_lat_ar)**2
        dist = dist[:,0] + dist[:,1]
        ind_min_dist = dist.argmin()
        if dist.min() <= 1e-8:
            min_dist_list.append(ind)
        ser = lon_lat.loc[ind_min_dist].serialno
        ser_list.append(ser)
        counter += 1
    
    df["serialno"] = ser_list
    return df

def last_processing(df):

    '''
    输出作为聚类算法输入值的最后一步，需运行完前面的特征构建后最后使用
    有些特征需要取负数或其他变换以保证 smaller is better 规则
    '''
    
    selected_features = ["WARN_TAPE","JJSIZE","WEIGHTED_MATL","WEIGHTED_DIAMETER",
                       "date_build_age","date_build_season","PRESS_O_WEIGHT","PRESS_D_WEIGHT",
                       "CONTRACTOR_WEIGHT", "SUPERVISOR_WEIGHT","LENGTH"]
                        
    df = df[selected_features]
    
    df = df.reset_index()
    
    # WARN_TAPE smaller is better
    ts = df["WARN_TAPE"].copy()
    df["WARN_TAPE"].loc[ts == 1] = 0
    df["WARN_TAPE"].loc[ts == 0] = 1
    df["WARN_TAPE"].loc[ts > 1] = 0 # cope with outliers
    
    # WEIGHTED_MATl smaller better
    df["WEIGHTED_MATL"] = -1 * df["WEIGHTED_MATL"]
    
    # CONTRACTOR_WEIGHT smaller better
    df["CONTRACTOR_WEIGHT"] = -1 * df["CONTRACTOR_WEIGHT"]
    
    # SUPERVISOR_WEIGHT smaller better
    df["SUPERVISOR_WEIGHT"] = -1 * df["SUPERVISOR_WEIGHT"]
    
    # construct hypothesis thickness
    press0 = df["PRESS_D_WEIGHT"].copy()
    press0 = (press0 - press0.min())/(press0.max()-press0.min())
    diameter0 = df["WEIGHTED_DIAMETER"].copy()
    diameter0 = (diameter0 -diameter0.min())/(diameter0.max()-diameter0.min())
    hthickness = (press0 * diameter0)/(1 + press0)
    hthickness = -1 * hthickness # smaller is better
    hthickness = (hthickness - hthickness.min())/(hthickness.max()-hthickness.min())
    df["hthickness"] = hthickness
    
    
    "JJSIZE"
    df["JJSIZE"] = (df["JJSIZE"] - df["JJSIZE"].mean())/(df["JJSIZE"])
    
    "date_build_season"
    ts = df["date_build_season"].copy()
    season = pd.Series(np.zeros_like(ts))
    season.loc[ts=="spring"] = 1
    season.loc[ts=="summer"] = 3
    season.loc[ts=="fall"] = 2
    season.loc[ts=="winter"] = 0
    df["date_build_season"] = (season -1/2)/4 # (i-1/2)/N , N为类别总数
    
    "LENGTH"
    df["LENGTH"] = np.log(df["LENGTH"])
    df["LENGTH"] = (df["LENGTH"] - df["LENGTH"].min())/(df["LENGTH"].max()-df["LENGTH"].min())
    
    "do 0,1 scaling on features except WARN_TAPE,JJSIZE,date_build_season,LENGTH"
    dataset = df.copy()
    
    for col in dataset:
        if col not in ["WARN_TAPE","JJSIZE","date_build_season","LENGTH","index","G3E_FID"]:
            # 0,1 MinMaxScaling
            dataset[col] = (dataset[col] - dataset[col].min())/(dataset[col].max()-dataset[col].min())
    
    dataset = dataset.sort_values(by="index").drop(["index"],axis=1)
    
    "存储用于聚类算法输入的表格"
    dataset.to_csv("gasline_clustering.csv",index=False,encoding="utf_8_sig")
    
    
if __name__ == "__main__":

    preprocessing()
    df = pd.read_csv("gasline_attr.csv")
    df = diameter(df)
    df = material(df)
    df = warn_tape(df)
    df = coord_to_lon_lat(df)
    df = pressure(df)
    df = date(df)
    df = contractor(df)
    df = supervisor(df)
    df.to_csv("gasline_attr.csv",index=False,encoding="utf_8_sig") 

    last_processing(df) # save gasline_clustering.csv
    
    
    
    
    
    
    
    
    
            
            