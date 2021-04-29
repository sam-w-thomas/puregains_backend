import mysql.connector
import unique_id
import time

gains_db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="toor",
    database="mydb"
)


def add_media(media):
    """
    Add media to backend database
    :param media: binary string of media
    :return: media_id
    """
    cursor = gains_db.cursor()

    id = unique_id.gen_id()
    date = time.strftime('%Y-%m-%d %H:%M:%S')

    media_sql = "INSERT INTO Media (media_id,date_posted,content) VALUES (%s,%s,%s)"
    values = (id, date, media)

    try:
        cursor.execute(media_sql,values)
        gains_db.commit()
    except Exception:
        print("Unable to add media")
        raise Exception

    return id

def create_media(filename):
    with open(filename, 'rb') as file:
        binary_file = file.read()
    return binary_file

