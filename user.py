from flask import Flask, request, Response
from flask.blueprints import Blueprint
import hashlib
import json
import random
import string

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


def userCreateToken(UID):

    token = ''.join(random.SystemRandom().choice(
        string.ascii_uppercase + string.digits) for _ in range(128))
    sql = "INSERT INTO user_tokens (user_id, token) VALUES (%s,%s)"
    res = DB_query(sql, (UID, token))

    if res["status"] != 1:  # if returned status is wrong
        return Response("{'err_msg':'DB error'}", status=500, mimetype='application/json')

    return {"UID": UID, "token": token}


def checkUserToken(UID):
    sql = "SELECT user_id FROM user_tokens WHERE user_id = %s"
    res = DB_query(sql, (UID,))

    if res["status"] != 1:  # if returned status is wrong
        return Response("{'err_msg':'DB error'}", status=500, mimetype='application/json')

    if res["data"] != []:
        return True

    return False


def TokenValidation(enteredToken):
    sql = "SELECT user_id, token FROM user_tokens WHERE token = %s"
    res = DB_query(sql, (enteredToken,))

    if res["status"] != 1:  # if returned status is wrong
        return Response("{'err_msg':'DB error'}", status=500, mimetype='application/json')

    if res["data"] == []:
        return {"status": False}

    if res["data"][0]["token"] != enteredToken:
        return {"status": False}

    return {"status": True, "UID": res["data"][0]["user_id"]}


@ user_BP.route("/login", methods=["POST"])  # user log in
def userLogIn():
    req = request.json

    # body validation
    if "login" not in req or "password" not in req:
        return Response("{'err_msg':'bad request'}", status=400, mimetype='application/json')

    if req["login"] == "" or req["password"] == "":
        return Response("{'err_msg':'login or password is missing'}", status=406, mimetype='application/json')

    # check if login exists in DB
    sql = "SELECT id, login FROM creds WHERE login = %s"
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
    if checkUserToken(res["data"][0]["id"]):
        return Response("{'err_msg': 'token error'}", status=401, mimetype='application/json')

    token = userCreateToken(res["data"][0]["id"])

    return Response(json.dumps({"login": req["login"], "token": token}), status=200, mimetype='application/json')


@ user_BP.route("/logout", methods=["POST"])  # user log out
def userLogOut():
    req = request.json

    if "token" not in req:
        return Response("{'err_msg':'bad request'}", status=400, mimetype='application/json')

    if req["token"] == "":
        return Response("{'err_msg': 'token is required'}", status=400, mimetype='application/json')

    tokenValid = TokenValidation(req["token"])

    if not tokenValid["status"]:
        return Response("{'err_msg': 'wrong token'}", status=401, mimetype='application/json')

    UID = tokenValid["UID"]
    sql = "DELETE FROM user_tokens WHERE user_id=%s"
    res = DB_query(sql, (UID,))

    if res["status"] != 1:  # if returned status is wrong
        return Response("{'err_msg':'DB error'}", status=500, mimetype='application/json')

    return Response(json.dumps({"UID": UID}), status=200, mimetype='application/json')
