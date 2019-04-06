from pymongo import MongoClient
# http://api.mongodb.com/python/current/tutorial.html
from pprint import pprint

def connect_database(database):
    print(database)
    client = MongoClient(database['uri'])
    try:
        if database['name'] in client.list_database_names():
            db = client[database['name']]
            return db
        else:
            print('Database not exixts, create database: ' + database['name'])
            db = client[database['name']]
            return db
    except Exception as e:
        print("Error:" + str(e))
        return 400


def get_server_status(db):
    return db.command("serverStatus") 


def insert(db, collection, data):
    if db != 400:
        try:
            mycol = db[collection]
            print("insert db")
            mycol.insert_one(data)
        except Exception as e:
            print(e)
            return 400   

def isExists(db, collection, data):
    mycol = db[collection]
    return mycol.find({data['column_name']: { "$in": data['key']}}).count() > 0
    