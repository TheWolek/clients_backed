from flask import Flask, request, Response
from flask.blueprints import Blueprint
import json

from DB_query import DB_query

proc_BP = Blueprint("proc", __name__)


@ proc_BP.route("/", methods=["POST"])
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


@ proc_BP.route("/<CID>", methods=["GET"])
def findClientProc(CID):

    return Response(status=200, mimetype='application/json')