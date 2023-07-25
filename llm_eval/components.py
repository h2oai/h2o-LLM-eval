from typing import Dict, List
from uuid import UUID

import emoji
from h2o_wave import Q, ui

from db.db_utils import (
    get_num_games_by_model_prompt,
    get_num_wins_by_model_prompt,
    get_responses_for_model_prompt_v1,
)

from .layouts import get_layouts
from .wave_utils import WhiteSpace


def get_meta(q: Q, layouts=None):
    custom_css = ui.inline_stylesheet(
        content="""
            div[data-test="main"]>div {
                box-shadow: none;
            }
            div[data-test="main"]>div:hover {
                box-shadow: none;
            }
            div[data-test="model_left"] > div {
                box-shadow: none;
            }
            div[data-test="model_left"] > div:hover {
                box-shadow: none;
            }
            div[data-test="model_right"] > div {
                box-shadow: none;
            }
            div[data-test="model_right"] > div:hover {
                box-shadow: none;
            }
            div[data-test="actions"] > div {
                box-shadow: none;
            }
            div[data-test="actions"] > div:hover {
                box-shadow: none;
            }
            div[data-test="footer"] > div {
                box-shadow: none;
            }
            div[data-test="footer"] > div:hover {
                box-shadow: none;
            }
            div[data-test="model_row_0"] > div {
                box-shadow: none;
            }
            div[data-test="model_row_0"] > div:hover {
                box-shadow: none;
            }
            div[data-test="model_row_1"] > div {
                box-shadow: none;
            }
            div[data-test="model_row_1"] > div:hover {
                box-shadow: none;
            }
            div[data-test="model_row_2"] > div {
                box-shadow: none;
            }
            div[data-test="model_row_2"] > div:hover {
                box-shadow: none;
            }
            div[data-test="model_row_3"] > div {
                box-shadow: none;
            }
            div[data-test="model_row_3"] > div:hover {
                box-shadow: none;
            }
            div[data-test="model_row_4"] > div {
                box-shadow: none;
            }
            div[data-test="model_row_4"] > div:hover {
                box-shadow: none;
            }
            div[data-test="model_row_5"] > div {
                box-shadow: none;
            }
            div[data-test="model_row_5"] > div:hover {
                box-shadow: none;
            }
            div[data-test="model_row_6"] > div {
                box-shadow: none;
            }
            div[data-test="model_row_6"] > div:hover {
                box-shadow: none;
            }
            div[data-test="model_row_7"] > div {
                box-shadow: none;
            }
            div[data-test="model_row_7"] > div:hover {
                box-shadow: none;
            }
            div[data-test="model_row_8"] > div {
                box-shadow: none;
            }
            div[data-test="model_row_8"] > div:hover {
                box-shadow: none;
            }
            div[data-test="model_row_9"] > div {
                box-shadow: none;
            }
            div[data-test="model_row_9"] > div:hover {
                box-shadow: none;
            }
            """
    )
    if layouts is None:
        layouts = get_layouts()

    return ui.meta_card(
        box="",
        title="H2O LLM Eval",
        layouts=layouts,
        theme="h2o-dark",
        stylesheet=custom_css,
    )


async def get_header(q: Q):
    return ui.header_card(
        box="header",
        title="H2O LLM Eval",
        subtitle="v0.1.0",
        image="https://wave.h2o.ai/img/h2o-logo.svg",
        items=[],
        color="card",
    )


def get_footer():
    return ui.form_card(
        box=ui.box("footer"),
        items=[
            ui.inline(
                justify="center",
                items=[
                    ui.text("Made with 💛 using H2O Wave."),
                ],
            )
        ],
    )


def get_side_nav(q: Q):
    nav_items = [
        ui.nav_group(
            "Menu",
            items=[
                ui.nav_item(name="model_elo_leaderboard", label="Elo Rankings"),
                ui.nav_item(name="eval_method", label="Evaluation Method"),
                ui.nav_item(name="ab_test", label="Which is Better: A or B?"),
                ui.nav_item(name="admin_prompts_v1", label="Prompts", disabled=False),
                ui.nav_item(name="admin_responses", label="Responses", disabled=False),
            ],
            collapsed=False,
        ),
    ]

    return ui.nav_card(
        box=ui.box("left_nav"),
        value="model_elo_leaderboard",
        title="",
        subtitle="",
        items=nav_items,
    )


