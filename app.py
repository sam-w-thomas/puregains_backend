from datetime import datetime
from urllib import request

import flask.json
from flask import Flask
import os
from flask import request
from flask import Response
import re
import user
from flask import Flask, request, jsonify
from flask import json
from wtforms import Form, BooleanField, StringField, PasswordField, validators

import verify
from verify import verify_str, verify_birth_date, verify_str_none
from varname import nameof
from json import dumps as json_dict

import util

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def request_connection():
    return "Flask Server & Android are Working Successfully"


@app.route('/api/user', methods=['POST'])
def user_create():
    json_request = request.json
    name = json_request["name"]
    birth = json_request["birth_date"]
    avatar_path = json_request["avatar_path"]
    password = json_request["password"]
    user_tags = json_request["user_tags"]

    # Input checking
    if not verify_str(name) or not verify_birth_date(birth) or not verify_str(avatar_path) or not verify_str(
            password):
        return Response("Invalid parameters", status=401, mimetype='application/json')

    if user_tags is None:
        user_tags = ""
        return Response("Invalid tags", status=401, mimetype='application/json')

    try:
        user_id = user.create_user(
            name,
            datetime.strptime(birth, "%Y/%M/%d").date(),
            avatar_path,
            password,
            user_tags
        )

        response_json = flask.json.dumps({"username": user_id})
        return Response(response_json, status=201, mimetype='application/json')
    except:
        response_json = flask.json.dumps({"username": "INVALID"})
        return Response(response_json, status=401, mimetype='application/json')


@app.route('/api/user/<username>', methods=['PUT'])
def user_update(username):
    assert username == request.view_args['username']

    try:
        json_request = request.json

        # Handle optional paramters and return dict
        return_dict = dict()
        try:
            name = json_request["name"]
            return_dict["name"] = name
        except KeyError:
            name = None

        try:
            avatar_path = json_request["avatar_path"]
            return_dict["avatar_path"] = avatar_path
        except KeyError:
            avatar_path = None

        try:
            reward_points = json_request["reward_points"]
            return_dict["reward_points"] = reward_points
        except KeyError:
            reward_points = None

        try:
            tags = json_request["tags"]
            return_dict["tags"] = tags
        except KeyError:
            tags = None

        user.update_user(
            username,
            name,
            avatar_path,
            reward_points,
            tags
        )

        response_json = json_dict(return_dict, indent=4)
        return Response(response_json, status=201, mimetype='application/json')
    except Exception as e:
        raise Exception
        print("Unable to update user")

        return Response(response_json, status=401, mimetype='application/json')


@app.route('/api/user/<username>', methods=['GET'])
def get_user(username):
    assert username == request.view_args['username']

    if not verify.verify_str(username):
        return Response("Invalid parameters", status=401, mimetype='application/json')

    response_json = json_dict(
        user.user_info(username),
        indent=4,
        default=str
    )
    return Response(response_json, status=201, mimetype='application/json')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
