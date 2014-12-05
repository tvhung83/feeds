#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import urllib2
import bottle
import pymongo
import json
from bson.objectid import ObjectId
from pymongo import MongoClient
from bottle import response, route, get, run
from sys import argv

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

page_size = 20
direct_prefix = 'http://fshare.herokuapp.com'

@get('/category/<code>')
@get('/category/<code>/<page:int>')
def index(code = 'phim-le', page = 1):
    results = db.items.find({'categories': code }, \
                { 'title': 1, 'thumbnail': 1 } ) \
                .sort('publishedAt',  pymongo.DESCENDING) \
                .skip((page-1)*page_size if page > 1 else 0) \
                .limit(page_size)
    total = int(db.items.find({'categories': code }).count() / page_size)
    response.content_type = 'application/json'
    return JSONEncoder().encode({ 'content': list(results), 'total': total })

@get('/id/<id>')
def index(id):
    item = db.items.find_one({'_id': ObjectId(id) }, { 'thumbnail': 1, 'links': 1, '_id': 0 } )
    if item and item['links']:
        for link in item['links']:
            file_id = re.search('\/file\/(\w+)', link['link']).group(0)
            req = urllib2.Request(direct_prefix + file_id)
            res = urllib2.urlopen(req)
            link['link'] = res.geturl()
    response.content_type = 'application/json'
    return JSONEncoder().encode(item)

@get('/health')
def health():
    return "ok"

MONGO_URL = os.environ.get('MONGOHQ_URL', \
    'mongodb://heroku:nw9jO-6c1dWBHT9OH3z6k3ZDBuFmO9dpuY4BfI0L8ZEjs8DEnm8K0taSizRAt5G1s8Kb5FjxwxsqiOSStIII1A@dogen.mongohq.com:10092/app32117576')
client = MongoClient(MONGO_URL)
# Specify the database
db = client.get_default_database()
bottle.run(host='0.0.0.0', port=argv[1], debug=False, reloader=False)