import database
import unique_id

db = database.gains_db

def create_post(username,message,likes=0,post_tags="",media=None):
    """
    Create a post
    :param username:
    :param message:
    :param post_tags:
    :param likes:
    :param media:
    :return:
    """
    cursor = db.cursor()

    #Generate initial IDs
    media_id = None
    if(media != None):
        media_id = database.add_media(media)

    post_id = unique_id.gen_id()


    post_sql = "INSERT INTO post (post_id,message,post_tags,likes,username_id,content_media_id) VALUES (%s,%s,%s,%s,%s,%s)"
    values = (post_id,message,post_tags,likes,username,media_id)

    try:
        cursor.execute(post_sql,values)
        db.commit()
    except:
        print("Unable to create post")
        raise Exception

    return post_id