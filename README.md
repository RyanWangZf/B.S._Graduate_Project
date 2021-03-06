# Savety Evaluation of Gas Pipeline based on Unstructured Multi-source Data  

## ABSTRACT:  
In the circumstance of the lack of domestic urban gas pipeline accident report database, this paper constructed a gas pipeline accident data system which consists of three main components including web crawler of accident reports, statistical analysis on failure inductions and results graphical display. It fills the void and is a constructive attempt.  
Before applying clustering algorithms on pipeline datasets from the GIS, this paper conducts data cleaning and diverse feature engineering, and then compared the performance of K-means, Hierarchical Clustering, DBSCAN and Spectral Clustering on these datasets, selected Hierarchical Clustering as the best. The clustering result passed Chi-square test, being proved to be able to distinguish risk states of gas pipelines. This clustering model brings new insights in risk evaluation of gas pipelines.  
This paper also built two-layered clustering model on time series, which were collected by the SCADA, and through which chose 10 typical series from more than 16,000 series in 2015. On the basis of series matching with the failure reports, 2 risky series were found and an anomaly detection model was created. At last, this paper tested this model on series in 2016 by which proved being capable of digging out 86% of risky series, or in other words, it gets 100% in precision and 86.3% in recall. That result certifies the validity, flexibility and implementation simplicity of the anomaly detection model based on risky series matching.  
## Keywords:  
gas pipeline, risk evaluation, web crawler, unsupervised clustering, anomaly detection   

# Files Description:  
## BaiduMap:  
show geographical distribution of gas pipelines, failure reports and monitors based on API of BaiduMap.  
## GasPipelineClustering:  
do data cleaning, feature engineering before clustering. Compare several clustering algorithms on preprocessed datasets, then 
do graphical presentation.  
## TimeSeriesClustering:  
do 2-layered clustering on 2015 pressure series from monitors, acquiring 10 typical series. then match series at failure occurrence 
nearest monitor with 10 typical series, making sure 2 of 10 as the risky series. at last, verify the risky series on 2016 normal series 
and failure series.    

=======
Please read Paper.pdf for details.  


