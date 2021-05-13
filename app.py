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

import verify
from verify import verify_str, verify_birth_date, verify_str_none
from json import dumps as json_dict
import authentication
import hashlib

import util

from authentication import authenticated as auth
from authentication import auth_comment
from authentication import auth_post

import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = "0fc8-200-41ayyup-ad0c-11eb-aedf-b0fc36c63f34"

success_code = 200
created_code = 201


def response_invalid():
    response_json = flask.json.dumps({"Status": "Invalid parameters"})
    return Response(response_json, status=400, mimetype='application/json')


def response_unauthorised():
    response_json = flask.json.dumps({"Status": "Invalid authentication"})
    return Response(response_json, status=401, mimetype='application/json')


def response_notFound():
    response_json = flask.json.dumps({"status": "Not Found"})
    return Response(response_json, status=404, mimetype='application/json')


def response_unknown():
    response_json = flask.json.dumps({"Status": "Server side error"})
    return Response(response_json, status=500, mimetype='application/json')


@app.route('/', methods=['GET', 'POST'])
def request_connection():
    return "Flask Server & Android are Working Successfully"


@app.route('/api/user', methods=['POST'])
def user_create():
    try:
        name= ""
        birth = ""
        password = ""
        try:
            json_request = request.json
            name = json_request["name"]
            birth = json_request["birth_date"]
            password = json_request["password"]
        except:
            response_invalid()

        try:
            avatar_path = json_request["avatar_path"]
        except KeyError:
            avatar_path = ""

        try:
            user_tags = json_request["user_tags"]
        except KeyError:
            user_tags = ""

        try:
            description = json_request["description"]
        except KeyError:
            description = ""

        # Input checking
        if not verify_str(name) or not verify_birth_date(birth) or not verify_str(avatar_path) or not verify_str(
                password) or name == "" or password == "":
            print(verify_str(name))
            print(verify_birth_date(birth))
            print(verify_str(avatar_path))
            print(verify_str(password))
            return response_invalid()

        user_id = user.create_user(
            name,
            datetime.strptime(birth, "%Y/%M/%d").date(),
            avatar_path,
            password,
            description,
            user_tags
        )

        print("user created " + user_id)

        response_json = flask.json.dumps({"Username": user_id})
        return Response(response_json, status=created_code, mimetype='application/json')

    except Exception as e:
        print(e)
        return response_unknown()


@app.route('/api/user/<username>', methods=['PUT'])
def user_update(username):
    assert username == request.view_args['username']
    if not auth(  # authenticate user
            app.config['SECRET_KEY'],
            request,
            username
    ):
        return response_unauthorised()

    try:
        json_request = request.json

        values = util.json_key(
            request,
            {
                "name": False,
                "avatar_path": False,
                "reward_points": False,
                "credit": False,
                "tags": False,
                "desc": False
            }
        )

        user.update_user(
            username,
            values['name'],
            values['avatar_path'],
            values['reward_points'],
            values['tags'],
            values['desc'],
            values['credit']
        )

        response_json = json_dict(values, indent=4)
        return Response(response_json, status=success_code, mimetype='application/json')
    except Exception as e:
        print(e)
        return response_unknown()


@app.route('/api/user/<username>', methods=['GET'])
def get_user(username):
    assert username == request.view_args['username']

    if not verify.verify_str(username):
        return response_invalid()
    try:
        response_json = json_dict(
            user.user_info(username),
            indent=4,
            default=str
        )
    except:
        return response_notFound()

    return Response(response_json, status=success_code, mimetype='application/json')


@app.route('/api/user/<username>', methods=['DELETE'])
def delete_user(username):
    """
    Delete a user
    :param username:
    :return:
    """
    assert username == request.view_args['username']
    if not auth(  # authenticate user
            app.config['SECRET_KEY'],
            request,
            username
    ):
        return response_unauthorised()

    try:
        user.delete_user(username)
        response_json = json_dict({"User deleted: ": username}, indent=4)
        return Response(response_json, status=success_code, mimetype='application/json')
    except Exception as e:
        print(e)
        return response_unknown()


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

        response_json = json_dict({"Reward_points": points}, indent=4)
        return Response(response_json, status=success_code, mimetype='application/json')

    except:
        return response_notFound()


