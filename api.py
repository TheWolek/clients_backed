from flask import Flask, request, Response
from flask_cors import CORS
import json

from DB_query import DB_query
from user import user_BP

api = Flask(__name__)
CORS(api)

api.register_blueprint(user_BP, url_prefix='/user')


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
