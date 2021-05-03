import database
import util
import numpy

db = database.gains_db


def create_advert(
        name,
        message,
        link,
        frequency,
        photo_path=None,
        video_path=None,
):
    """
    Create an advert
    :param name:
    :param message:
    :param photo_path:
    :param video_path:
    :param link:
    :return:
    """

    try:
        cursor = db.cursor()
        advert_id = util.gen_id()

        advert_sql = "INSERT INTO advert (advert_id, name, message, photo_path, link, frequency, video_path) VALUE (%s,%s,%s,%s,%s,%s,%s)"
        values = (advert_id, name, message, photo_path, link, frequency, video_path)
        cursor.execute(advert_sql, values)
    except:
        print("Unable to create advert")
        raise Exception

    finally:
        db.commit()


def remove_advert(
        advert_id
):
    """
    Removes an advert
    :param advert_id:
    :return:
    """
    try:
        cursor = db.cursor()

        advert_sql = "DELETE FROM advert WHERE advert_id = %s"
        cursor.execute(advert_sql, (advert_id,))
    except:
        print("Unable to remove advert")
        raise Exception
    finally:
        db.commit()

def get_advert():
    """
    Returns a randoma advert, the higher the frequency the greater the chance of advert showing
    :return:
    """

    current_adverts = []
    try:
        cursor = db.cursor()

        advert_sql = "SELECT name, message, link, photo_path, video_path, frequency FROM advert"
        cursor.execute(advert_sql)

        current_adverts = cursor.fetchall()
    except:
        print("Unable to remove advert")
        raise Exception
    finally:
        db.commit()

    # Handle frequency and probability of adverts
    if len(current_adverts) > 1:
        advert_prob = numpy.array([ad[:-1] for ad in current_adverts])
        advert_prob = advert_prob / advert_prob.sum()

        sel_advert = numpy.random.choice(
            current_adverts,
            len(current_adverts),
            p=advert_prob
        )
    else:
        sel_advert = []

    return sel_advert

