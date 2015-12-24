from pymongo import MongoClient
import pandas as pd
import numpy as np


client=MongoClient()
db=client['scorecard']
coll=db['full']


def flatten_dict(nestdict):
    final_dict={}
    for key,value in nestdict.iteritems():
        if type(value) is not dict:
            final_dict[key]=value
        else:
            sub_dict=flatten_dict(value)
            final_dict.update(sub_dict)
    return final_dict

def convert_nested_keys(cursors):
    for cursor in cursors:
        yield flatten_dict(cursor)



def sd_zip_code(zc):
    zc=str(zc)
    if len(zc)>=5:
        return zc[0:5]
    else:
        return zc.zfill(5)

import json
a=open('zip_to_county_state_geoid.json','r')
zc_to_countyid_dict=json.load(a)
a.close()


sum1_year_zc=coll.aggregate([{"$group":{"_id":{"Year":"$Year","ZipCode":"$ZIP","controltype":"$CONTROL"},"count":{"$sum":1},                                "avgadrate":{"$avg":"$ADM_RATE"},"avgntrps":{"$avg":"$TUITFTE"},                                "avgfs":{"$avg":"$AVGFACSAL"},"avgtin":{"$avg":"$TUITIONFEE_IN"},                                "avgtout":{"$avg":"$TUITIONFEE_OUT"},"avgtprog":{"$avg":"$TUITIONFEE_PROG"},                                "avgnumstud":{"$avg":"$UGDS"},"avgnppub":{"$avg":"$NPT4_PUB"},"avgnppriv":{"$avg":"$NPT4_PRIV"},                                "avgnpprog":{"$avg":"$NPT4_PROG"},"avgnpother":{"$avg":"$NPT4_OTHER"},                                "avgfracwhite":{"$avg":"$UGDS_WHITE"},"avgfracblack":{"$avg":"$UGDS_BLACK"},                                "avgfrachisp":{"$avg":"$UGDS_HISP"},"avgfracasian":{"$avg":"$UGDS_ASIAN"},                                "avgfracaian":{"$avg":"$UGDS_AIAN"},"avgfracnhpi":{"$avg":"$UGDS_NHPI"},                                "avgfrac2mor":{"$avg":"$UGDS_2MOR"},"avgfracnra":{"$avg":"$UGDS_NRA"},                                "avgperlow":{"$avg":"$INC_PCT_LO"},"avgperm1":{"$avg":"$INC_PCT_M1R"},                                "avgperm2":{"$avg":"$INC_PCT_M"},"avgperh1":{"$avg":"$INC_PCT_H1"},                                "avgperh2":{"$avg":"$INC_PCT_H"}       
                                      }}])
sum1_year_zc=pd.DataFrame(list(convert_nested_keys(sum1_year_zc))) 
sum1_year_zc["county"],sum1_year_zc["state"],sum1_year_zc["Gid"]=zip(*(sum1_year_zc['ZipCode'].map(sd_zip_code).map(zc_to_countyid_dict)))



sum2_year_zc=coll.aggregate([{"$group":{"_id":{"Year":"$Year","ZipCode":"$ZIP","controltype":"$CONTROL"},"avgpctloan":{"$avg":"$PCTFLOAN"},                                "avgcumdebt":{"$avg":"$DEBT_MDN"},"avggraddebt":{"$avg":"$GRAD_DEBT_MDN"},                                "avgwdrawdebt":{"$avg":"$WDRAW_DEBT_MDN"},"avgcompwhite":{"$avg":"$C150_4_WHITE"},                                "avgcompblack":{"$avg":"$C150_4_BLACK"},"avgcomphisp":{"$avg":"$C150_4_HISP"},                                "avgcompasian":{"$avg":"$C150_4_ASIAN"},"avgcompaian":{"$avg":"$C150_4_AIAN"},                                "avgcompnhpi":{"$avg":"$C150_4_NHPI"},"avgcomp2mor":{"$avg":"$C150_4_2MOR"},                                "avgcompnra":{"$avg":"$C150_4_NRA"},"avgmeanearn":{"$avg":"$mn_earn_wne_p6"},                                "avgmeanearni1":{"$avg":"$mn_earn_wne_inc1_p6"},"avgmeanearni2":{"$avg":"$mn_earn_wne_inc2_p6"},                                "avgmeanearni3":{"$avg":"$mn_earn_wne_inc3_p6"},"avgfracrpy":{"$avg":"$RPY_7YR_RT"}       
                                      }}])
sum2_year_zc=pd.DataFrame(list(convert_nested_keys(sum2_year_zc))) 
sum2_year_zc["county"],sum2_year_zc["state"],sum2_year_zc["Gid"]=zip(*(sum2_year_zc['ZipCode'].map(sd_zip_code).map(zc_to_countyid_dict)))


sum1_year_zc.merge(sum2_year_zc, on=['county','state','Gid','Year','ZipCode','controltype']).to_csv('summary_by_county.csv',index=False,encoding='utf-8')


coll.close()