@app.route('/api/user/<username>/premium', methods=['PUT'])
def user_premium_update(username):
    """
    set a users profile to premium
    :param username:
    :return:
    """
    try:
        assert username == request.view_args['username']
        try:
            values = util.json_key(
                request,
                {
                    "premium": True
                }
            )
        except:
            return response_invalid()

        user.update_user(
            username,
            premium=values['premium']
        )

        response_json = json_dict({"premium": values['premium']}, indent=4)
        return Response(response_json, status=success_code, mimetype='application/json')

    except Exception as e:
        print(e)
        return response_unknown()


@app.route('/api/user/<username>/credit', methods=['PUT'])
def user_credit_update(username):
    """
    Sets a users credit
    :param username:
    :return:
    """
    try:
        assert username == request.view_args['username']
        try:
            values = util.json_key(
                request,
                {
                    "credit": True
                }
            )
        except:
            return response_invalid()

        user.user_credit_change(username,
                                values['credit'])

        response_json = json_dict({"credit": user.user_credit_amount(username)}, indent=4)
        return Response(response_json, status=success_code, mimetype='application/json')

    except Exception as e:
        print(e)
        return response_unknown()


@app.route('/api/user/<username>/type', methods=['GET'])
def user_type(username):
    """
    Get a users type (free or premium)
    :param username:
    :return:
    """
    try:
        assert username == request.view_args['username']
        type = user.user_type(username)
        response_json = json_dict({"type": type}, indent=4)
        return Response(response_json, status=success_code, mimetype='application/json')

    except:
        return response_notFound()


@app.route('/api/user/<username>/credit', methods=['GET'])
def user_credit_get(username):
    """
    Get a users credit
    :param username:
    :return:
    """
    try:
        assert username == request.view_args['username']
        points = user.user_credit_amount(username)
        response_json = json_dict({"credit": points}, indent=4)
        return Response(response_json, status=success_code, mimetype='application/json')

    except:
        return response_notFound()


@app.route('/api/user/<username>/reward', methods=['PUT'])
def user_reward_update(username):
    """
    Update a users reward points
    :param username:
    :return:
    """
    try:
        assert username == request.view_args['username']

        if not auth(  # authenticate user
                app.config['SECRET_KEY'],
                request,
                username
        ):
            return response_unauthorised()

        json_request = request.json

        try:
            points = json_request['reward_points']
            user.update_user(username, reward_points=points)
        except:
            return response_invalid()

        response_json = json_dict({"reward_points": points}, indent=4)
        return Response(response_json, status=success_code, mimetype='application/json')

    except Exception as e:
        print(e)
        return response_unknown()


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
            return response_invalid()

        response_json = json_dict({"user_tags": tags}, indent=4)
        return Response(response_json, status=success_code, mimetype='application/json')

    except Exception as e:
        print(e)
        return response_notFound()


@app.route('/api/user/<username>/tags', methods=['PUT'])
def user_tag_add(username):
    """
    Add new tags to a user
    :param username:
    :return:
    """

    try:
        assert username == request.view_args['username']

        if not auth(  # authenticate user
                app.config['SECRET_KEY'],
                request,
                username
        ):
            return response_unauthorised()

        json_request = request.json

        # Check user_tags parameter exists
        try:
            new_tags = json_request['user_tags']
            current_tags = user.user_info(username)['user_tags']
            separate = "" if current_tags == "" else ","  # stop incorrect commas at start of comma separated lists
            current_tags = current_tags + separate + new_tags.replace(" ", "")  # remove whitespace in tags
            user.update_user(username, tags=current_tags)
        except:
            return response_invalid()

        response_json = json_dict({"user_tags": current_tags}, indent=4)
        return Response(response_json, status=success_code, mimetype='application/json')

    except Exception as e:
        print(e)
        return response_unknown()


@app.route('/api/user/<username>/tags', methods=['DELETE'])
def user_tags_clear(username):
    """
    Delete ALL tags associate with user
    :param username:
    :return:
    """

    if not auth(  # authenticate user
            app.config['SECRET_KEY'],
            request,
            username
    ):
        return response_unauthorised()

    try:
        assert username == request.view_args['username']

        user.update_user(username, tags="")
        response_json = flask.json.dumps({"Status": "Tags deleted"})
        return Response(response_json, status=success_code, mimetype='application/json')

    except Exception as e:
        print(e)
        return response_unknown()


