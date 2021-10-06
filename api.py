from os import stat
from flask import Flask, request, Response
from flask.scaffold import _endpoint_from_view_func
from flask_cors import CORS
import hashlib
import json

from DB_query import DB_query

api = Flask(__name__)
CORS(api)


@api.route("/register", methods=["POST"])  # registering new user
def userRegister():
    req = request.json

    # body validation
    if "login" not in req or "password" not in req:
        return Response("{'err_msg':'bad request'}", status=400, mimetype='application/json')

    if req["login"] == "" or req["password"] == "":
        return Response("{'err_msg':'login or password missing'}", status=406, mimetype='application/json')

    # body data parsing
    hash = hashlib.md5(req["password"].encode())
    newUser = {
        "login": req["login"],
        "password": hash.hexdigest()
    }

    # check if login already exists
    sql = "SELECT login FROM creds WHERE login = %s"
    val = (newUser["login"],)
    res = DB_query(sql, val)

    if res["status"] != 1:  # if returned status is wrong
        return Response("{'err_msg':'DB error'}", status=500, mimetype='application/json')

    if res["data"] != []:  # if login exists throw error
        return Response("{'err_msg':'account with that login already exists. Please log in'}", status=406, mimetype='application/json')

    # instert user data to DB
    sql = "INSERT INTO creds (login, pass) VALUES (%s, %s)"
    val = (newUser["login"], newUser["password"])
    res = DB_query(sql, val)

    if res["status"] != 1:  # if returned status is wrong
        return Response("{'err_msg':'DB error'}", status=500, mimetype='application/json')

    # OK, user created
    return Response(status=201, mimetype='application/json')


@ api.route("/login", methods=["POST"])  # user log in
def userLogin():
    req = request.json

    # body validation
    if "login" not in req or "password" not in req:
        return Response("{'err_msg':'bad request'}", status=400, mimetype='application/json')

    if req["login"] == "" or req["password"] == "":
        return Response("{'err_msg':'login or password is missing'}", status=406, mimetype='application/json')

    # check if login exists in DB
    sql = "SELECT login FROM creds WHERE login = %s"
    val = (req["login"],)
    res = DB_query(sql, val)

    if res["status"] != 1:  # if returned status is wrong
        return Response("{'err_msg':'DB error'}", status=500, mimetype='application/json')

    if res["data"] == []:  # if no throw error
        return Response("{'err_msg': 'wrong login or password'}", status=401, mimetype='application/json')

    # body data parsing
    EnteredHash = hashlib.md5(req["password"].encode())
    # check if password matches
    sql = "SELECT pass FROM creds WHERE login = %s"
    val = (req["login"],)
    fetchedHash = DB_query(sql, val)

    if fetchedHash["status"] != 1:  # if returned status is wrong
        return Response("{'err_msg':'DB error'}", status=500, mimetype='application/json')

    # wrong password
    if not EnteredHash.hexdigest() == fetchedHash["data"][0]["pass"]:
        return Response("{'err_msg': 'wrong login or password'}", status=401, mimetype='application/json')

    # OK, user is loged in
    return Response(json.dumps({"login": req["login"]}), status=200, mimetype='application/json')


@ api.route("/client", methods=["POST"])  # create new client
def clientAdd():
    req = request.json

    # body validation
    if "imie_Nazwisko" not in req:
        return Response("{'err_msg':'imie_Nazwisko field is missing'}", status=406, mimetype='application/json')

    # body data parsing
    name = req["imie_Nazwisko"].lower()

    # DB query
    sql = "INSERT INTO clients (imie_Nazwisko) VALUES (%s)"
    val = (name,)
    res = DB_query(sql, val)

    # something went wrong with database and no record was insterted, throw error
    if res["status"] != 1:
        return Response(status=500, mimetype='application/json')

    # OK, client created
    return Response(json.dumps({"CID": res["ID"]}), status=200, mimetype='application/json')


# fetch client data by name
@ api.route("/client/<client_name>", methods=["GET"])
def findClient(client_name):
    client_name = "%"+client_name+"%"
    sql = "SELECT id, imie_Nazwisko FROM clients WHERE imie_Nazwisko like %s"
    val = (client_name, )
    res = DB_query(sql, val)

    if res["status"] != 1:  # if returned status is wrong
        return Response("{'err_msg':'DB error'}", status=500, mimetype='application/json')

    return Response(json.dumps({"data": res["data"]}), status=200, mimetype='application/json')

# delete client


@ api.route("/client/<CID>", methods=["DELETE"])
def deleteClient(CID: int):
    # check if user exists
    sql = "SELECT id FROM clients WHERE ID=%s"
    val = (CID,)
    res = DB_query(sql, val)

    if res["status"] != 1:  # if returned status is wrong
        return Response("{'err_msg':'DB error'}", status=500, mimetype='application/json')

    if res["data"] == []:
        return Response("{'err_msg':'no client was found'}", status=404, mimetype='application/json')

    sql = "DELETE FROM clients WHERE id=%s"
    res = DB_query(sql, (CID,))

    if res["status"] != 1:
        return Response("{'err_msg':'DB error'}", status=500, mimetype='application/json')

    return Response(json.dumps({"CID": CID}), status=200, mimetype='application/json')


@ api.route("/proc", methods=["POST"])
def createProc():
    req = request.json

    if "CID" not in req or "desc" not in req:
        return Response("{'err_msg':'CID and description are required'}", status=406, mimetype='application/json')

    if req["desc"] == "":
        return Response("{'err_msg':'description can not be empty'}", status=406, mimetype='application/json')

    sql = "SELECT id FROM clients WHERE id = %s"
    val = (str(req["CID"]),)
    res = DB_query(sql, val)

    if res["status"] != 1:  # if returned status is wrong
        return Response("{'err_msg':'DB error'}", status=500, mimetype='application/json')

    if res["data"] == []:
        return Response("{'err_msg':'no client found'}", status=406, mimetype='application/json')

    sql = "INSERT INTO proc (CID, description) VALUES (%s, %s)"
    val = (str(req["CID"]), req["desc"])
    res = DB_query(sql, val)

    if res["status"] != 1:
        return Response("{'err_msg':'DB error'}", status=500, mimetype='application/json')

    return Response(json.dumps({"ID": res["ID"]}), status=200, mimetype='application/json')


@ api.route("/proc/<CID>", methods=["GET"])
def findClientProc(CID):

    return Response(status=200, mimetype='application/json')


if __name__ == "__main__":
    api.run()
