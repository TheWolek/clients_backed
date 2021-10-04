from os import stat
from flask import Flask, request, Response
from flask.scaffold import _endpoint_from_view_func
from flask_cors import CORS
import hashlib
import json
import mysql.connector


api = Flask(__name__)
CORS(api)

# utils


def DB_query(query: str, values=None):
    try:
        cnx = mysql.connector.connect(
            user='root', password='132', host='localhost', database='clients')
        cur = cnx.cursor()
        if values == None:
            cur.execute(query)
            cnx.close()
            return cur.fetchall()
        else:
            cur.execute(query, values)
            cnx.commit()
            cnx.close()
            return {"status": cur.rowcount, "ID": cur.lastrowid}

    except mysql.connector.Error as err:
        print(err)


@api.route("/register", methods=["POST"])
def userRegister():
    req = request.json

    if "login" not in req or "password" not in req:
        return Response("{'err_msg':'bad request'}", status=400, mimetype='application/json')

    if req["login"] == "" or req["password"] == "":
        return Response("{'err_msg':'login or password missing'}", status=406, mimetype='application/json')

    hash = hashlib.md5(req["password"].encode())
    newUser = {
        "login": req["login"],
        "password": hash.hexdigest()
    }

    # connect to DB and store user data
    sql = "SELECT login FROM creds WHERE login = '" + newUser["login"] + "'"
    res = DB_query(sql)
    if res != []:
        return Response("{'err_msg':'account with that login already exists. Please log in'}", status=406, mimetype='application/json')

    sql = "INSERT INTO creds (login, pass) VALUES (%s, %s)"
    val = (newUser["login"], newUser["password"])
    res = DB_query(sql, val)

    return Response(status=201, mimetype='application/json')


@ api.route("/login", methods=["POST"])
def userLogin():
    req = request.json

    if "login" not in req or "password" not in req:
        return Response("{'err_msg':'bad request'}", status=400, mimetype='application/json')

    if req["login"] == "" or req["password"] == "":
        return Response("{'err_msg':'login or password is missing'}", status=406, mimetype='application/json')

    res = DB_query("SELECT login FROM creds WHERE login = '" +
                   req["login"] + "'")
    if res == []:
        return Response("{'err_msg': 'wrong login or password'}", status=401, mimetype='application/json')

    EnteredHash = hashlib.md5(req["password"].encode())
    fetchedHash = DB_query(
        "SELECT pass FROM creds WHERE login = '" + req["login"] + "'")

    if not EnteredHash.hexdigest() == fetchedHash[0][0]:
        return Response("{'err_msg': 'wrong login or password'}", status=401, mimetype='application/json')

    return Response(json.dumps({"login": req["login"]}), status=200, mimetype='application/json')


@ api.route("/client", methods=["POST"])
def clientAdd():
    req = request.json

    if "imie_Nazwisko" not in req:
        return Response("{'err_msg':'imie_Nazwisko field is missing'}", status=406, mimetype='application/json')

    name = req["imie_Nazwisko"].lower()

    sql = "INSERT INTO clients (imie_Nazwisko) VALUES (%s)"
    val = (name,)
    res = DB_query(sql, val)

    if res["status"] != 1:
        return Response(status=500, mimetype='application/json')

    return Response(json.dumps({"CID": res["ID"]}), status=200, mimetype='application/json')


if __name__ == "__main__":
    api.run()