def get_response_card(title: str, content: str, box: str):
    return ui.form_card(
        box=ui.box(
            box,
        ),
        items=[
            ui.text_xl(name="title", content=title),
            ui.text_xl("   "),
            ui.text(content),
        ],
    )


def get_ab_test_buttons(model_a: UUID, model_b: UUID):
    items = [
        ui.buttons(
            justify="between",
            items=[
                ui.button(
                    name="ab_test_result",
                    label="A is Better",
                    primary=True,
                    value=str(model_a),
                ),
                ui.button(
                    name="ab_test_result",
                    label="B is Better",
                    primary=True,
                    value=str(model_b),
                ),
                ui.button(
                    name="ab_test_result",
                    label="Both are Same",
                    primary=False,
                    value="tie",
                ),
                ui.button(
                    name="ab_test_result",
                    label="Both are Bad",
                    primary=False,
                    value="both_bad",
                ),
                ui.button(
                    name="next_ab_test",
                    label="Next",
                    primary=False,
                ),
            ],
        ),
    ]
    return ui.form_card(
        box=ui.box(
            zone="main",
            order=1,
            height="65px",
        ),
        items=items,
    )


def get_ab_test_mini_buttons(model_a: UUID, model_b: UUID):
    items = [
        ui.inline(
            align="center",
            direction="column",
            items=[
                ui.text_l("Choose 🏆"),
                ui.text_l(WhiteSpace.em),
                ui.text_l(WhiteSpace.em),
                ui.button(
                    name="ab_test_result",
                    tooltip="A is Better",
                    label=emoji.emojize(":backhand_index_pointing_left: A is Better"),
                    width="150px",
                    value=str(model_a),
                ),
                ui.text_l(WhiteSpace.em),
                ui.button(
                    name="ab_test_result",
                    tooltip="B is Better",
                    label=emoji.emojize("B is Better :backhand_index_pointing_right:"),
                    width="150px",
                    value=str(model_b),
                ),
                ui.text_l(WhiteSpace.em),
                ui.button(
                    name="ab_test_result",
                    tooltip="Either is OK",
                    label=emoji.emojize(":OK_hand: Either is OK"),
                    width="150px",
                    value="tie",
                ),
                ui.text_l(WhiteSpace.em),
                ui.button(
                    name="ab_test_result",
                    tooltip="Both are Bad",
                    label=emoji.emojize(":warning: Both are Bad"),
                    width="150px",
                    value="both_bad",
                ),
                ui.text_l(WhiteSpace.em),
                ui.button(
                    name="next_ab_test",
                    tooltip="Next",
                    label=emoji.emojize(":next_track_button: Next"),
                    width="150px",
                ),
            ],
        ),
    ]
    return ui.form_card(
        box=ui.box(
            zone="actions",
        ),
        items=items,
    )


def get_response_flags():
    return [
        ui.text_l(emoji.emojize(":triangular_flag: Flag")),
        ui.checklist(
            name="flags",
            # label="Flag",
            choices=[
                ui.choice(name="not_appropriate", label="Not Appropriate"),
                ui.choice(name="hate_speech", label="Hate Speech"),
                ui.choice(name="sexual_content", label="Sexual Content"),
                ui.choice(name="other", label="Other"),
            ],
            inline=True,
        ),
        ui.text(WhiteSpace.em),
        ui.text(WhiteSpace.em),
        ui.text_l(emoji.emojize(":light_bulb: Additional Feedback")),
        ui.textbox(
            name="additional_feedback",
            multiline=True,
            spellcheck=True,
            width="500px",
            height="100px",
        ),
        ui.text(WhiteSpace.em),
        ui.text(WhiteSpace.em),
        ui.buttons(
            justify="start",
            items=[
                ui.button(
                    name="skip_ab_test",
                    label="Skip",
                    primary=False,
                    width="250px",
                ),
                ui.button(
                    name="submit_ab_test",
                    label="Submit",
                    primary=True,
                    width="250px",
                ),
            ],
        ),
    ]


