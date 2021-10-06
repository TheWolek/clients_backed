from flask import Flask, request, Response
from flask.blueprints import Blueprint
import json

from DB_query import DB_query

client_BP = Blueprint("client", __name__)


@ client_BP.route("/", methods=["POST"])  # create new client
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
@ client_BP.route("/<client_name>", methods=["GET"])
def findClient(client_name):
    client_name = "%"+client_name+"%"
    sql = "SELECT id, imie_Nazwisko FROM clients WHERE imie_Nazwisko like %s"
    val = (client_name, )
    res = DB_query(sql, val)

    if res["status"] != 1:  # if returned status is wrong
        return Response("{'err_msg':'DB error'}", status=500, mimetype='application/json')

    return Response(json.dumps({"data": res["data"]}), status=200, mimetype='application/json')


@ client_BP.route("/<CID>", methods=["DELETE"])  # delete client
def deleteClient(CID: int):
    sql = "DELETE FROM clients WHERE id=%s"
    res = DB_query(sql, (CID,))

    if res["status"] != 1:  # nothing was deleted
        return Response("{'err_msg':'client with provided ID was not found'}", status=406, mimetype='application/json')

    return Response(json.dumps({"CID": CID}), status=200, mimetype='application/json')


@ client_BP.route("/", methods=["PUT"])  # edit client
def updateClient():
    req = request.json
    imie_Nazwisko = req["imie_Nazwisko"].lower()

    sql = """UPDATE clients SET imie_Nazwisko = %s WHERE id = %s"""
    val = (imie_Nazwisko, req["id"])
    res = DB_query(sql, val)

    if res["status"] == 0:  # if nothing was updated
        return Response("{'err_msg':'client with provided ID was not found or value has not changed'}", status=406, mimetype='application/json')

    return Response(json.dumps({"CID": req["id"], "imie_Nazwisko": req["imie_Nazwisko"]}), status=200, mimetype='application/json')
