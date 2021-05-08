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

    # Check tags are valid
    post_tags = post_tags[1:] if post_tags.startswith(",") else post_tags
    post_tags = post_tags[:-1] if post_tags.endswith(",") else post_tags

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

    return_post = {
        "username": None,
        "message": None,
        "post_tags": None,
        "likes": None,
        "post_date": None,
        "photo_path": None,
        "video_path": None
    }

    index = 0
    for key in return_post:
        return_post[key] = result[index]
        index += 1

    return return_post


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
        all_user_sql = "SELECT post.post_id, post.username_id, post.message, post.post_tags, post.likes, post.post_date, post.photo_path, post.video_path, user.name, user.avatar_path " \
                       "FROM post INNER JOIN user " \
                       "ON post.username_id=user.username " \
                       "WHERE username_id = (%s)"
        cursor.execute(all_user_sql, (username,))
        posts = cursor.fetchall()

        # format comments to (list of) dict
        return_posts = util.format_posts(posts)

        return return_posts

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

    # convert tags into list
    valid_posts = set()

    try:
        cursor = db.cursor()

        if tags is not None:
            tags = tags.split(",")
            for tag in tags:
                tag_sql = "SELECT post.post_id, post.username_id, post.message, post.post_tags, post.likes, post.post_date, post.photo_path, post.video_path, user.name, user.avatar_path " \
                          "FROM post INNER JOIN user " \
                          "ON post.username_id==user.username" \
                          "WHERE post_tags LIKE CONCAT('%', %s,'%') "
                cursor.execute(tag_sql, (tag,))

                tag_posts = cursor.fetchall()
                # Add valid posts into valid_posts
                for tag_post in tag_posts:
                    if tag_post is not None:
                        valid_posts.add(tag_post)

        if name is not None:
            name_sql = "SELECT post.post_id, post.username_id, post.message, post.post_tags, post.likes, post.post_date, post.photo_path, post.video_path, user.name, user.avatar_path  " \
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

    return util.format_posts(list(valid_posts))


def get_posts():
    """
    Get all posts
    :return:
    """

    post_sql = "SELECT post.post_id, post.username_id, post.message, post.post_tags, post.likes, post.post_date, post.photo_path, post.video_path, user.name, user.avatar_path " \
               "FROM post INNER JOIN user " \
               "ON post.username_id=user.username"
    valid_posts = set()

    try:
        cursor = db.cursor()
        cursor.execute(post_sql)

        posts = cursor.fetchall()
        # Add valid posts into valid_posts
        for post in posts:
            if post is not None:
                valid_posts.add(post)

        return util.format_posts(list(valid_posts))

    except:
        print("Unable to get all posts")
        raise Exception
    finally:
        db.commit()

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


def get_comments(post_id):
    """
    Retrieve comments associated with particular comment
    :param post_id:
    :return:
    """

    try:
        cursor = db.cursor()

        comment_sql = "SELECT comment_id, message, post_id, username " \
                      "FROM comment WHERE comment.post_id=(%s)"

        cursor.execute(comment_sql, (post_id,))

        all_comments = cursor.fetchall()

        # format comments to (list of) dict
        return_comments = list()
        template_comment = {
            "comment_id": None,
            "message": None,
            "post_id": None,
            "username": None
        }

        for comment in all_comments:
            index = 0
            for key in template_comment:
                template_comment[key] = comment[index]
                index += 1

            return_comments.append(template_comment)

        return return_comments

    except:
        print("Unable to get comments")
        raise Exception
    finally:
        db.commit()

def get_comment(comment_id):
    """
    Retrieve comment associated with particular comment_id
    :param post_id:
    :return:
    """

    try:
        cursor = db.cursor()

        comment_sql = "SELECT comment_id, message, post_id, username " \
                      "FROM comment WHERE comment.comment_id=(%s)"

        cursor.execute(comment_sql, (comment_id,))

        comment = cursor.fetchone()
        template_comment = {
            "comment_id": None,
            "message": None,
            "post_id": None,
            "username": None
        }

        index = 0
        for key in template_comment:
            template_comment[key] = comment[index]
            index += 1

        return template_comment
    except:
        print("Unable to get comments")
        raise Exception
    finally:
        db.commit()


def remove_post_comments(post_id):
    """
    Delete all comments associated with post
    :param post_id:
    :return:
    """
    try:
        cursor = db.cursor()

        comment_sql = "DELETE FROM comment WHERE post_id=(%s)"

        cursor.execute(comment_sql, (post_id,))
    except:
        print("Unable to remove posts associated with " + post_id)
        raise Exception

