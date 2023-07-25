from h2o_wave import ui
from h2o_wave.server import Q

from db.db_utils import get_elo_scores_new

from .components import (
    get_elo_table,
    get_footer,
    get_header,
    get_loading_dialog,
    get_meta,
    get_side_nav,
)


async def make_base_ui(q: Q, save=False):
    q.page["meta"] = get_meta(q)
    q.page["header"] = await get_header(q)
    q.page["side_nav"] = get_side_nav(q)
    q.page["footer"] = get_footer()

    set_full_page_layout(q)
    await show_elo_leaderboard(q)

    if save:
        await q.page.save()


def set_full_page_layout(q: Q):
    q.page["meta"] = get_meta(
        q,
        layouts=[
            ui.layout(
                breakpoint="xs",
                min_height="100vh",
                zones=[
                    ui.zone(
                        name="wrapper",
                        size="100vh",
                        zones=[
                            ui.zone("header", size="100px"),
                            ui.zone(
                                "container",
                                size="1",
                                direction=ui.ZoneDirection.ROW,
                                zones=[
                                    ui.zone(
                                        "left_nav",
                                        size="250px",
                                        direction=ui.ZoneDirection.COLUMN,
                                    ),
                                    ui.zone(
                                        "main_content",
                                        direction=ui.ZoneDirection.COLUMN,
                                        zones=[
                                            ui.zone(
                                                "main",
                                                size="1",
                                                direction=ui.ZoneDirection.COLUMN,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            ui.zone(name="footer", size="65px"),
                        ],
                    ),
                ],
            ),
        ],
    )


async def show_elo_leaderboard(q: Q):
    q.page["side_nav"].value = "model_elo_leaderboard"
    q.client.current_layout = "admin"

    q.page["meta"].dialog = get_loading_dialog()
    await q.page.save()

    models = await get_elo_scores_new()

    # Done ...

    q.page["meta"].dialog = None

    models_table = get_elo_table(models=models)
    q.page["model_elo_leaderboard"] = ui.form_card(
        box=ui.box("main"),
        items=[
            ui.text_xl("Elo Leaderboard"),
            ui.buttons(
                justify="end",
                items=[
                    ui.button(
                        name="add_new_model_from_elo",
                        label="Submit New Model for Eval",
                        primary=True,
                        icon="Add",
                        disabled=True,
                        visible=False,
                    ),
                ],
            ),
            models_table,
        ],
    )
    await q.page.save()
