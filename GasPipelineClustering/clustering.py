# -*- coding: utf-8 -*-

'''
method:
import clustering as cl

cl.pca_plot() # show 2D scatters, decomposed by PCA

cl.lle_plot() # show 2D scatters, decomposed by LocallyLinearEmbedding

cl.minik_means() # do mini-k-means clustering, then show 2D scatters of clustering results.

cl.spectral_clustering() # do spectral_clustering, then show 2D scatters of clustering results.

cl.hierarchical_clustering() # do AgglomerativeClustering, then show 2D scatters of clustering results.

cl.DBSCAN() # do DBSCAN clustering, then show 2D scatters of clustering results.

cl.describe() # do Agglomerative Clustering and show their location scatters
'''


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pdb



np.random.seed(84) # set random seed

# params of matplotlib
plt.rc("font",family="SimHei",size=10)
plt.rcParams['axes.unicode_minus'] = False #解决保存图像是负号'-'显示为方块的问题

n_clusters = 6
sca_dict = {"color":["blue","red","green","brown","yellow","cyan"],"marker":["o","v","s","+","*","h"]}

def fit_predict(estimator_,df,x,name):
    '''
    Input: df:raw data, x:PCA decomposed data, name: pic's name
    '''
    from sklearn.metrics import calinski_harabaz_score
    pic_path = ".\\DataEDA\\"  
    y = estimator_.fit_predict(df)
    
    # pdb.set_trace()
    
    for i in range(n_clusters):
        plt.scatter(x[:,0][y==i],x[:,1][y==i],c=sca_dict["color"][i],marker=sca_dict["marker"][i],alpha=0.75)
    
    ch_index = calinski_harabaz_score(df,y)
    plt.xlabel("第一主向量")
    plt.ylabel("第二主向量")
    plt.title("管道属性样本散点图(PCA降维)")
    plt.savefig(pic_path+"pca_scatter_"+name,dpi=300)
    plt.show()
    print("calinski_harabaz_score:",ch_index)

    

def pca_plot():
    "用PCA降维观察散点图"
    from sklearn.decomposition import PCA
    from mpl_toolkits.mplot3d import Axes3D
    pic_path = ".\\DataEDA\\"   
    df = pd.read_csv("gasline_clustering.csv")

    pca = PCA(n_components=3)
    # (n_components=None, copy=True, whiten=False, svd_solver='auto', tol=0.0, iterated_power='auto', random_state=None)
    
    x = pca.fit_transform(df)
    plt.rc("font",family="SimHei",size=10)
    plt.rcParams['axes.unicode_minus'] = False #解决保存图像是负号'-'显示为方块的问题
    
    print("pca variance ratio",pca.explained_variance_ratio_)
    
    ax = plt.subplot(221,projection = '3d')
    # plt.scatter(x[:,1],x[:,0])
    
    ax.scatter(x[:4000,0],x[:4000,1],x[:4000,2],alpha=0.8,c="blue",marker=".")
    ax.scatter(x[4000:8000,0],x[4000:8000,1],x[4000:8000,2],alpha=0.8,c="red",marker=".")
    ax.scatter(x[8000:,0],x[8000:,1],x[8000:,2],alpha=0.6,c="green",marker=".")
    ax.set_xlabel('x') 
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.set_title("散点分布-三维")
    
    ax = plt.subplot(222)
    ax.scatter(x[:,0],x[:,1],alpha=0.8,c="crimson",marker=".")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("散点分布-俯视图")
    
    ax = plt.subplot(223)
    ax.scatter(x[:,1],x[:,2],alpha=0.8,c="chocolate",marker=".")
    ax.set_xlabel("y")
    ax.set_ylabel("z")
    ax.set_title("散点分布-正视图")   

    ax = plt.subplot(224)
    ax.scatter(x[:,0],x[:,2],alpha=0.8,c="darkcyan",marker=".")
    ax.set_xlabel("x")
    ax.set_ylabel("z")
    ax.set_title("散点分布-侧视图")


    plt.savefig(pic_path+"pca_scatter_ori_3d",dpi=300)
    plt.show()
    
def lle_plot():
    "流形学习二维化观察散点图（未分类）"
    from sklearn.manifold import LocallyLinearEmbedding
    
    pic_path = ".\\DataEDA\\"
    df = pd.read_csv("gasline_clustering.csv")
    
    lle = LocallyLinearEmbedding(n_neighbors=5, n_components=2,eigen_solver="dense")
    
    x = lle.fit_transform(df)
    
    plt.rc("font",family="SimHei",size=10)
    plt.rcParams['axes.unicode_minus'] = False #解决保存图像是负号'-'显示为方块的问题
    
    plt.scatter(x[:,0],x[:,1])
    plt.xlabel("第二主向量")
    plt.ylabel("第一主向量")
    plt.title("管道属性样本散点图(LLE降维)")
    plt.savefig(pic_path+"pca_scatter_LLE_ori",dpi=300)
    plt.show()
    
