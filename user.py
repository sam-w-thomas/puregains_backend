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

    cursor = db.cursor()
    sql = "SELECT password FROM user WHERE username = %s"

    try:
        cursor.execute(sql, (username,))
        actual_password = cursor.fetchone()

        db.commit()
    except:
        print("Unable to get user information")
        raise Exception

    if actual_password == None: #Unable to get password
        raise Exception

    return True if actual_password[0] == password else False

def user_info(username):
    """
    Retrive information on user: name, birth_date, avatar and tags

    :param username:
    :return: info_user: Tuple of user information
    """
    cursor = db.cursor()
    user_sql = "SELECT name,birth_date,avatar_media_id,user_tags FROM user WHERE username = %s"

    info_user = ()
    try:
        cursor.execute(user_sql, (username,))
        info_user = cursor.fetchone()
    except:
        print("Unable to get user information")
        raise Exception

    return info_user

def update_user(username, name=None,avatar=None,reward_points=None,tags=None):
    """
    Update user values
    :param username:
    :param name:
    :param avatar:
    :param reward_points:
    :param tags:
    :return:
    """

    cursor = db.cursor()
    user_sql = "SELECT reward_profile_id FROM user WHERE username = %s"

    #Get initial information
    try:
        cursor.execute(user_sql, (username,))
        reward_id = cursor.fetchone()[0]
    except:
        print("Unable to get user information, to update")
        raise Exception

    db.commit()

    #Begin main edit
    try:
        if(name != None):
            name_sql = "UPDATE user SET name = %s WHERE username = %s"
            cursor.execute(name_sql, (name,username))

        if(avatar != None):
            avatar_media_id = database.add_media(avatar)
            avatar_sql = "UPDATE user SET avatar_media_id = %s WHERE username = %s"
            cursor.execute(avatar_sql, (avatar_media_id,username))

        if(reward_points != None):
            reward_sql = "UPDATE reward_profile SET points = %s WHERE reward_id = %s"
            cursor.execute(reward_sql, (reward_points, reward_id))

        if (tags != None):
            tags_sql = "UPDATE user SET user_tags = %s WHERE username = %s"
            cursor.execute(tags_sql, (tags, username))

        db.commit()

    except:
        print("Unable to update user information")
        raise Exception