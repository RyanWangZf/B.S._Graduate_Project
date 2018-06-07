## oracle_loader.py  
用于从oracle database中提取原数据，存储为csv文件  
extract data from Oracle database, saving as *.csv  

## match_RTDMD_CLIENT.py  
用于匹配RTDMD测点与CLIENTINFO的测点位置  
matach RTDMD's location with CLIENTINFO  

## heatmap.py  
用于画出事故的地点分布，用
gaussian kernel density estimation 拟合事故分布概率密度，
画出分布热图  
use Kernel Density Estimation to fit the geographical probability distribution,
then paint the hear map  

## get_dtw_D.py  
对每个测点的365天内日线做DTW距离的交叉矩阵，
作为第一层谱聚类的邻接矩阵(affinity matrix)  
get cross DTW distance matrix as the pre-computed affinity matrix  

## spec_cluster.py  
根据得到的第一层的每个测点dtw距离矩阵D，
对每个测点的序列做聚类并得到每个测点的8条典型序列  
do spectral clustering based on D matrix from get_dtw_D.py,
then get 8 typical time-series from every detection monitor's data.  

## last_dtw_cluster.py  
由第一层聚类得到的典型序列计算交叉距离矩阵D，
随后对D作谱聚类，最终得到所有测点的所有序列的
10条典型走势  
get 10 typical time series from 8*number of detection monitor's typical time series
 by spectral clustering, too.  

## report_ser_match.py  
匹配事故发生地最近的测点序列号  
match the nearest monitor of every failure report  

## ts_report_stats.py  
匹配10条典型序列与事故发生地测点序列，展示不同序列的风险度差异  
match 2015 failure reports with every 10 typical time series, show the stats results.  

## 2016_report_ts.py  
匹配2016年的事故序列与10条模版线，验证高风险模版线在2016年是否继续为高风险  
match 2016 failure reports with every 10 typical time series, show stats results to 
vertify whether or not the risky series in 2015 keep risky in 2016.  

## sampling_ts.py  
从2016年序列中随机抽取300余条序列，验证非事故走势是否符合高风险模版线  
sampling over 300 series randomly and match with 10 typical time series, verifying if normal 
series match the risky series.  

