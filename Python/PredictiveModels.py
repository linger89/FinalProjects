
from pymongo import MongoClient
import pandas as pd
import numpy as np
from sklearn.cluster import SpectralClustering


client=MongoClient()
db=client['scorecard']
coll=db['full']


data_for_clustering_2013=coll.find({'Year':2013},{'INSTNM':1,'CONTROL':1,'CCBASIC':1,'CCUGPROF':1,'CCSIZSET':1,'RELAFFIL':1, 'DISTANCEONLY':1,'TUITFTE':1,'INEXPFTE':1,'AVGFACSAL':1,'ADM_RATE_ALL':1,'SATVRMID':1,'SATMTMID':1,'SATWRMID':1, 'TUITIONFEE_IN': 1, 'TUITIONFEE_OUT': 1, 'TUITIONFEE_PROG': 1, 'UGDS': 1, 'UGDS_WHITE' : 1, 'UGDS_BLACK' : 1, 'UGDS_HISP' :1, 'UGDS_ASIAN': 1, 'UGDS_AIAN':1, 'UGDS_NHPI':1,  'UGDS_2MOR':1, 'UGDS_NRA':1, 'PPTUG_EF': 1, 'INC_PCT_LO' : 1,'INC_PCT_M1' : 1, 'INC_PCT_M2' : 1, 'INC_PCT_H1' : 1, 'INC_PCT_H2' : 1, 'RET_FT4' : 1, 'RET_PT4' : 1, 'RET_FTL4' : 1, 'RET_PTL4' : 1,  'UG25abv' : 1, 'PAR_ED_PCT_1STGEN' : 1, 'PCTFLOAN' : 1, 'DEBT_MDN' : 1, 'LO_INC_DEBT_MDN' : 1,   'MD_INC_DEBT_MDN' : 1,  'HI_INC_DEBT_MDN' : 1, 'DEP_DEBT_MDN' : 1, 'IND_DEBT_MDN' : 1, 'FEMALE_DEBT_MDN' : 1 , 'MALE_DEBT_MDN' : 1 , 'FIRSTGEN_DEBT_MDN' : 1, 'NOTFIRSTGEN_DEBT_MDN' :1, 'C150_4_POOLE' : 1, 'CDR3' : 1, 'COMPL_RPY_3YR_RT': 1, 'NONCOM_RPY_3YR_RT' : 1, 'LO_INC_RPY_3YR_RT': 1,  'MD_INC_RPY_3YR_RT' : 1,  'HI_INC_RPY_3YR_RT': 1, 'DEP_RPY_3YR_RT' : 1, 'IND_RPY_3YR_RT' : 1, 'FEMALE_RPY_3YR_RT': 1,  'MALE_RPY_3YR_RT' : 1, 'FIRSTGEN_RPY_3YR_RT' : 1,  'NOTFIRSTGEN_RPY_3YR_RT' : 1,'_id':0})


data_for_clustering_2013_df=pd.DataFrame(list(data_for_clustering_2013))


data_for_clustering_2013_df=data_for_clustering_2013_df.applymap(lambda x:np.nan if x in ["","PrivacySuppressed"] else x)

data_for_clustering_2013_df.set_index(keys='INSTNM',inplace=True)


def dist_gower_new(df):
    sample_length,feature_length=df.shape
    df = df.apply(lambda x:(x - min(x))/(max(x)-min(x)) if x.dtype == dtype('float64') else x, axis = 0)
    d_matrix=np.zeros([sample_length,sample_length])
    delta_matrix=np.zeros([sample_length,sample_length])
    agg1=np.zeros([sample_length,sample_length])
    agg2=np.zeros([sample_length,sample_length])
    for k,col in enumerate(df.columns):
        temp_data=np.tile(df[col],(sample_length,1))
        if df[col].dtype == np.float64:  
            d_matrix=np.absolute(temp_data-temp_data.T)
        else:
            d_matrix=np.equal(temp_data,temp_data.T)
        delta_matrix=1-np.isnan(d_matrix)
        agg1+=np.nan_to_num(d_matrix)*delta_matrix
        agg2+=delta_matrix
    return agg1/agg2


dist_matrix=dist_gower_new(data_for_clustering_2013_df)


clus=SpectralClustering(n_clusters=100, affinity='precomputed')
labels=clus.fit_predict(dist_matrix)

data_for_clustering_2013_df['cluster']=labels


cluster_colleges=data_for_clustering_2013_df.groupby('cluster').apply(lambda x:x.index.values)


cluster_colleges.to_json('cluster_colleges.json')

data_for_clustering_2013_df['cluster'].to_csv("college_clusters.csv",encoding='utf-8')


for institute in data_for_clustering_2013_df.index:
    coll.update_many({'INSTNM':institute}, {"$set": {"clusterlabel":str(data_for_clustering_2013_df.loc[institute]['cluster'])}})


coll.close()




