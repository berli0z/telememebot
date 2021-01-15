import json
import threading

import pandas as pd
from flask import Flask
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, Api
from werkzeug.security import generate_password_hash, check_password_hash

from config import DOC_URL, WAIT_SECONDS, user, pwd


def update():
    df = pd.read_csv(DOC_URL)
    df = df.groupby('category').tail(40)
    df.to_csv("output.csv", index=False)
    print("data updated!")
    threading.Timer(WAIT_SECONDS, update).start()


app = Flask(__name__)
auth = HTTPBasicAuth()
users = {
    user: generate_password_hash(pwd)
}


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


api = Api(app)


class Memes(Resource):
    @auth.login_required
    def get(self):
        data = pd.read_csv('output.csv')  # read CSV
        data.index.name = 'index'
        data = data.groupby('category').tail(40)
        data = data.to_json(orient='index')  # convert dataframe to dictionary
        dat = json.loads(data)
        return {'data': dat}, 200  # return data and 200 OK code


api.add_resource(Memes, '/memes')  # '/users' is our entry point

if __name__ == '__main__':
    update()
    app.run(host='0.0.0.0')  # run our Flask app
