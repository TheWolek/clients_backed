from flask import Flask, request, Response
from flask_cors import CORS
import json

from DB_query import DB_query
from user import user_BP
from client import client_BP
from proc import proc_BP

api = Flask(__name__)
CORS(api)

api.register_blueprint(user_BP, url_prefix='/user')
api.register_blueprint(client_BP, url_prefix='/client')
api.register_blueprint(proc_BP, url_prefix='/proc')


if __name__ == "__main__":
    api.run()
