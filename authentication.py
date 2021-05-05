import jwt
import datetime
from json import dumps as json_dict
from flask import Response


def encode_token(key, username):
    """
    Generate authentication token
    :param key:
    :param username:
    :return:
    """

    try:
        payload = {
            # 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
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

    token_username = decode_token(key, token)['username']

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
