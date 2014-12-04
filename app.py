#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import bottle
import pymongo
from pymongo import MongoClient
from bottle import response, route, get, run
from json import dumps
from sys import argv

@get('/<code>')
@get('/<code>/<page:int>')
def index(code = 'phim-le', page = 1):
    MONGO_URL = os.environ.get('MONGOHQ_URL', \
        'mongodb://heroku:nw9jO-6c1dWBHT9OH3z6k3ZDBuFmO9dpuY4BfI0L8ZEjs8DEnm8K0taSizRAt5G1s8Kb5FjxwxsqiOSStIII1A@dogen.mongohq.com:10092/app32117576')
    client = MongoClient(MONGO_URL)
    # Specify the database
    db = client.get_default_database()
    results = db.items.find({'categories': code }, \
                { 'title': 1, 'thumbnail': 1, 'links': 1, '_id': 0 } ) \
                .sort('publishedAt',  pymongo.DESCENDING) \
                .skip((page-1)*20 if page > 1 else 0) \
                .limit(20)
    response.content_type = 'application/json'
    return dumps(list(results))

@get('/health')
def health():
    return "ok"
    
bottle.run(host='0.0.0.0', port=argv[1], debug=False, reloader=False)