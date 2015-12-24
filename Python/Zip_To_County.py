from pymongo import MongoClient
import pandas as pd
import numpy as np
import json
import io
import geonameszip
from collections import defaultdict


client=MongoClient()
db=client['scorecard']
coll=db['full']

counties = json.load(io.open('us-counties-20m.json',encoding='latin-1'))
counties=counties['features']
counties=[ele['properties'] for ele in counties]
counties=pd.DataFrame(counties)[['NAME','STATE','GEO_ID']]

states = json.load(io.open('us-states.json',encoding='latin-1'))
states=states['features']
states=[{'id':ele['id'],'statename':ele['properties']['name']} for ele in states]
states=pd.DataFrame(states)

counties_final=counties.merge(states, how='outer',left_on='STATE',right_on='id')[['NAME','statename','GEO_ID']]



counties_final=counties_final.set_index(keys=['NAME','statename']).to_dict()['GEO_ID']



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


num_zc=coll.aggregate([{"$group":{"_id":{"ZipCode":"$ZIP"},"count":{"$sum":1}}}])
num_zc=pd.DataFrame(list(convert_nested_keys(num_zc)))


# Notice that some zipcodes are short than 5 digits, in which case they need to be zero padded. Some zipcodes are longer than 5 digits, then we only use the first 5 digits

def sd_zip_code(zc):
    zc=str(zc)
    if len(zc)>=5:
        return zc[0:5]
    else:
        return zc.zfill(5)



def return_county_and_state(zc):
    lu=geonameszip.lookup_postal_code(str(zc),'US')
    if lu is None:
        return (None,None)
    return (lu['county'].split('(')[0].strip(),lu['state'])






zc_to_countyid_dict=defaultdict(str)
for zc in num_zc['ZipCode'].map(sd_zip_code).drop_duplicates():
    zc_to_countyid_dict[zc]=return_county_and_state(zc)+(counties_final.get(return_county_and_state(zc),'NotFound'),)



a=open('zip_to_county_state_geoid.json','rw+')
json.dump(zc_to_countyid_dict,a)
a.close()





