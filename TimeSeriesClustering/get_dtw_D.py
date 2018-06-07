# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
import time
import pdb
import re
import gc

from itertools import combinations
from multiprocessing import Process,Pool
from multiprocessing import Manager

def dtw(ts1,ts2):
    # ts1 : m , ts2 : n
    # get raw cross distance matrix D(n,m), d[i,j] = (ts1[i]-ts2[j])**2
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
        
def get_D(df,dist_matrix_name,dist_path,dist_file):
    if dist_matrix_name in dist_file:
        print(dist_matrix_name," existed, skip it. --", time.asctime(time.localtime(time.time())))
    else:
        print(dist_matrix_name," processing...wait. --",time.asctime(time.localtime(time.time())))
        d_dict = dict()
        date_list = df.index.normalize().unique().strftime("%Y%m%d") # get dates
        for ind in combinations(np.arange(len(date_list)).tolist(),r=2):
            i,j = ind[0],ind[1]
            try:
                "需要考虑日线完全平的，没有动的情况"
                tsi = df.loc[date_list[i]].PRESSURE.copy()
                if tsi.std()==0:
                    tsi = pd.Series(np.zeros(len(tsi)))
                else:
                    tsi = (tsi - tsi.mean())/tsi.std()
                
                tsj = df.loc[date_list[j]].PRESSURE.copy()
                if tsj.std() == 0:
                    tsj = pd.Series(np.zeros(len(tsj)))
                else:
                    tsj = (tsj - tsj.mean())/tsj.std()
                
                d_dict["(%s,%s)"%(i,j)] = dtw(tsi,tsj)
                # print("processing %s's "%(dist_matrix_name),ind)
            except:
                raise Exception("error in sub-process")
        
        D = np.zeros([len(date_list),len(date_list)])
        for k,v in d_dict.items(): #遍历d_dict获取D的坐标和对应的值
            coord = re.findall("(\d+,\d+)",k)[0]
            i = int(re.findall("\d+,",coord)[0][:-1])
            j = int(re.findall(",\d+",coord)[0][1:])
            D[i,j] = v
        
        D = np.array(D)
        D = D.T + D # 由上三角矩阵转为对称矩阵
        df_D = pd.DataFrame(D)
            
        df_D.to_csv(dist_path+"\\"+dist_matrix_name,index=False,encoding="utf_8_sig") 
        print(dist_matrix_name," processed. --", time.asctime(time.localtime(time.time())))

        
    
if __name__ == "__main__":

    
    origin_path = ".\\RTDMD_processed"
    origin_list = os.listdir(origin_path)
    
    dist_path = ".\\DistMatrix"
    dist_file = os.listdir(dist_path)
    file_counter = 0
    num_file = len(origin_list)
    file_list_ = []
    
    n_process = 4
    
    for file in origin_list:
        file_counter += 1
        file_list_.append(file)
        if np.mod(file_counter,n_process) == 0 and file_counter > 0:
            p = Pool(n_process)
            num = 0
            for num in range(n_process):
                file = file_list_[num]
                df = pd.read_csv(origin_path+"\\"+file,parse_dates=[0],index_col=[0],engine="python")
                df = df.resample("H").last().fillna(method="ffill") # resample the df with freq = 60 minutes
                dist_matrix_name =  str(int(df.SERIALNO[0])) + "_D.csv" 
                p.apply_async(get_D,args=(df,dist_matrix_name,dist_path,dist_file))
           
            p.close()
            p.join()
            print(file_list_," processed.(%s of %s)"%(file_counter,num_file))
            # pdb.set_trace()
            file_list_ = [] 
            del df;gc.collect()
        
        elif file_counter >= num_file: # 处理最后剩余的不到4个文件
            n_process_last = np.mod(file_counter,n_process)
            p = Pool(n_process_last)
            num = 0
            for num in range(n_process_last):
                file = file_list_[num]
                df = pd.read_csv(origin_path+"\\"+file,parse_dates=[0],index_col=[0],engine="python")
                df = df.resample("H").last().fillna(method="ffill") # resample the df with freq = 60 minutes
                dist_matrix_name =  str(int(df.SERIALNO[0])) + "_D.csv" 
                p.apply_async(get_D,args=(df,dist_matrix_name,dist_path,dist_file))
            
            
            p.close()
            p.join()
            print(file_list_," processed.(%s of %s)"%(file_counter,num_file))
            # pdb.set_trace()
            file_list_ = [] 
            del df;gc.collect()
            break
