import database
import unique_id
import time
from PIL import Image
import numpy

db = database.gains_db


def create_user(name,birth_date,avatar,password):
    """
    Create a user
    :param name:
    :param birth_date:
    :param avatar:
    :param password:
    :return: username:
    """
    cursor = db.cursor()

    #ID setup
    avatar = database.add_media(avatar) #wrap in try, except - if problem set avatar as standard
    username = unique_id.gen_username(name)
    reward_profile = create_reward_profile()

    create_sql = "INSERT INTO user (username,name,avatar_media_id,birth_date,password,reward_profile_id) VALUES (%s,%s,%s,%s,%s,%s)"
    values = (
        username,
        name,
        avatar,
        birth_date,
        password,
        reward_profile
    )

    cursor.execute(create_sql,values)
    db.commit()

    return username

def create_reward_profile():
    """
    Create a blank reward profile
    :return:
    """
    cursor = db.cursor()

    id = unique_id.gen_id()
    reward_sql = "INSERT INTO reward_profile (reward_id,points) VALUES (%s,%s)"
    values = (id, 0)
    cursor.execute(reward_sql,values)
    db.commit()

    return id


def delete_user(username):
    """
    Delete a user
    :param username:
    :return:
    """
    cursor = db.cursor()

    sql = "SELECT reward_profile_id, avatar_media_id FROM user WHERE username = %s"
    cursor.execute(sql, (username,))

    reward_profile_id, avatar_media_id = cursor.fetchone()

    db.commit()

    delete_sql_user = "DELETE FROM user WHERE username = %s "
    delete_sql_avatar = "DELETE FROM media WHERE media_id = %s "
    delete_sql_reward = "DELETE FROM reward_profile WHERE reward_id = %s "

    cursor.execute(delete_sql_user, (username,))
    cursor.execute(delete_sql_avatar, (avatar_media_id,))
    cursor.execute(delete_sql_reward, (reward_profile_id,))

    db.commit()

    return username

def check_password(username, password):
    """
    Compare hashed password for user is correct
    :param password:
    :return: boolean:
    """

    sql = "SELECT password FROM user WHERE password = %s"
    cursor = db.cursor()

    cursor.execute(sql, (username,))
    actual_password = cursor.fetchone()

    db.commit()

    return True if actual_password == password else False