@app.route('/api/user/<username>/tag', methods=['DELETE'])
def user_tag_remove(username):
    """
    Delete SINGLE tag associate with user
    :param username:
    :return:
    """
    if not auth(  # authenticate user
            app.config['SECRET_KEY'],
            request,
            username
    ):
        return response_unauthorised()
    try:
        assert username == request.view_args['username']

        try:
            tag = request.json['user_tag']
            tags = user.user_info(username)['user_tags']
            new_tags = tags.replace(tag, '')
            new_tags = util.tag_validator(new_tags)  # format tags
            user.update_user(username, tags=new_tags)
        except KeyError:
            return response_invalid()

        response_json = json_dict({"user_tags": new_tags}, indent=4)
        return Response(response_json, status=success_code, mimetype='application/json')

    except Exception as e:
        print(e)
        return response_unknown()


@app.route('/api/post', methods=['POST'])
def create_post():
    """
    Create a new post
    :return:
    """
    try:

        try:  # Check parameters follow expected schema
            body_param = util.json_key(request,
                                       {
                                           "username": True,
                                           "message": True,
                                           "photo_path": False,
                                           "video_path": False,
                                           "post_tags": True
                                       })
        except:
            return response_invalid()

        if body_param['message'] == "" or body_param['post_tags'] == "":
            response_invalid()

        if not auth(app.config['SECRET_KEY'], request, body_param['username']):
            return response_unauthorised()

        post_id = post.create_post(
            body_param['username'],
            body_param['message'],
            0,
            util.tag_validator(body_param['post_tags']),  # format tags
            body_param['photo_path'],
            body_param['video_path']
        )
        response_json = json_dict({"post_id": post_id}, indent=4)
        return Response(response_json, status=created_code, mimetype='application/json')

    except Exception as e:
        print(e)
        return response_unknown()


@app.route('/api/post/<post_id>/likes', methods=['PUT'])
def update_post_likes(post_id):
    """
    Update the likes associated with a post
    :param post_id:
    :return:
    """

    try:
        try:
            json_request = request.json
            username = json_request["username"]
        except:
            return response_invalid()
        if not auth(  # authenticate user
                app.config['SECRET_KEY'],
                request,
                username
        ):
            return response_unauthorised()

        assert post_id == request.view_args['post_id']

        # Get current likes
        try:
            current_likes = post.get_post(post_id)['likes']
        except:
            return response_notFound()
        new_likes = current_likes + 1
        post.update_post(
            post_id,
            likes=new_likes
        )
        response_json = json_dict({"post_likes": new_likes}, indent=4)
        return Response(response_json, status=success_code, mimetype='application/json')

    except Exception as e:
        print(e)
        return response_unknown()


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

        try:
            post_info = post.get_post(post_id)
        except:
            return response_notFound()

        response_json = json_dict(post_info, indent=4, default=str)
        return Response(response_json, status=success_code, mimetype='application/json')

    except Exception as e:
        print(e)
        return response_unknown()


@app.route('/api/post/<post_id>/comments', methods=['GET'])
def get_comments(post_id):
    """
    Get a (JSON) list of all comments associated with a post
    :param post_id:
    :return:
    """

    try:
        assert post_id == request.view_args['post_id']

        try:
            comments = post.get_comments(
                post_id
            )
        except:
            return response_notFound()

        response_json = json_dict(comments, indent=4, default=str)
        return Response(response_json, status=success_code, mimetype='application/json')

    except Exception as e:
        print(e)
        return response_unknown()


@app.route('/api/post/<post_id>/comment', methods=['POST'])
def add_comment(post_id):
    """
    Adds a comment to a post
    :param post_id:
    :return:
    """
    try:
        assert post_id == request.view_args['post_id']

        if not auth_post(  # authenticate user
                app.config['SECRET_KEY'],
                request,
                post_id
        ):
            return response_unauthorised()

        try:  # verify required body parameters
            values = util.json_key(
                request,
                {
                    "username": True,
                    "message": True
                }
            )
            print(values['username'])
        except:
            return response_invalid()

        try:
            comment_id = post.add_comment(
                post_id,
                values['message'],
                values['username']
            )
        except:
            return response_notFound()

        response_json = json_dict({"comment_id": comment_id}, indent=4)
        return Response(response_json, status=created_code, mimetype='application/json')

    except Exception as e:
        print(e)
        return response_unknown()


@app.route('/api/user/<username>/posts', methods=['GET'])
def user_posts(username):
    """
    Retrieves posts associated with a user
    :param username:
    :return:
    """

    try:
        posts = post.get_post_user(username)
        if not posts:
            return response_notFound()
        response_json = json_dict(posts, indent=4, default=str)
        return Response(response_json, status=success_code, mimetype='application/json')
    except Exception as e:
        print(e)
        return response_unknown()