'''      
if __name__ == "__main__":
 
    from itertools import combinations
    from multiprocessing import Process,Pool
    from multiprocessing import Manager
    origin_path = "C:\\Users\\Administrator\\Desktop\\毕业论文\\汇报-第十一周\\RTDMD_processed"
    origin_list = os.listdir(origin_path)
    
    dist_path = "C:\\Users\\Administrator\\Desktop\\毕业论文\\汇报-第十一周\\DistMatrix"
    dist_file = os.listdir(dist_path)
    file_counter = 0
    num_file = len(origin_list)
    for file in origin_list:
        df = pd.read_csv(origin_path+"\\"+file,parse_dates=[0],index_col=[0],engine="python")
        df = df.resample("H").last().fillna(method="ffill") # resample the df with freq = 30 minutes
        date_list = df.index.normalize().unique().strftime("%Y%m%d") # get dates
        
        dist_matrix_name =  str(df.SERIALNO[0]) + "_D.csv"
        if dist_matrix_name in dist_file:
            print(dist_matrix_name,"existed, skip it.")
            file_counter+=1
            continue
        n_process = 4
        ind_list = []
        counter = 0
        "实现多进程之间的数据共享"   
        M = Manager()
        d_dict = M.dict() 
        # 只能对dict进行dict[key]=value这种形式的赋值才能共享，
        # 如果是对dict[key][i,j]=value这种形式的赋值无法在子进程和父进程之间共享

        # C{365,2} = 365*364/2 = 66430    
        for ind in combinations(np.arange(len(date_list)).tolist(),r=2):
             
            if np.mod(counter,n_process) == 0 and counter > 0:
                p = Pool(n_process)
                for num in range(n_process):
                    i,j = ind_list[num][0],ind_list[num][1]
                    p.apply_async(proc_,args=(d_dict,i,j,df,date_list))
                p.close()
                p.join()
                print("%s of %s(%s,%s)complete."%(counter,file,file_counter,num_file),ind_list)
                ind_list = []
                
            ind_list.append(ind)    
            counter += 1
            
        D = np.zeros([len(date_list),len(date_list)])
        for k,v in d_dict.items(): #遍历d_dict获取D的坐标和对应的值
            coord = re.findall("(\d+,\d+)",k)[0]
            i = int(re.findall("\d+,",coord)[0][:-1])
            j = int(re.findall(",\d+",coord)[0][1:])
            D[i,j] = v
        
        # pdb.set_trace()
        D = np.array(D)
        D = D.T + D # 由上三角矩阵转为对称矩阵
        
        # D = pd.DataFrame(D)
        # D = D.fillna(1.0).values # fill nan
        
        # D进行转换使其适合 Affinity 矩阵的条件： np.exp(- dist_matrix ** 2 / (2. * delta ** 2)) , Gassusian kernel 
        # D = np.exp(-D**2/(2.0*1**2))
        # D[np.eye(365,365)==1] = 1.0 # 对角线赋值 1.0
        
        df_D = pd.DataFrame(D)
        
        df_D.to_csv(dist_path+"\\"+dist_matrix_name,index=False,encoding="utf_8_sig")
        
        print(file," processed. --", time.asctime(time.localtime(time.time())))
        file_counter += 1
        del df,df_D,D;gc.collect()
''' 
        

    
    





