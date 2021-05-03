import uuid
import hashlib
import os

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
    return str(name[0:5]).lower().replace(" ", "_") + "." + str(uuid.uuid1())[0:6] #check username doesnt already exist in future

def hash_password(password):
    return hashlib.md5(password.encode('utf-8')).hexdigest()


