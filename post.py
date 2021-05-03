import database
import util
import datetime

db = database.gains_db


def create_post(username, message, likes=0, post_tags="", photo_path=None, video_path=None):
    """
    Create a post
    :param photo_path:
    :param video_path:
    :param username:
    :param message:
    :param post_tags:
    :param likes:
    :return:
    """
    cursor = db.cursor()

    post_id = util.gen_id()
    date = datetime.datetime.now()

    post_sql = "INSERT INTO post (post_id, message, post_tags, likes, username_id, photo_path, video_path, post_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    values = (post_id, message, post_tags, likes, username, photo_path, video_path, date)

    try:
        cursor.execute(post_sql, values)
        db.commit()
    except:
        print("Unable to create post")
        raise Exception

    return post_id


def remove_post(post_id):
    """
    Remove a post
    :param post_id:
    :return:
    """
    cursor = db.cursor()

    remove_sql = "DELETE FROM post WHERE post_id = (%s)"

    try:
        cursor.execute(remove_sql, (post_id,))
    except:
        print("Unable to remove post")
        raise Exception
    finally:
        db.commit()


def get_post(post_id):
    """
    Return information about a post
    :param post_id:
    :return:
    """
    cursor = db.cursor()

    post_sql = "SELECT username_id, message, post_tags, likes, post_date, photo_path, video_path FROM post WHERE post_id = (%s)"

    result = ()
    try:
        cursor.execute(post_sql, (post_id,))
        result = cursor.fetchone()
    except:
        print("Unable to get post")
        raise Exception
    finally:
        db.commit()

    return result


def update_post(
        post_id,
        post_tags=None,
        likes=None
):
    """
    Update a posts likes and tags. Result of post NOT editable
    :param post_id:
    :param post_tags:
    :param likes:
    :return:
    """
    cursor = db.cursor()

    try:
        if post_tags is not None:
            tags_sql = "UPDATE post SET post_tags = %s WHERE post_id = %s"
            cursor.execute(tags_sql, (post_tags, post_id))

        if likes is not None:
            likes_sql = "UPDATE post SET likes = %s WHERE post_id = %s"
            cursor.execute(likes_sql, (likes, post_id))

    except:
        print("Unable to update post")
        raise Exception
    finally:
        db.commit()

    return post_id


def get_post_user(username):
    """
    Get all posts associated with a user
    :param username:
    :return:
    """

    all_user_data = ()
    try:
        cursor = db.cursor()
        all_user_sql = "SELECT post_id, username_id, message, post_tags, likes, post_date, photo_path, video_path FROM post WHERE username_id = (%s)"
        cursor.execute(all_user_sql, (username,))
        all_user_data = cursor.fetchall()

    except:
        print("Unable to get all posts")
        raise Exception
    finally:
        db.commit()

    return all_user_data


def get_post_tag_name(
        tags=None,
        name=None):
    """
    Get posts associated with tags or name
    :param name:
    :param tags:
    :return:
    """

    # Conver tags into list
    valid_posts = set()

    try:
        cursor = db.cursor()

        if tags is not None:
            tags = tags.split(",")
            for tag in tags:
                tag_sql = "SELECT post_id, username_id, message, post_tags, likes, post_date, photo_path, video_path FROM post WHERE post_tags LIKE CONCAT('%', %s,'%') "
                cursor.execute(tag_sql, (tag,))

                tag_posts = cursor.fetchall()
                # Add valid posts into valid_posts
                for tag_post in tag_posts:
                    if tag_post is not None:
                        valid_posts.add(tag_post)

        if name is not None:
            name_sql = "SELECT post.post_id, post.username_id, post.message, post.post_tags, post.likes, post.post_date, post.photo_path, post.video_path, user.username " \
                       "FROM post INNER JOIN user ON post.username_id=user.username " \
                       "WHERE user.name LIKE CONCAT('%', %s,'%')"

            cursor.execute(name_sql, (name,))
            name_posts = cursor.fetchall()
            for name_post in name_posts:
                if name_post is not None:
                    valid_posts.add(name_post)
    except:
        print("Unable to get posts associated with tags / name")
        raise Exception
    finally:
        db.commit()

    return list(valid_posts)


def add_comment(
        post_id,
        message,
        username):
    """
    Add a comment to a post
    :param post_id:
    :param message:
    :return:
    """

    try:
        cursor = db.cursor()

        comment_id = util.gen_id()

        comment_sql = "INSERT INTO comment (comment_id, message, post_id, username) VALUES (%s, %s, %s, %s)"
        values = (comment_id, message, post_id, username)

        cursor.execute(comment_sql, values)
    except:
        print("Unable to add comment")
        raise Exception
    finally:
        db.commit()

    return comment_id


def remove_comment(comment_id):
    """
    Remove a comment
    :param comment_id:
    :return:
    """
    cursor = db.cursor()

    remove_sql = "DELETE FROM comment WHERE comment_id = (%s)"

    try:
        cursor.execute(remove_sql, (comment_id,))
    except:
        print("Unable to remove comment")
        raise Exception
    finally:
        db.commit()

    return comment_id
