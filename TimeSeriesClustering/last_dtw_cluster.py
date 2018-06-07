import pandas as pd
import numpy as np
import pdb
import os
from itertools import combinations
import re
import matplotlib.pyplot as plt
from sklearn.cluster import SpectralClustering

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
    
 
if __name__ == "__main__":

    # set global variables
    n_clusters = 10
    
    typical_path = "C:\\Users\\Administrator\\Desktop\\毕业论文\\汇报-第十一周\\Typical_TS"

    typical_files = os.listdir(typical_path)

    lines_ = pd.DataFrame()

    print("loading daily lines from typical_files...")
    for file in typical_files:
        
        df = pd.read_csv(typical_path+"\\"+file,engine="python")
        
        cols = df.columns.tolist()
        col_pref = re.findall("\d+",file)[0]
        cols = [col_pref+"_"+col for col in cols]
        
        df.columns = cols
        
        lines_ = pd.concat([lines_,df],axis=1)
    
    this_files = os.listdir()
    lines_list = lines_.columns
    if "D_of_2nd_cluster.csv" not in this_files:
        d_dict = dict()    
        for ind in combinations(np.arange(len(lines_list)),r=2):    
            
            i,j = ind[0],ind[1]
            col_i,col_j = lines_list[i],lines_list[j]
            print("now processing %s & %s..."%(col_i,col_j))
            try:
                "需要考虑日线完全平的，没有动的情况，或者日线值过小，明显异常的情况"
                tsi = lines_[col_i]
                if tsi.std()==0:
                    tsi = np.zeros(len(tsi))
                else:
                    tsi = (tsi - tsi.mean())/tsi.std()
                
                tsj = lines_[col_j]
                if tsj.std() == 0:
                    tsj = np.zeros(len(tsj))
                else:
                    tsj = (tsj - tsj.mean())/tsj.std()
                
                d_dict["(%s,%s)"%(i,j)] = dtw(tsi,tsj)
                # print("processing %s's "%(dist_matrix_name),ind)
            
            except:
                raise Exception("error in combinations: ",col_i,"---",col_j)

        D = np.zeros([len(lines_list),len(lines_list)])
        for k,v in d_dict.items():
            coord = re.findall("(\d+,\d+)",k)[0]
            i = int(re.findall("\d+,",coord)[0][:-1])
            j = int(re.findall(",\d+",coord)[0][1:])
            D[i,j] = v
        
        df_D = pd.DataFrame(D,index=lines_list,columns=lines_list)
        df_D.to_csv("D_of_2nd_cluster.csv",encoding="utf_8_sig")
        print("Cross Distance Matrix of 2nd clustering has been saved.")
    
    else:
        print("find existed D of cluster, load it.")
        D = pd.read_csv("D_of_2nd_cluster.csv",index_col=[0])
        # pdb.set_trace()
    # start 2nd clustering
    
    
    
    if "typical_ts_of_2nd_clustering.csv" in os.listdir():
    
        print("find existed typical_ts_of_2nd_clustering.csv, load it.")
        typical_df = pd.read_csv("typical_ts_of_2nd_clustering.csv")
        
    else:
    
        sc = SpectralClustering(n_clusters=n_clusters,affinity="precomputed")
        D = D.values
        D = D + D.T
        D = np.exp(-D**2/(2*10**2)) # Gaussian kernel
        
        sc.fit(D)
        y = sc.labels_
        
        print("SpectralClustering completed.")
        
        
        df = lines_
        typical_df = pd.DataFrame()
        # search typical time series
        for cl_num in range(n_clusters):
            print("Now getting typical time series of cluster %s..."%cl_num)
            lines_cl = lines_list[np.where(y==cl_num)]
            
            D_part = D[np.where(y==cl_num)]
            sum_list = [D_part[:,np.where(y==cl_num)][j].sum() for j in range(len(lines_cl))]
            sum_ar = np.array(sum_list)
            ind_ = np.argsort(sum_ar)[0]
            # pdb.set_trace()
            typical_df[lines_cl[ind_]] = df[lines_cl[ind_]].values
            
        typical_df.to_csv("typical_ts_of_2nd_clustering.csv",index=False,encoding="utf_8_sig")    
    
    print("start plot typical timeseries and save.")
    
    fig_path = "C:\\Users\\Administrator\\Desktop\\毕业论文\\汇报-第十一周\\2nd_ts\\"
    cols = typical_df.columns.tolist()
    # pdb.set_trace()
    for i in range(n_clusters):
        ax = plt.figure()
        plt.plot(typical_df[cols[i]])
        plt.title(cols[i])
        ax.savefig(fig_path+cols[i],dpi=300)
        plt.close()
        
    
    print("Task completed, Programme Ends.")
        
        
        
        
    
    
    
    
    
    
    





   
    
    
    
    
    
