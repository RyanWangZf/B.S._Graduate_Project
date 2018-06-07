# -*- coding: utf-8 -*-
'''

Get heat map of distribution of failure reports.

'''

from matplotlib.colors import LogNorm
import re
import pdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

def get_lng(x):
    
    lng = re.findall("\d+.\d+",x)[0]
    return lng
    
def get_lat(x):
    
    lat = re.findall("\d+.\d+",x)[1]
    return lat
    
    
if __name__ == "__main__":
    
    df = pd.read_csv("failure_report.csv")
    lng_ = df["经纬度"].apply(lambda x : get_lng(x))
    lat_ = df["经纬度"].apply(lambda x : get_lat(x))
    
    x = lng_.astype(np.float64).values
    y = lat_.astype(np.float64).values
    
    '''
    longitude range: 120.65961082469951 120.86540172553127
    latitude range: 31.24660722778891 31.42576791825509
    # 事故分布散点图
    plt.scatter(x,y)
    plt.xlim(120.65961082469951,120.86540172553127)
    plt.ylim(31.24660722778891,31.42576791825509)
    plt.show()
    '''
    
    xy = np.vstack([x,y])
    x1,y1 = np.linspace(x.min(),x.max(),300),np.linspace(y.min(),y.max(),300)
    xyn = np.array([[x1[i],y1[j]] for i in range(300) for j in range(300)])
    xy1 = np.zeros([xyn.shape[1],xyn.shape[0]])
    xy1[0] = xyn[:,0]
    xy1[1] = xyn[:,1]
    kern = gaussian_kde(xy)
    z0 = kern(xy)
    z1 = kern(xy1)
    
    z1[z1<=0.0] = z0.min()
    # pdb.set_trace()
    
    plt.scatter(xy1[0],xy1[1],c=z1,cmap="hot")
      
    #plt.scatter(x,y,c=z,s=100,edgecolor='')# cmap="hot"
    
    plt.colorbar()
    plt.xlim(120.65961082469951,120.86540172553127)
    plt.ylim(31.24660722778891,31.42576791825509)
    plt.show()
    
    # 画三维曲面图
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure()
    ax = Axes3D(fig)
    X1,Y1  = np.meshgrid(x1,y1)
    Z1 = np.meshgrid(z1)[0].reshape(len(x1),len(y1))
    ax.plot_surface(X1,Y1,Z1,cmap="rainbow")
    plt.savefig("surface_of_failure",dpi=300)
    plt.show()
    pdb.set_trace()
    
    
    
    
    
    
    