import os
import sys
import json
from utils import debug
import rekognize
from flask import Flask, render_template, redirect, url_for, request, session
# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy


# EB looks for an 'application' callable by default.
application = Flask(__name__)

# Configurations
application.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(application)
from models import *

@application.route('/')
def index():
    datasets = Dataset.query.all()
    return render_template("index.html", 
                           datasets=datasets)


@application.route('/search')
def search():
    return render_template("search.html")
    
@application.route('/new', )
def new():
    return render_template("form.html")
    
@application.route('/add', methods=['GET', 'POST'])
def process_data():
    try:
        name =  request.form['name']
        description = request.form['description']
        image = request.files['image']
        
        print "getting data from image..."
        try:
            data = rekognize.analyze(image, image.filename)
            if isinstance(data, list):
                # some necessarily evil for csv conversion
                temp_lst = []
                for _ in data:
                    temp_lst.append({"Data": _ })
                data = temp_lst
            data = json.dumps(data)
            print data
                
        except Exception as e:
            data = "No data"
            debug("Failed to analyze image:", e)
        
        dataset = Dataset(name, description, data)
        db.session.add(dataset)
        db.session.commit()
    except Exception as e:
        print debug("Failed to add image:", e)
        pass
    return redirect(url_for('index'))

# run the app.
if __name__ == "__main__":
    # Build the database:
    # This will create the database file using SQLAlchemy
    db.create_all()
    
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run(host='0.0.0.0', port=5005)
