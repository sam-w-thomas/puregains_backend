from datetime import datetime
from urllib import request

import flask.json
from flask import Flask
import os
from flask import request
from flask import Response
import re

import post
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


@app.route('/api/user/<username>', methods=['DELETE'])
def delete_user(username):
    """
    Delete a user
    :param username:
    :return:
    """
    assert username == request.view_args['username']

    try:
        user.delete_user(username)
        response_json = json_dict({"username": username}, indent=4)
        return Response(response_json, status=201, mimetype='application/json')
    except:
        print("Unable to delete user")
        response_json = json_dict({"status": "INVALID"}, indent=4)
        return Response(response_json, status=401, mimetype='application/json')


@app.route('/api/user/<username>/reward', methods=['GET'])
def user_reward_get(username):
    """
    Get a users reward points
    :param username:
    :return:
    """
    try:
        assert username == request.view_args['username']

        points = user.user_reward_points(username)

        response_json = json_dict({"reward_points": points}, indent=4)
        return Response(response_json, status=201, mimetype='application/json')

    except:
        response_json = json_dict({"status": "INVALID"}, indent=4)
        return Response(response_json, status=401, mimetype='application/json')


@app.route('/api/user/<username>/reward', methods=['PUT'])
def user_reward_update(username):
    """
    Update a users reward points
    :param username:
    :return:
    """
    try:
        assert username == request.view_args['username']

        json_request = request.json

        try:
            points = json_request['reward_points']
        except KeyError:
            response_json = json_dict({"status": "reward_points required paramter"}, indent=4)
            return Response(response_json, status=401, mimetype='application/json')

        user.update_user(username, reward_points=points)

        response_json = json_dict({"reward_points": points}, indent=4)
        return Response(response_json, status=201, mimetype='application/json')

    except:
        response_json = json_dict({"status": "INVALID"}, indent=4)
        return Response(response_json, status=401, mimetype='application/json')


@app.route('/api/user/<username>/tags', methods=['GET'])
def user_tag_get(username):
    """
    Retrive tags associated with user
    :param username:
    :return:
    """
    try:
        assert username == request.view_args['username']

        tags = user.user_info(username)['user_tags']

        if not isinstance(tags, str):
            response_json = json_dict({"status": "INVALID"}, indent=4)
            return Response(response_json, status=401, mimetype='application/json')

        response_json = json_dict({"user_tags": tags}, indent=4)
        return Response(response_json, status=201, mimetype='application/json')

    except:
        print("Unable to get user tags")
        response_json = json_dict({"status": "INVALID"}, indent=4)
        return Response(response_json, status=401, mimetype='application/json')


@app.route('/api/user/<username>/tags', methods=['PUT'])
def user_tag_add(username):
    """
    Add new tags to a user
    :param username:
    :return:
    """

    try:
        assert username == request.view_args['username']

        json_request = request.json

        # Check user_tags parameter exists
        try:
            new_tags = json_request['user_tags']
        except KeyError:
            print("No user_tags paramter")
            response_json = json_dict({"status": "user_tags paramter not found"}, indent=4)
            return Response(response_json, status=401, mimetype='application/json')

        current_tags = user.user_info(username)['user_tags']

        seperate = "" if current_tags == "" else ","  # stop incorrect commas at start of comma separated lists
        current_tags = current_tags + seperate + new_tags.replace(" ", "")  # remove whitespace in tags

        user.update_user(username, tags=current_tags)

        response_json = json_dict({"user_tags": current_tags}, indent=4)
        return Response(response_json, status=201, mimetype='application/json')

    except:
        print("Unable to update (PUT) user tags")
        response_json = json_dict({"status": "INVALID"}, indent=4)
        return Response(response_json, status=401, mimetype='application/json')


@app.route('/api/user/<username>/tags', methods=['DELETE'])
def user_tags_clear(username):
    """
    Delete ALL tags associate with user
    :param username:
    :return:
    """

    try:
        assert username == request.view_args['username']

        user.update_user(username, tags="")

        return Response("", status=201, mimetype='application/json')

    except:
        print("Unable to clear all user tags")
        response_json = json_dict({"status": "INVALID"}, indent=4)
        return Response(response_json, status=401, mimetype='application/json')


@app.route('/api/user/<username>/tag', methods=['DELETE'])
def user_tag_remove(username):
    """
    Delete SINGLE tag associate with user
    :param username:
    :return:
    """

    try:
        assert username == request.view_args['username']

        json_request = request.json

        # Check user_tags paramter exists, TODO replace with function
        try:
            tag = json_request['user_tag']
        except KeyError:
            tags = ""
            print("No user_tags paramter")
            response_json = json_dict({"status": "user_tags paramter not found"}, indent=4)
            return Response(response_json, status=401, mimetype='application/json')

        tags = user.user_info(username)['user_tags']
        tags = util.tag_validator(tags)  # format tags

        user.update_user(username, tags=tags)

        response_json = json_dict({"user_tags": tags}, indent=4)
        return Response(response_json, status=201, mimetype='application/json')

    except:
        print("Unable to delete user tag")
        response_json = json_dict({"status": "INVALID"}, indent=4)
        return Response(response_json, status=401, mimetype='application/json')


@app.route('/api/post', methods=['POST'])
def create_post():
    """
    Create a new post
    :return:
    """

    try:
        try: # Check parameters follow expected schema
            body_param = util.json_key(request,
                                       {
                                           "username":True,
                                           "message":True,
                                           "photo_path":False,
                                           "video_path":False,
                                           "post_tags":True
                                       })
        except KeyError:
            print("Couldnt create post : missing required paramters")
            response_json = json_dict({"status": "missing required parameters"}, indent=4)
            return Response(response_json, status=401, mimetype='application/json')

        post_id = post.create_post(
            body_param['username'],
            body_param['message'],
            0,
            util.tag_validator(body_param['post_tags']),  # format tags
            body_param['photo_path'],
            body_param['video_path']
        )

        response_json = json_dict({"post_id": post_id}, indent=4)
        return Response(response_json, status=201, mimetype='application/json')

    except:
        print("Unable to create post")
        response_json = json_dict({"status": "unable to create post"}, indent=4)
        return Response(response_json, status=401, mimetype='application/json')


