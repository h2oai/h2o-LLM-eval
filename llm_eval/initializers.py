# import os

from h2o_wave import Q
from loguru import logger

from .common import make_base_ui


# async def custom_app_init(q: Q):
#     pass


# async def custom_user_init(q: Q):
# q.user.first_name = "Anonymous"
# q.user.last_name = "User"
# q.user.full_name = f"{q.user.first_name} {q.user.last_name}".strip().title()
# q.user.user_role = "user"
# pass


# async def custom_client_init(q: Q):
#     q.client.current_layout = "admin"
#     q.client.dark_mode = True


# async def initialize_app(q: Q):
# Initialize only once per app instance
# if q.app.initialized:
# return

# logger.info("Initializing App")

# All logged in users will be added to this during user init
# q.app.users = []

# Perform all initialization specific to this app
# await custom_app_init(q)

# Mark the app as initialized
# q.app.initialized = True


# async def initialize_user(q: Q):
#     anonymous_user_id = os.getenv("ANONYMOUS_USER_ID", "")
#     anonymous_user_email = os.getenv("ANONYMOUS_USER_EMAIL", "")
#     q.user.user_id = anonymous_user_id
#     q.user.email = anonymous_user_email

#     # If this user exists, do nothing
#     if q.user.user_id in q.app.users:
#         return

#     logger.info("Initializing User")

#     # Save new user
#     q.app.users.append(q.user.user_id)

#     # Perform user initialization specific to this app
#     await custom_user_init(q)


async def initialize_client(q: Q):
    if q.client.initialized:
        return

    logger.info("Initializing Client")

    # Perform all initialization specific to this app
    q.client.current_layout = "admin"
    q.client.dark_mode = True

    # Crate the first view of the app
    await make_base_ui(q, save=False)

    # Mark the client as initialized
    q.client.initialized = True
