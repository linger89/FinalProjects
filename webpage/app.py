from flask import Flask, render_template, session, redirect, url_for, flash
from flask import request
from flask import make_response
from flask.ext.bootstrap import Bootstrap
from datetime import datetime
from flask.ext.wtf import Form
from wtforms import Form, TextField, validators, SubmitField
from pymongo import MongoClient
import json
from bson import json_util
from bson.json_util import dumps
import csv
import json
import io

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'scorecard'
COLLECTION_NAME = 'visualcounty'
FIELDS = {'Gid': True, 'Year': True,'controltype':True, 'county':True, 'state': True, 'count': True, '_id': False}
NAMEDICT = {'Admission Rate':'avgadrate','Faculty Salary':'avgfs', "Number of Students": 'avgnumstud','Percentage of Students Receiving Federal Loans': 'avgpctloan', "Median Cumulative Debt": 'avgcumdebt', "Mean Earning after 6 Years": 'avgmeanearn', "Federal Loan Payment Rate": "avgfracrpy"}

class SimpleForm(Form):
    username = TextField('School Name', [validators.Length(min=4, max=100)])

app=Flask(__name__)
bootstrap=Bootstrap(app)
app.secret_key = 'random bytes'

@app.route('/')
def index():
	return render_template('index.html')


@app.route('/countylevelexploration/<string:name>')
def county(name):
	connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
	collection = connection[DBS_NAME][COLLECTION_NAME]
	FIELDS_local=FIELDS.copy()
	name.replace('%%20'," ")
	name_in_db=NAMEDICT[name]
	FIELDS_local.update({name_in_db:True})
	projects = collection.find({}, FIELDS_local)
	json_projects = []
	for project in projects:
		if project['Gid']!="NotFound" and project['count'] and project['controltype'] and project[name_in_db] and int(project['count'])>0 and float(project[name_in_db])>0:
			json_projects.append(project)
	json_projects = json.dumps(json_projects, default=json_util.default)
	connection.close()
	return render_template('countylevelexploration.html',statisticname=name,json_file=json_projects,dbname=name_in_db)

@app.route('/basicsummary/<string:name>')
def basic(name):
	name.replace('%%20'," ")
	return render_template('basicsummary.html',statisticname=name)

@app.route('/schoollevelexploration/<string:name>',methods=['GET','POST'])
def similarschools(name):
    form = SimpleForm(request.form)
    error=None
    if request.method == 'POST' and form.validate():
        reader = csv.reader(open('static/data/college_clusters.csv', 'r'))
        college_to_cluster = {row[0]:row[1] for row in reader}
        cluster_num=college_to_cluster.get(form.username.data,'NotFound')
        if cluster_num is 'NotFound':
            error = 'Invalid College Name!'
        else:
            name.replace('%%20'," ")
            if  name == 'Find Similar Schools':
                cluster_colleges = json.load(io.open('static/data/cluster_colleges.json',encoding='latin-1'))
            return render_template('similarschools_show.html',data=cluster_colleges[cluster_num],name=name)
    return render_template('similarschools.html',form=form,error=error)



if __name__=='__main__':
	app.run(debug=True)
