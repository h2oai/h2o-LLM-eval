from h2o_wave import Q

from .common import make_base_ui


async def initialize_client(q: Q):
    if q.client.initialized:
        return

    # Perform all initialization specific to this app
    q.client.current_layout = "admin"
    q.client.dark_mode = True

    # Crate the first view of the app
    await make_base_ui(q, save=False)

    # Mark the client as initialized
    q.client.initialized = True
