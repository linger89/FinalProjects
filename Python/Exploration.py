from pymongo import MongoClient
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sn
get_ipython().magic(u'pylab inline')


client=MongoClient()
client.database_names()


db=client['scorecard'] # access the database 'scorecard'


db.collection_names()


coll=db['full'] # access the collection 'full'

totalcount=coll.count() # 124699 records


# Here is a list of columns and their meanings:
# 
# |Column Name|Column Content|Type|Detailed Info|
# |:---------:|:------------:|:--:|:-----------:|
# |Id|unique identification number| |
# |Year| | |1996 to 2013|
# |_id|unique id for mongodb| |
# |numbranch|number of branch campuses at that school| |
# |preddeg|the type of degrees that the school primarily awards|int|
# |HIGHDEG|highest award level offered at that school|int||
# |region| | |
# |CITY|city name| | |
# |STABBR|state name abbrieviation|str||
# |main|1 indicates main campus, 0 not| |0 or 1|
# |CURROPER|currently operating or not by FSA| |0 or 1|
# |ZIP|zip code| |
# |INSTNM|institution name| |
# |LATITUDE||||
# |LONGITUDE||||
# |UnitID|IPEDS id: unique for postsecondary institutions|||
# |OPEID|FSA id: institutions eligible for federal financial aid|||
# |CONTROL|institution's governance structure||public, private nonprofit, or private for-profit|

numschool_vs_year = coll.aggregate([{"$group":{"_id":"$Year","count":{"$sum":1}}}])



numschool_vs_year=pd.DataFrame(list(numschool_vs_year))



numschool_vs_year['_id']=numschool_vs_year['_id'].astype(int)


numschool_vs_year.sort(columns='_id', ascending=True, inplace=True)


fig,ax=plt.subplots()
numschool_vs_year.plot(kind='bar',ax=ax ,x='_id',y='count',rot=60)
ax.set_xlabel('Year')
plt.tight_layout()
fig.savefig("Number_of_Institutions_vs_Year.pdf")


# Next let's look at the SAT scores

SAT_2013=coll.find({'Year':2013, 'SATMTMID':{'$not':{'$in':['','PrivacySuppressed']}},'SATWRMID':{'$not':{'$in':['','PrivacySuppressed']}},'SATVRMID':{'$not':{'$in':['','PrivacySuppressed']}}},{'INSTNM':1,'SATMTMID':1,'SATVRMID':1,'SATWRMID':1})


SAT_2013_df=pd.DataFrame(list(SAT_2013))

fig,ax=plt.subplots()
sn.kdeplot(SAT_2013_df['SATMTMID'],shade=True,ax=ax,label='Math')
sn.kdeplot(SAT_2013_df['SATVRMID'],shade=True,ax=ax,label='Verbal')
sn.kdeplot(SAT_2013_df['SATWRMID'],shade=True,ax=ax,label='Writing')
ax.set_xlabel('SAT Score (2013)')
ax.set_yticklabels('')
plt.tight_layout()
fig.savefig("SAT_scores_2013.pdf")

fig,ax=plt.subplots()
SAT_2013_df[['INSTNM','SATMTMID']].sort(columns=['SATMTMID'],ascending=False).head(20).set_index(keys=['INSTNM']).plot(kind='barh',ax=ax,xlim=[700,800],legend=False,title="SAT Math 2013")
for p in ax.patches:
    ax.annotate(str(p.get_width()), (p.get_width() * 0.98, p.get_y() * 1))
plt.tight_layout()
fig.savefig('Top20SATMATH2013.pdf')

fig,ax=plt.subplots()
SAT_2013_df[['INSTNM','SATVRMID']].sort(columns=['SATVRMID'],ascending=False).head(20).set_index(keys=['INSTNM']).plot(kind='barh',ax=ax,xlim=[700,800],legend=False,title='SAT Verbal 2013')
for p in ax.patches:
    ax.annotate(str(p.get_width()), (p.get_width() * 0.98, p.get_y() * 1))
plt.tight_layout()
fig.savefig('Top20SATVERBAL2013.pdf')

fig,ax=plt.subplots()
SAT_2013_df[['INSTNM','SATWRMID']].sort(columns=['SATWRMID'],ascending=False).head(20).set_index(keys=['INSTNM']).plot(kind='barh',ax=ax,xlim=[700,800],legend=False,title='SAT Writing 2013')
for p in ax.patches:
    ax.annotate(str(p.get_width()), (p.get_width() * 0.98, p.get_y() * 1))
plt.tight_layout()
fig.savefig('Top20SATWRITING2013.pdf')

