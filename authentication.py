import jwt
import datetime
from json import dumps as json_dict
from flask import Response
import post

def encode_token(key, username):
    """
    Generate authentication token
    :param key:
    :param username:
    :return:
    """

    try:
        payload = {
            'iat': datetime.datetime.utcnow(),
            'username': username
        }

        token = jwt.encode(
            payload,
            key,
            algorithm='HS256'
        )

        return token

    except Exception as e:
        response_json = json_dict({"status": "unable to generate token"}, indent=4)
        return Response(response_json, status=401, mimetype='application/json')


def authenticated(key, request, username):
    """
    Validate a request with a supplied username
    Raises
    :param key:
    :param request:
    :param username:
    :return:
    """

    if 'x-access-tokens' in request.headers:
        token = request.headers['x-access-tokens']
    else:
        return False

    try:
        token_username = decode_token(key, token)['username']
    except:
        return False

    if token_username != username:
        return False

    return True


def decode_token(key, token):
    """
    Validate authentication token
    Returns payload
    :param key:
    :param token:
    :return:
    """

    try:
        response = jwt.decode(
            token,
            key,
            algorithms=['HS256']
        )

        return response

    except:
        raise Exception

def auth_post(key, request, post_id):
    """
    Authenticate a post, ie user editing post
    :param post_id:
    :return:
    """

    username = post.get_post(post_id)['username']

    return authenticated(key, request, username)

def auth_comment(key, request, comment_id):
    """
    Authenticate a comment, ie user editing post
    :param comment_id:
    :return:
    """

    username = post.get_comment(comment_id)['username']

    return authenticated(key, request, username)
