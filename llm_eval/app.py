from dotenv import find_dotenv, load_dotenv
from h2o_wave import Q, app, handle_on, main  # noqa: F401
from loguru import logger

from . import handlers  # noqa: F401
from .initializers import initialize_app, initialize_client, initialize_user
from .wave_utils import handle_crash


def on_startup():
    _ = load_dotenv(find_dotenv())
    logger.info("Starting H2O LLM Eval!")


def on_shutdown():
    logger.info("Stopping H2O LLM Eval!")


@app("/", on_startup=on_startup, on_shutdown=on_shutdown)
async def serve(q: Q):
    # Wrap the entire app functionality in a try/except block
    # This will prevent the app from crashing and showing stack traces in the UI
    try:
        # Initialization
        await initialize_app(q)
        await initialize_user(q)
        await initialize_client(q)

        # Handle pre-defined actions for user input
        await handle_on(q)

    except Exception as unknown_exception:  # noqa
        logger.exception(unknown_exception)

        # Inform the user that something went wrong
        await handle_crash(q)