def get_ab_test_radio_buttons(model_a: UUID, model_b: UUID):
    return [
        ui.text_l(emoji.emojize(":trophy: Which is better: A or B?")),
        ui.choice_group(
            name="ab_test_result",
            choices=[
                ui.choice(name=str(model_a), label="A is Better"),
                ui.choice(name=str(model_b), label="B is Better"),
                ui.choice(name="tie", label="Both are Equal"),
                ui.choice(name="both_bad", label="Both are Bad"),
            ],
            inline=True,
        ),
        ui.text(WhiteSpace.em),
        ui.text(WhiteSpace.em),
    ]


def get_prompt_card(prompt: str, model_a: UUID, model_b: UUID):
    return ui.form_card(
        box=ui.box("main"),
        items=[
            ui.text_xl("Prompt"),
            ui.text(content=f"**{prompt}**"),
        ],
    )


def get_loading_dialog():
    return ui.dialog(
        title="Loading",
        closable=False,
        blocking=True,
        items=[
            ui.progress(label=""),
        ],
    )


def get_ab_test_completed_dialog(q: Q):
    names = list(q.client.model_names.values())
    return ui.dialog(
        title="Eval Submitted!",
        closable=False,
        blocking=True,
        items=[
            ui.text(
                "Thank you for completing the AB test. Here are the names of the Models in your test."
            ),
            ui.text_l(WhiteSpace.em),
            ui.label("Model A:"),
            ui.text(names[0]),
            ui.label("Model B:"),
            ui.text(names[1]),
            ui.text_l(WhiteSpace.em),
            ui.buttons(
                justify="end",
                items=[
                    ui.button(
                        name="ab_test",
                        label="Close",
                        primary=True,
                    ),
                ],
            ),
        ],
    )


def get_admin_prompts_table(prompts):
    categories = {
        "planning": "$violet",
        "facts": "$azure",
        "question answering": "$purple",
        "recommendation": "$green",
        "writing": "$indigo",
        "harm": "$red",
        "troubleshooting": "$blue",
        "reasoning": "$mint",
        "math": "$white",
        "evaluation": "$tangerine",
        "summarization": "$pink",
        "coding": "$indigo",
        "knowledge": "$amber",
    }
    tags = [ui.tag(label=n, color=c) for n, c in categories.items()]
    return ui.table(
        name="admin_prompts_table",
        height="800px",
        columns=[
            ui.table_column(
                name="prompts_table_index",
                label="#",
                min_width="50px",
                link=False,
            ),
            ui.table_column(
                name="prompt_text",
                label="Prompt",
                min_width="1000px",
                link=False,
                cell_overflow="tooltip",
                sortable=False,
                searchable=True,
            ),
            ui.table_column(
                name="categories",
                label="Categories",
                min_width="250px",
                link=False,
                cell_overflow="tooltip",
                sortable=False,
                searchable=False,
                cell_type=ui.tag_table_cell_type(
                    name="tags",
                    tags=tags,
                ),
            ),
        ],
        resettable=True,
        rows=[
            ui.table_row(
                name=str(x["prompt_id"]),
                cells=[
                    str(i),
                    x.get("prompt_text") or "",
                    ",".join(x.get("categories", [])),
                ],
            )
            for i, x in enumerate(prompts, start=1)
        ],
        downloadable=False,
    )


