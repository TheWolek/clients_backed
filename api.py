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


def DB_query(query: str, values=None):  # master function for DB interaction
    try:
        cnx = mysql.connector.connect(
            user='root', password='132', host='localhost', database='clients')
        cur = cnx.cursor(dictionary=True)

        if query[:6] == "SELECT":
            cur.execute(query)
            cnx.close()
            return cur.fetchall()

        if query[:6] == "DELETE":
            cur.execute(query, values)
            cnx.commit()
            cnx.close()
            return {"status": cur.rowcount}

        if query[:6] == "INSERT":
            cur.execute(query, values)
            cnx.commit()
            cnx.close()
            return {"status": cur.rowcount, "ID": cur.lastrowid}

    except mysql.connector.Error as err:
        print(err)


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
    sql = "SELECT login FROM creds WHERE login = '" + newUser["login"] + "'"
    res = DB_query(sql)
    if res != []:  # if so throw error
        return Response("{'err_msg':'account with that login already exists. Please log in'}", status=406, mimetype='application/json')

    # instert user data to DB
    sql = "INSERT INTO creds (login, pass) VALUES (%s, %s)"
    val = (newUser["login"], newUser["password"])
    res = DB_query(sql, val)

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
    res = DB_query("SELECT login FROM creds WHERE login = '" +
                   req["login"] + "'")
    if res == []:  # if no throw error
        return Response("{'err_msg': 'wrong login or password'}", status=401, mimetype='application/json')

    # body data parsing
    EnteredHash = hashlib.md5(req["password"].encode())
    # check if password matches
    fetchedHash = DB_query(
        "SELECT pass FROM creds WHERE login = '" + req["login"] + "'")

    # wrong password
    if not EnteredHash.hexdigest() == fetchedHash[0]["pass"]:
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
    sql = "SELECT id, imie_Nazwisko FROM clients WHERE imie_Nazwisko like '%" + \
        client_name + "%'"
    res = DB_query(sql)

    return Response(json.dumps({"data": res}), status=200, mimetype='application/json')

# delete client


@ api.route("/client/<CID>", methods=["DELETE"])
def deleteClient(CID: int):
    # check if user exists
    sql = "SELECT id FROM clients WHERE ID=" + CID
    res = DB_query(sql)

    if res == []:
        return Response("{'err_msg':'no client was found'}", status=404, mimetype='application/json')

    sql = "DELETE FROM clients WHERE id=%s"
    res = DB_query(sql, (CID,))

    if res["status"] != 1:
        return Response("{'err_msg':'DB error'}", status=500, mimetype='application/json')

    return Response(json.dumps({"CID": CID}), status=200, mimetype='application/json')


if __name__ == "__main__":
    api.run()