meanearnings_after_10_years=coll.find({'Year':2011, 'mn_earn_wne_p10':{'$not':{'$in':['','PrivacySuppressed']}},'mn_earn_wne_inc1_p10':{'$not':{'$in':['','PrivacySuppressed']}}, 'mn_earn_wne_inc2_p10':{'$not':{'$in':['','PrivacySuppressed']}}, 'mn_earn_wne_inc3_p10':{'$not':{'$in':['','PrivacySuppressed']}}, 'mn_earn_wne_indep0_p10':{'$not':{'$in':['','PrivacySuppressed']}}, 'mn_earn_wne_indep1_p10':{'$not':{'$in':['','PrivacySuppressed']}}, 'mn_earn_wne_male0_p10':{'$not':{'$in':['','PrivacySuppressed']}}, 'mn_earn_wne_male1_p10':{'$not':{'$in':['','PrivacySuppressed']}}},{'INSTNM':1,'CONTROL':1,'mn_earn_wne_p10':1,'mn_earn_wne_inc1_p10':1,'mn_earn_wne_inc2_p10':1,'mn_earn_wne_inc3_p10':1,'mn_earn_wne_indep0_p10':1,'mn_earn_wne_indep1_p10':1,'mn_earn_wne_male0_p10':1,'mn_earn_wne_male1_p10':1})


meanearnings_after_10_years_df=pd.DataFrame(list(meanearnings_after_10_years))

meanearnings_income_brackets=sn.FacetGrid(meanearnings_after_10_years_df, col='CONTROL', sharex=True,size=4,                        aspect=0.9,sharey=True,xlim=[0,200000])
labels=["\$ 0 to \$ 30,000", "\$ 30,001 to \$ 75,000","\$ 75,001 and above "]
def plot_individual_kde(*namelist,**kwargs):
    colors=sn.color_palette("muted",len(namelist))
    for key,name in enumerate(list(namelist)):
        sn.kdeplot(name,shade=True,color=colors[key],label=labels[key])
meanearnings_income_brackets=meanearnings_income_brackets.map(plot_individual_kde,'mn_earn_wne_inc1_p10','mn_earn_wne_inc2_p10','mn_earn_wne_inc3_p10').add_legend(title='Family Income Brakets').set_titles("{col_name}").set(xticks=[0,40000,80000,120000,160000,200000]).set_xlabels('Mean Earnings (\$) after 10 Years').set_ylabels('').set_yticklabels('').set_xticklabels([0,'40k','80k','120k','160k','200k'])
meanearnings_income_brackets.savefig('10_year_mean_earnings_family_income.pdf')

meanearnings_indep=sn.FacetGrid(meanearnings_after_10_years_df, col='CONTROL', sharex=True,size=4,                        aspect=0.9,sharey=True,xlim=[0,200000])
labels=["Dependent","Independet"]
meanearnings_indep=meanearnings_indep.map(plot_individual_kde,'mn_earn_wne_indep0_p10','mn_earn_wne_indep1_p10').add_legend(title='Dependence').set_titles("{col_name}").set(xticks=[0,40000,80000,120000,160000,200000]).set_xlabels('Mean Earnings (\$) after 10 Years').set_ylabels('').set_yticklabels('').set_xticklabels([0,'40k','80k','120k','160k','200k'])
meanearnings_indep.savefig('10_year_mean_earnings_independence.pdf')


meanearnings_gender=sn.FacetGrid(meanearnings_after_10_years_df, col='CONTROL', sharex=True,size=4,                        aspect=0.9,sharey=True,xlim=[0,200000])
labels=["Female","Male"]
meanearnings_gender=meanearnings_gender.map(plot_individual_kde,'mn_earn_wne_male0_p10','mn_earn_wne_male1_p10').add_legend(title='Gender').set_titles("{col_name}").set(xticks=[0,40000,80000,120000,160000,200000]).set_xlabels(    'Mean Earnings (\$) after 10 Years').set_ylabels('').set_yticklabels('').set_xticklabels([0,'40k','80k','120k','160k','200k'])
meanearnings_gender.savefig('10_year_mean_earnings_gender.pdf')



