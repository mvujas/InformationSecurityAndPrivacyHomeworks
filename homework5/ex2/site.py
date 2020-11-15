#!/usr/bin/env python3
import sys
import populate
from flask import Flask
from flask import request, jsonify
import pymysql
from operator import itemgetter


app = Flask(__name__)
username = "root"
password = "root"
database = "hw5_ex2"

# This method returns a list of messages in a json format such as
# [
# { "name": <name>, "message": <message> },
# { "name": <name>, "message": <message> },
# ...
# ]
# If this is a POST request and there is a parameter "name" given, then only
# messages of the given name should be returned.
# If the POST parameter is invalid, then the response code must be 500.


@app.route("/messages", methods=["GET", "POST"])
def messages():
    def row_to_dictionary(row):
        return {
            'name': row[0],
            'message': row[1]
        }
    with db.cursor() as cursor:
        if request.method == 'GET':
            cursor.execute('SELECT name, message FROM messages')
        else:
            name = request.form.get('name')
            if name:
                cursor.execute('SELECT name,message FROM messages WHERE name=%s', name)
            else:
                return 'invalid post request', 500
        try:
            json = list(map(row_to_dictionary, cursor.fetchall()))
        except:
            json = None
        return jsonify(json), 200


# This method returns the list of users in a json format such as
# { "users": [ <user1>, <user2>, ... ] }
# This methods should limit the number of users if a GET URL parameter is given
# named limit. For example, /users?limit=4 should only return the first four
# users.
# If the paramer given is invalid, then the response code must be 500.
@app.route("/users", methods=["GET"])
def contact():
    def create_response(rows):
        return {
            'users': list(map(itemgetter(0), rows))
        }
    with db.cursor() as cursor:
        limit = request.args.get('limit')
        if limit:
            try:
                cursor.execute('SELECT name FROM users LIMIT %s', int(limit))
            except:
                return 'invalid limit parameter', 500
        else:
            cursor.execute('SELECT name FROM users')
        json = create_response(cursor.fetchall())
        #json = None
        return jsonify(json), 200


if __name__ == "__main__":
    db = pymysql.connect("localhost",
                         username,
                         password,
                         database)
    with db.cursor() as cursor:
        populate.populate_db(cursor)
        db.commit()
    print("[+] database populated")

    app.run(host='0.0.0.0', port=80)
