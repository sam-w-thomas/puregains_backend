import database
import util
import time
import numpy

db = database.gains_db


def create_user(name, birth_date, avatar_path, password,desc=None, user_tags=""):
    """
    Create a user
    :param user_tags:
    :param avatar_path:
    :param name:
    :param birth_date:
    :param password:
    :return: username:
    """
    cursor = db.cursor()

    username = util.gen_username(name)
    reward_profile = create_reward_profile()

    create_sql = "INSERT INTO user (username,name,avatar_path,birth_date,password,reward_profile_id,user_tags,description) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    values = (
        username,
        name,
        avatar_path,
        birth_date,
        util.hash_password(password),
        reward_profile,
        user_tags.replace(" ", ""), # remove white space in tags
        desc
    )

    try:
        cursor.execute(create_sql, values)
        db.commit()
    except:
        print("Unable to create user")
        raise Exception

    return username


def create_reward_profile():
    """
    Create a blank reward profile
    :return:
    """
    cursor = db.cursor()

    id = util.gen_id()
    reward_sql = "INSERT INTO reward_profile (reward_id,points) VALUES (%s,%s)"
    values = (id, 0)
    cursor.execute(reward_sql, values)
    db.commit()

    return id


def delete_user(username):
    """
    Delete a user
    :param username:
    :return:
    """
    cursor = db.cursor()

    try:
        sql = "SELECT reward_profile_id FROM user WHERE username = %s"
        cursor.execute(sql, (username,))

        reward_profile_id = cursor.fetchone()[0]

        db.commit()

        delete_sql_user = "DELETE FROM user WHERE username = %s "
        delete_sql_reward = "DELETE FROM reward_profile WHERE reward_id = %s "

        cursor.execute(delete_sql_user, (username,))
        cursor.execute(delete_sql_reward, (reward_profile_id,))

        db.commit()
    except:
        print("Unable to delete user")
        raise Exception

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

    print(actual_password)
    if actual_password == None:  # Unable to get password
        raise Exception

    return True if actual_password[0] == password else False


def user_info(username):
    """
    Retrieve information on user: name, birth_date, avatar and tags

    :param username:
    :return: info_user: Tuple of user information
    """
    cursor = db.cursor()
    user_sql = "SELECT name,birth_date,avatar_path,user_tags,description FROM user WHERE username = %s"

    info_user = ()
    try:
        cursor.execute(user_sql, (username,))
        info_user = cursor.fetchone()
    except:
        print("Unable to get user information")
        raise Exception

    # Convert to dict
    return_user = {
        "name": "null",
        "birth_date": "null",
        "avatar_path": "null",
        "user_tags": "null",
        "description" : "null"
    }

    index = 0
    for key in return_user:
        return_user[key] = info_user[index]
        index += 1

    return return_user


def update_user(username, name=None, avatar_path=None, reward_points=None, tags=None, desc=None):
    """
    Update user values
    :param desc:
    :param username:
    :param name:
    :param avatar_path:
    :param reward_points:
    :param tags:
    :return:
    """

    cursor = db.cursor()
    user_sql = "SELECT reward_profile_id FROM user WHERE username = %s"

    # Get initial information
    try:
        cursor.execute(user_sql, (username,))
        reward_id = cursor.fetchone()[0]
    except:
        print("Unable to get user information, to update")
        raise Exception

    db.commit()

    # Begin main edit
    try:
        if name is not None:
            name_sql = "UPDATE user SET name = %s WHERE username = %s"
            cursor.execute(name_sql, (name, username))

        if avatar_path is not None:
            avatar_sql = "UPDATE user SET avatar_path = %s WHERE username = %s"
            cursor.execute(avatar_sql, (avatar_path, username))

        if reward_points is not None:
            reward_sql = "UPDATE reward_profile SET points = %s WHERE reward_id = %s"
            cursor.execute(reward_sql, (reward_points, reward_id))

        if tags is not None:
            tags_sql = "UPDATE user SET user_tags = %s WHERE username = %s"
            cursor.execute(tags_sql, (tags, username))

        if desc is not None:
            tags_sql = "UPDATE user SET description = %s WHERE username = %s"
            cursor.execute(tags_sql, (desc, username))

        db.commit()

    except:
        print("Unable to update user information")
        raise Exception


def user_reward_points(username):
    """
    Retrive a users reward points
    :param username:
    :return:
    """

    if not isinstance(username, str):  # Input checking
        raise Exception

    try:
        cursor = db.cursor()

        point_sql = "SELECT reward_profile.points " \
                    "FROM user INNER JOIN reward_profile " \
                    "ON user.reward_profile_id=reward_profile.reward_id WHERE user.username=(%s)" \

        cursor.execute(point_sql, (username,))

        points = cursor.fetchone()[0]

        return points

    except:
        print("Unable to get user reward points")
        raise Exception
    finally:
        db.commit()

