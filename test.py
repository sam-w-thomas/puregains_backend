import user
import time
import database
import post

# user.create_user(
#     "Samuel Thomas",
#     time.strftime('%Y-%m-%d %H:%M:%S'),
#     database.create_media("imgs/sam_picture.jpg"),
#     "PASSWORD"
# )

post.create_post(
    "samue.cf45d2",
    "Gotta get them squats working lovely HOT",
    likes=0,
    media=database.create_media("imgs/sam_picture.jpg")
)