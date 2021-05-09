import uuid
import hashlib
import os
import datetime
from operator import itemgetter

def gen_id():
    """
    Generate unique ID, return as string
    :return:
    """
    return str(uuid.uuid1())


def gen_username(name):
    """
    Geneate username, first five characters of username, plus
    :param name:
    :return:
    """
    return str(name[0:5]).lower().replace(" ", "_") + "." + str(uuid.uuid1())[
                                                            0:6]  # check username doesnt already exist in future


def hash_password(password):
    return hashlib.md5(password.encode('utf-8')).hexdigest()


def json_key(request, values):
    """
    Generates a dictionary of values of request body
    Raises key error if any TRUE values are not present
    Items not required, but not present, are None

    :raises KeyError:
    :param values:
    :param request:
    :return:
    """
    request_json = request.json

    return_dict = dict()
    if request.method == 'GET':
        headers = request.headers

        for key, value in values.items():
            try:
                return_dict[key] = headers[key]
            except KeyError:
                if value is True:
                    raise KeyError
                else:
                    return_dict[key] = None
    else:
        for key, value in values.items():
            try:
                return_dict[key] = request_json[key]
            except KeyError:
                if value is True:
                    raise KeyError
                else:
                    return_dict[key] = None

    return return_dict


def tag_validator(tags):
    """
    Validates a comma-seperated tag string
    Returns a valid tag string
    :param tags:
    :return:
    """

    print(tags)

    tags = tags.replace(",,", ",")
    tags = tags.replace(" ", "")

    tags = tags[1:] if tags.startswith(",") else tags
    tags = tags[:-1] if tags.endswith(",") else tags

    if tags.startswith(",") or tags.endswith(",") or ",," in tags or " " in tags:
        return tag_validator(tags)  # recursion to get to base case when no tags at start or end
    else:
        if len(tags) > 100:
            print("Tag length of 100 excedded in post")
            raise Exception
        return tags


def format_posts(posts):
    """
    Formats posts into a (list of) dictionary's
    :param posts:
    :return:
    """

    return_posts = list()
    template_post = {
        "post_id": None,
        "username": None,
        "message": None,
        "post_tags": None,
        "likes": None,
        "post_date": None,
        "photo_path": None,
        "video_path": None,
        "name": None,
        "avatar_path" : None

    }

    for post in posts:
        index = 0
        for key in template_post:
            template_post[key] = post[index]
            index += 1

        return_posts.append(template_post.copy()) # copy required as otherwise you just overwrite the original reference

    return_posts.sort(key=lambda post_item:str(post_item['post_date']), reverse=True)
    return return_posts