@app.route('/api/post/<post_id>/likes', methods=['PUT'])
def update_post_likes(post_id):
    """
    Update the likes associated with a post
    :param post_id:
    :return:
    """
    try:
        assert post_id == request.view_args['post_id']

        # Get current likes
        current_likes = post.get_post(post_id)['likes']
        new_likes = current_likes + 1

        post.update_post(
            post_id,
            likes=new_likes
        )

        response_json = json_dict({"post_likes": new_likes}, indent=4)
        return Response(response_json, status=201, mimetype='application/json')
    except:
        print("Unable to update post likes")
        response_json = json_dict({"status": "unable to update post likes"}, indent=4)
        return Response(response_json, status=401, mimetype='application/json')


@app.route('/api/post/<post_id>', methods=['GET'])
def get_post_info(post_id):
    """
    Get information post
    Formatted as specific in API documentation
    :param post_id:
    :return:
    """

    try:
        assert post_id == request.view_args['post_id']

        post_info = post.get_post(post_id)

        response_json = json_dict(post_info, indent=4, default=str)
        return Response(response_json, status=201, mimetype='application/json')

    except:
        print("Unable to get post info")
        response_json = json_dict({"status": "unable to update post likes"}, indent=4)
        return Response(response_json, status=401, mimetype='application/json')


@app.route('/api/post/<post_id>/comments', methods=['GET'])
def get_comments(post_id):
    """
    Get a (JSON) list of all comments associated with a post
    :param post_id:
    :return:
    """

    try:
        assert post_id == request.view_args['post_id']

        comments = post.get_comments(
            post_id
        )

        response_json = json_dict(comments, indent=4, default=str)
        return Response(response_json, status=201, mimetype='application/json')

    except:
        print("Unable to get post info")
        response_json = json_dict({"status": "unable to update post likes"}, indent=4)
        return Response(response_json, status=401, mimetype='application/json')


@app.route('/api/post/<post_id>/comment', methods=['POST'])
def add_comment(post_id):
    """
    Adds a comment to a post
    :param post_id:
    :return:
    """

    try:
        assert post_id == request.view_args['post_id']

        try:  # verify required body parameters
            values = util.json_key(
                request,
                {
                    "username": True,
                    "message": True
                }
            )
        except KeyError:
            response_json = json_dict({"status": "missing essential parameters"}, indent=4)
            return Response(response_json, status=401, mimetype='application/json')

        comment_id = post.add_comment(
            post_id,
            values['message'],
            values['username']
        )

        response_json = json_dict({"comment_id": comment_id}, indent=4)
        return Response(response_json, status=201, mimetype='application/json')

    except:
        print("Unable to add post")
        response_json = json_dict({"status": "unable to add post"}, indent=4)
        return Response(response_json, status=401, mimetype='application/json')


@app.route('/api/user/<username>/posts', methods=['GET'])
def user_posts(username):
    """
    Retrieves posts associated with a user
    :param username:
    :return:
    """

    try:
        comments = post.get_post_user(username)

        response_json = json_dict(comments, indent=4, default=str)
        return Response(response_json, status=201, mimetype='application/json')
    except:
        print("Unable to get posts associated with user")
        response_json = json_dict({"status": "unable to get user posts"}, indent=4)
        return Response(response_json, status=401, mimetype='application/json')


@app.route('/api/posts', methods=['GET'])
def user_posts_filter():
    """
    Retrive posts associated with a (filter) paramters: tags & name
    :return:
    """

    try:
        try:  # verify required body parameters
            values = util.json_key(
                request,
                {
                    "tags": False,
                    "name": False
                }
            )
        except KeyError:
            response_json = json_dict({"status": "missing essential parameters"}, indent=4)
            return Response(response_json, status=401, mimetype='application/json')

        posts = post.get_post_tag_name(
            tags=values['tags'],
            name=values['name']
        )

        response_json = json_dict(posts, indent=4, default=str)
        return Response(response_json, status=201, mimetype='application/json')
    except:
        print("Unable to get posts associated with tags or name")
        response_json = json_dict({"status": "unable to get posts"}, indent=4)
        return Response(response_json, status=401, mimetype='application/json')

@app.route('/api/post/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    Delete post and associated comments
    :param post_id:
    :return:
    """

    try:
        assert post_id == request.view_args['post_id']

        post.remove_post_comments(post_id)
        post.remove_post(post_id)

        response_json = json_dict({"post_id":post_id}, indent=4, default=str)
        return Response(response_json, status=201, mimetype='application/json')
    except:
        print("Unable to get delete posts associated with ID " + post_id)
        response_json = json_dict({"status": "unable to delete posts"}, indent=4)
        return Response(response_json, status=401, mimetype='application/json')


@app.route('/api/comment/<comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """
    Delete a single comment
    :param comment_id:
    :return:
    """

    try:
        assert comment_id == request.view_args['comment_id']

        post.remove_comment(comment_id)

        response_json = json_dict({"comment_id": comment_id}, indent=4, default=str)
        return Response(response_json, status=201, mimetype='application/json')

    except:
        print("Unable to delete comment " + comment_id)
        response_json = json_dict({"status": "unable to delete comment"}, indent=4)
        return Response(response_json, status=401, mimetype='application/json')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