def minik_means():
    pic_path = ".\\DataEDA\\"
    
    from sklearn.cluster import MiniBatchKMeans
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    from sklearn.metrics import calinski_harabaz_score
    
    pca = PCA(n_components=2)
    km = KMeans(n_clusters=n_clusters,init="k-means++",max_iter=100,random_state=84)
    df = pd.read_csv("gasline_clustering.csv")
    km.fit(df)
    y = km.predict(df)
    
    x = pca.fit_transform(df)
   
    
    for i in range(n_clusters):      
        plt.scatter(x[:,0][y==i],x[:,1][y==i],c=sca_dict["color"][i],marker=sca_dict["marker"][i],alpha=0.75)
    
    
    ch_index = calinski_harabaz_score(df,y)
    
    plt.xlabel("第一主向量")
    plt.ylabel("第二主向量")
    plt.title("管道属性样本散点图(PCA降维)")
    plt.savefig(pic_path+"pca_scatter_minikmeans",dpi=300)
    plt.show()
    
    print("calinski_harabaz_score:",ch_index)
    
def spectral_clustering():
    
    from sklearn.decomposition import PCA
    from sklearn.cluster import SpectralClustering
    df = pd.read_csv("gasline_clustering.csv")
    pca = PCA(n_components=2)
    x = pca.fit_transform(df)
    
    spc = SpectralClustering(n_clusters=n_clusters,gamma=0.5,affinity='rbf',n_neighbors=10,assign_labels='kmeans')
    # spc = SpectralClustering(n_clusters=n_clusters,gamma=1.0,affinity='nearest_neighbors',n_neighbors=4,assign_labels='kmeans')
    
    fit_predict(spc,df,x,"spc_trial")

def hierarchical_clustering():
    from sklearn.decomposition import PCA
    from sklearn.cluster import AgglomerativeClustering
    
    df = pd.read_csv("gasline_clustering.csv")
    pca = PCA(n_components=2)
    x = pca.fit_transform(df)
    
    
    agg = AgglomerativeClustering(n_clusters=n_clusters,affinity="euclidean",linkage="ward")
    # affinity option： “euclidean”, “l1”, “l2”, “manhattan”, “cosine”, 
    # linkage : {“ward”, “complete”, “average”}, 
    fit_predict(agg,df,x,"hierarchical")
    
def DBSCAN():
    from sklearn.cluster import DBSCAN
    from sklearn.decomposition import PCA
    from sklearn.metrics import calinski_harabaz_score
    
    df = pd.read_csv("gasline_clustering.csv")
    pca = PCA(n_components=2)
    x = pca.fit_transform(df)
    
    
    dbs = DBSCAN(eps=0.9, min_samples=100, metric='euclidean',algorithm='auto')
    
    
    pic_path = ".\\DataEDA\\"  

    
    # "尝试PCA降维后再接DBSCAN"
    # pca_1 = PCA(n_components = 4) # top 4 explained variance ratio sum : 94 %
    # pca_df = pca_1.fit_transform(df)
    # y = dbs.fit_predict(pca_df)
    
    y = dbs.fit_predict(df)
    
    label_list = pd.Series(dbs.labels_).unique().tolist()
    
    for i in label_list:
        if i == -1: # noise
            plt.scatter(x[:,0][y==-1],x[:,1][y==-1],c="black",marker="*",alpha=0.75)
        else:
            plt.scatter(x[:,0][y==i],x[:,1][y==i],c=sca_dict["color"][i],marker=sca_dict["marker"][i],alpha=0.75)
    
    ch_index = calinski_harabaz_score(df,y)
    plt.xlabel("第一主向量")
    plt.ylabel("第二主向量")
    plt.title("管道属性样本散点图(PCA降维)")
    plt.savefig(pic_path+"pca_scatter_"+"dbscan",dpi=300)
    plt.show()
    print("calinski_harabaz_score:",ch_index)
    
def describe():
    from sklearn.cluster import AgglomerativeClustering
    
    agg = AgglomerativeClustering(n_clusters=6,affinity="euclidean",linkage="ward")
    df = pd.read_csv("gasline_clustering.csv")
    y = agg.fit_predict(df)
    
    # describe
    ft_list = ["LENGTH","JJSIZE","date_build_age"]
    
    df = pd.read_csv("gasline_attr.csv")
    
    icg = pd.read_csv("ICG_CLIENTINFO.csv")
    icg = icg.dropna(how="all") # col GPSLAT & GPSLON
    
    lon_list = df.LON[df.LON>100]
    lat_list = df.LAT[df.LON>100]
    print("longitude range:",lon_list.min(),lon_list.max())
    print("latitude range:",lat_list.min(),lat_list.max())
    
    for i in range(6):
        lon = df.loc[np.where(y==i)].LON.values
        lat = df.loc[np.where(y==i)].LAT.values
        lon_ = lon[lon>100]
        lat_ = lat[lon>100]
        plt.scatter(lon_,lat_,label=str(i+1),norm=0.5,marker=",")
    
    
    plt.legend()
    plt.show()
        
        

    



















    
    
    






    
    
    
    
    