@app.route('/api/posts', methods=['GET'])
def user_posts_filter():
    """
    Retrive posts associated with a (filter) paramters: tags & name
    If no paramters, returns all posts
    :return:
    """

    try:
        tags = request.headers.get("tags")
        name = request.headers.get("name")

        if tags is None and name is None:
            posts = post.get_posts()
        else:
            posts = post.get_post_tag_name(
                tags=tags,
                name=name
            )

        response_json = json_dict(posts, indent=4, default=str)
        return Response(response_json, status=success_code, mimetype='application/json')

    except Exception as e:
        print(e)
        return response_unknown()


@app.route('/api/post/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    Delete post and associated comments
    :param post_id:
    :return:
    """
    try:
        assert post_id == request.view_args['post_id']
        try:
            if not auth_post(  # authenticate user
                    app.config['SECRET_KEY'],
                    request,
                    post_id
            ):
                return response_unauthorised()
            post.remove_post_comments(post_id)
            post.remove_post(post_id)
        except:
            return response_notFound()

        response_json = json_dict({"post deleted: ": post_id}, indent=4, default=str)
        return Response(response_json, status=success_code, mimetype='application/json')

    except Exception as e:
        print(e)
        return response_unknown()


@app.route('/api/comment/<comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """
    Delete a single comment
    :param comment_id:
    :return:
    """

    try:
        assert comment_id == request.view_args['comment_id']
        try:
            if not auth_comment(  # authenticate user
                    app.config['SECRET_KEY'],
                    request,
                    comment_id
            ):
                return response_unauthorised()
            post.remove_comment(comment_id)
        except:
           return response_notFound()

        response_json = json_dict({"Comment deleted: ": comment_id}, indent=4, default=str)
        return Response(response_json, status=success_code, mimetype='application/json')

    except Exception as e:
        print(e)
        return response_unknown()


@app.route('/api/post/<post_id>/tags', methods=['PUT'])
def post_tags(post_id):
    """
    Update a post tags
    :param post_id:
    :return:
    """

    try:
        try:
            assert post_id == request.view_args['post_id']
            if not auth_post(  # authenticate user
                    app.config['SECRET_KEY'],
                    request,
                    post_id
            ):
                return response_unauthorised()
        except:
            return response_notFound()
        try:
            tags = request.json['post_tags']
            current_tags = post.get_post(post_id)['post_tags']
            new_tags = util.tag_validator(current_tags + "," + tags)
            post.update_post(
                post_id,
                new_tags
            )
        except:
            return response_invalid()

        response_json = json_dict({"post_tags": new_tags}, indent=4, default=str)
        return Response(response_json, status=success_code, mimetype='application/json')

    except Exception as e:
        print(e)
        return response_unknown()


@app.route('/api/post/<post_id>/tag', methods=['DELETE'])
def delete_tag(post_id):
    """
    Remove tag from post
    :param post_id:
    :return:
    """

    try:
        try:
            if not auth_post(  # authenticate user
                    app.config['SECRET_KEY'],
                    request,
                    post_id
            ):
                return response_unauthorised()
        except:
            return response_notFound()

        try:
            tag = request.json['post_tag']
            current_tags = post.get_post(post_id)['post_tags']
            new_tags = util.tag_validator(
                current_tags.replace(tag, "")
            )
            post.update_post(
                post_id,
                post_tags=new_tags
            )
        except KeyError:
            return response_invalid()

        response_json = json_dict({"post_tags": new_tags}, indent=4, default=str)
        return Response(response_json, status=success_code, mimetype='application/json')

    except Exception as e:
        print(e)
        return response_unknown()


@app.route('/api/token/<username>', methods=['GET'])
def get_token(username):
    """
    Generate authentication token, checks password
    :param username:
    :return:
    """
    try:
        assert username == request.view_args['username']

        password = request.headers.get("Password")
        if password is None: return response_invalid()

        # hash password
        hashed_password = util.hash_password(password)
        # check password
        if not user.check_password(username, hashed_password):
            return response_unauthorised()

        token = authentication.encode_token(app.config['SECRET_KEY'], username)
        response_json = json_dict({"token": token}, indent=4, default=str)
        return Response(response_json, status=success_code, mimetype='application/json')

    except Exception as e:
        print(e)
        return response_unknown()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