statistics_2013=coll.find({'Year':2013, 'COSTT4_A':{'$ne':''},'enrollment':{'$ne':''},'UGDS_WHITE':{'$ne':''},'UGDS_BLACK':{'$ne':''},'UGDS_HISP':{'$ne':''},'UGDS_ASIAN':{'$ne':''},'UGDS_AIAN':{'$ne':''},'UGDS_NHPI':{'$ne':''}, 'UGDS_2MOR':{'$ne':''},'UGDS_NRA':{'$ne':''},'LO_INC_DEBT_MDN':{'$not':{'$in':['','PrivacySuppressed']}},'MD_INC_DEBT_MDN':{'$not':{'$in':['','PrivacySuppressed']}},                           'HI_INC_DEBT_MDN':{'$not':{'$in':['','PrivacySuppressed']}},'DEP_DEBT_MDN':{'$not':{'$in':['','PrivacySuppressed']}},'IND_DEBT_MDN':{'$not':{'$in':['','PrivacySuppressed']}}, 'FEMALE_DEBT_MDN':{'$not':{'$in':['','PrivacySuppressed']}},'MALE_DEBT_MDN':{'$not':{'$in':['','PrivacySuppressed']}}},{'INSTNM':1,'CONTROL':1,'COSTT4_A':1,'enrollment':1,'UGDS_WHITE':1,'UGDS_BLACK':1,'UGDS_HISP':1,'UGDS_ASIAN':1,'UGDS_AIAN':1,'UGDS_NHPI':1, 'UGDS_2MOR':1, 'UGDS_NRA':1,'LO_INC_DEBT_MDN':1,'MD_INC_DEBT_MDN':1, 'HI_INC_DEBT_MDN':1, 'DEP_DEBT_MDN':1,  'IND_DEBT_MDN':1, 'FEMALE_DEBT_MDN':1, 'MALE_DEBT_MDN':1})


statistics_2013_df=pd.DataFrame(list(statistics_2013))


enrollmentrate_2013_race=sn.FacetGrid(statistics_2013_df, col='CONTROL', sharex=True,size=4,                        aspect=0.9,sharey=True,xlim=[0,1],ylim=[0,30])
labels=["White","Black","Hispanic","Asian","American Indian/Alaska Native",'Native Hawaiian/Pacific Islander',         "Two or More Races","Non-Resident Alien"]
enrollmentrate_2013_race=enrollmentrate_2013_race.map(plot_individual_kde,'UGDS_WHITE','UGDS_BLACK','UGDS_HISP','UGDS_ASIAN','UGDS_AIAN','UGDS_NHPI', 'UGDS_2MOR', 'UGDS_NRA',).add_legend(title='Race').set_titles("{col_name}").set_xlabels('Admission Rate in 2013').set_ylabels('').set_yticklabels('')
enrollmentrate_2013_race.savefig('enrollment_rate_by_race_2013.pdf')

debt_income_brackets=sn.FacetGrid(statistics_2013_df, col='CONTROL', sharex=True,size=4,                        aspect=0.9,sharey=True,xlim=[0,35000])
labels=["\$ 0 to \$ 30,000", "\$ 30,001 to \$ 75,000","\$ 75,001 and above "]
debt_income_brackets=debt_income_brackets.map(plot_individual_kde,'LO_INC_DEBT_MDN','MD_INC_DEBT_MDN','HI_INC_DEBT_MDN').add_legend(title='Family Income Brakets').set_titles("{col_name}").set_xlabels('Cumulative Median Debt (\$) (2013)').set_ylabels('').set_yticklabels('').set(xticks=[0,10000,20000,30000]).set_xticklabels([0,'10k','20k','30k'])
debt_income_brackets.savefig('cumulative_mediam_debt_by_family_income.pdf')


debt_dependence=sn.FacetGrid(statistics_2013_df, col='CONTROL', sharex=True,size=4,                        aspect=0.9,sharey=True,xlim=[0,35000])
labels=["Dependent", "Independent"]
debt_dependence=debt_dependence.map(plot_individual_kde,'DEP_DEBT_MDN','IND_DEBT_MDN').add_legend(title='Dependence').set_titles("{col_name}").set_xlabels('Cumulative Median Debt (\$) (2013)').set_ylabels('').set_yticklabels('').set(xticks=[0,10000,20000,30000]).set_xticklabels([0,'10k','20k','30k'])
debt_dependence.savefig('cumulative_mediam_debt_by_dependence.pdf')



debt_gender=sn.FacetGrid(statistics_2013_df, col='CONTROL', sharex=True,size=4,                        aspect=0.9,sharey=True,xlim=[0,35000])
labels=["Female", "Male"]
debt_gender=debt_gender.map(plot_individual_kde,'FEMALE_DEBT_MDN','MALE_DEBT_MDN').add_legend(title='Gender').set_titles("{col_name}").set_xlabels('Cumulative Median Debt (\$) (2013)').set_ylabels('').set_yticklabels('').set(xticks=[0,10000,20000,30000]).set_xticklabels([0,'10k','20k','30k'])
debt_gender.savefig('cumulative_mediam_debt_by_gender.pdf')