def get_elo_table(models: List[Dict]):
    rows = []
    for i, m in enumerate(models, start=1):
        m_name = m.get("model_name", "")
        hf_url = m.get("model_hf_url", "")

        m_name_short = m_name
        if m_name:
            m_name_short = m_name.split("/")[-1]

        if m_name and hf_url:
            model_name = f"[{m_name_short}]({hf_url})"
        elif m_name:
            model_name = m_name_short
        else:
            model_name = ""

        license = m.get("license", "")

        diff_from_last_week_str = m.get("elo_score_delta", "-")

        elo_score = round(m.get("elo_score", 0))

        row = ui.table_row(
            name=str(m["model_id"]),
            cells=[  # type: ignore
                str(i),
                diff_from_last_week_str,
                model_name,
                str(elo_score),
                license,
            ],
        )
        rows.append(row)

    return ui.table(
        name="elo_table",
        height="850px",
        columns=[
            ui.table_column(
                name="model_rank",
                label="#",
                min_width="80px",
                max_width="80px",
                link=False,
            ),
            ui.table_column(
                name="model_rank_delta",
                label="▲",
                min_width="80px",
                max_width="80px",
                link=False,
            ),
            ui.table_column(
                name="model_name",
                label="Name",
                min_width="500px",
                link=False,
                cell_type=ui.markdown_table_cell_type(target="_blank"),
                cell_overflow="tooltip",
            ),
            ui.table_column(
                name="elo_rating",
                label="Elo Rating",
                min_width="150px",
                # align="right",
                data_type="number",
                sortable=True,
            ),
            ui.table_column(
                name="license",
                label="License",
                min_width="200px",
                filterable=False,
            ),
        ],
        resettable=True,
        rows=rows,
    )


def get_prompt_model_selection_card(q: Q):
    selected_prompt_text = q.client.prompts.get(q.client.selected_prompt_id).get("prompt_text")  # type: ignore
    items = [
        ui.inline(
            justify="between",
            items=[
                ui.inline(
                    justify="start",
                    items=[
                        ui.mini_button(
                            name="select_models_to_compare",
                            label="Select Models",
                            icon="Settings",
                        ),
                        ui.mini_button(
                            name="select_new_prompt",
                            label="Select New Prompt",
                            icon="Search",
                        ),
                        ui.mini_button(
                            name="show_previous_prompt",
                            label="Previous",
                            icon="Previous",
                        ),
                        ui.mini_button(
                            name="show_next_prompt",
                            label="Next",
                            icon="Next",
                        ),
                    ],
                ),
                ui.buttons(
                    justify="end",
                    items=[
                        ui.button(
                            name="show_gpt_eval",
                            label="Show GPT Eval",
                            primary=True,
                        ),
                    ],
                ),
            ],
        ),
        ui.text_m(
            name="select_eval_prompt",
            content=f"{q.client.current_prompt_idx + 1}. {selected_prompt_text}",
        ),
    ]

    return ui.form_card(
        box=ui.box(
            "main",
        ),
        items=items,
    )


async def make_model_response_cards(q: Q):
    for i in range(len(q.client.models)):
        del q.page[f"model_{i}"]

    for i, m_id in enumerate(q.client.selected_model_ids):
        model_row_num = i // 2
        response_row = await get_responses_for_model_prompt_v1(
            model_id=UUID(m_id), prompt_id=UUID(q.client.selected_prompt_id)
        )

        response_text = response_row[1]

        response_tstamp = response_row[5].strftime("%Y-%m-%d %H:%M:%S")

        num_games = await get_num_games_by_model_prompt(
            model_id=UUID(m_id), prompt_id=UUID(q.client.selected_prompt_id)
        )

        num_wins = await get_num_wins_by_model_prompt(
            model_id=UUID(m_id), prompt_id=UUID(q.client.selected_prompt_id)
        )

        win_rate = round((num_wins / num_games) * 100, 2) if num_games > 0 else 0

        q.page[f"model_{i}"] = ui.form_card(
            box=ui.box(f"model_row_{model_row_num}", width="50%"),
            items=[
                ui.text_l(q.client.models[m_id]["model_name"].split("/")[-1]),
                ui.inline(
                    justify="start",
                    items=[
                        ui.text_s(f"**Created at**: {response_tstamp} UTC"),
                        ui.text_s(f"**Win Rate**: {win_rate}%"),
                    ],
                ),
                ui.text_xl(WhiteSpace.em),
                ui.text_xl(WhiteSpace.em),
                ui.text(response_text),
            ],
        )
