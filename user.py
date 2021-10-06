from flask import Flask, request, Response
from flask.blueprints import Blueprint
import hashlib
import json

from DB_query import DB_query

user_BP = Blueprint("user", __name__)


@user_BP.route("/register", methods=["POST"])  # user register
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


@ user_BP.route("/login", methods=["POST"])  # user log in
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
