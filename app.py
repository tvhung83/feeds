#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
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

@get('/category/<code>')
@get('/category/<code>/<page:int>')
def category(code = 'phim-le', page = 1):
    categories = code.split(',')
    results = db.items.find({'categories': { "$all": categories } }, \
                { 'title': 1, 'thumbnail': 1 } ) \
                .sort('publishedAt',  pymongo.DESCENDING) \
                .skip((page-1)*page_size if page > 1 else 0) \
                .limit(page_size)
    count = db.items.find({'categories': { "$all": categories } }).count()
    total = ((count - 1) // page_size) + 1
    response.content_type = 'application/json'
    return JSONEncoder().encode({ 'content': list(results), 'total': total })

@get('/search/<keyword>')
@get('/search/<keyword>/<page:int>')
def search(keyword, page = 1):
    words = re.split(" +", keyword)
    results = db.items.find({'tags': { "$in": words }}, \
                { 'title': 1, 'thumbnail': 1 } ) \
                .sort('publishedAt',  pymongo.DESCENDING) \
                .skip((page-1)*page_size if page > 1 else 0) \
                .limit(page_size)
    count = db.items.find({'tags': { "$in": words }}).count()
    total = ((count - 1) // page_size) + 1
    response.content_type = 'application/json'
    return JSONEncoder().encode({ 'content': list(results), 'total': total })

@get('/id/<id>')
def item(id):
    item = db.items.find_one({'_id': ObjectId(id) }, { 'title': 1, 'thumbnail': 1, 'links': 1, '_id': 0 } )
    response.content_type = 'application/json'
    return JSONEncoder().encode(item)

@route('/favicon.ico')
def favicon():
    return static_file('favicon.ico', root='./')

@get('/health')
def health():
    return "ok"

MONGO_URL = os.environ.get('MONGOHQ_URL', \
    'mongodb://heroku:nw9jO-6c1dWBHT9OH3z6k3ZDBuFmO9dpuY4BfI0L8ZEjs8DEnm8K0taSizRAt5G1s8Kb5FjxwxsqiOSStIII1A@dogen.mongohq.com:10092/app32117576')
client = MongoClient(MONGO_URL)
# Specify the database
db = client.get_default_database()
bottle.run(host='0.0.0.0', port=argv[1], debug=False, reloader=False)