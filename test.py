import datetime

import util
import user
import post
import authentication

# print(user.create_user(
#     "Samuel Thomas",
#     datetime.date(1999, 12, 4),
#     "sam_photo",
#     "ROB"
# ))

# user.delete_user("samue.1f7cd1")

# user.update_user("samue.5e1588", avatar_path="leg_squat")

# post.create_post(
#     "samue.062405",
#     "ROAST"
# )

# post.update_post(
#     "0f4f8201-ab4b-11eb-a71f-b0fc36c63f34",
#     post_tags="hello, gym, excercise"
# )

# print(post.get_post_user("samue.062405"))

# print(
#     post.get_post_tag_name(
#         name="Steven"
#     )
# )

# print(
#     post.add_comment(
#         "0f4f8201-ab4b-11eb-a71f-b0fc36c63f34",
#         "THIS IS A MESSAGE FOR A COMMENT",
#         "samue.062405"
#     )
# )

# print(
#     post.remove_comment("693f712e-ab53-11eb-a370-b0fc36c63f34")
# )

# print(
#     util.tag_validator("hello,,,   test,,,,,")
# )

# print(
#     post.get_post_user("bob_r.2743cd")
# )

token = authentication.encode_token(
    "Test",
    "paul"
)

authentication.authenticate(
    "Test",
    token,
    "steve"
)

