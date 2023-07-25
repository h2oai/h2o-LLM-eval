from datetime import datetime, timezone
from uuid import UUID

from h2o_wave import Q, on, ui
from loguru import logger

from db.db_utils import (
    get_ab_test_by_model_ids,
    get_all_model_names_ids,
    get_all_prompts_sha_v1,
    get_all_prompts_v1_with_tags,
    get_elo_scores_new,
    get_evals_by_model_for_eval_model_ab_test_prompt,
    get_random_ab_task_for_user,
    get_random_ab_task_for_user_no_repeat_v1,
    insert_eval_by_human_into_db,
)
from .utils import get_sha256

from .components import (
    get_ab_test_mini_buttons,
    get_admin_prompts_table,
    get_elo_table,
    get_loading_dialog,
    get_meta,
    get_prompt_card,
    get_prompt_model_selection_card,
    get_response_card,
    make_model_response_cards,
)
from .landing_page import content, references, system_prompt_and_api_call
from .layouts import get_zones4
from .wave_utils import WhiteSpace


@on()
async def close_dialog(q: Q):
    q.page["meta"].dialog = None

    q.client.ab_test_id = None
    q.client.prompt_id = None
    q.client.model_names = None
    q.client.model_id = None
    q.client.eval_model_id = None

    await q.page.save()


async def load_ab_test(q: Q):
    # Loading ....

    q.page["side_nav"].value = "ab_test"

    q.page["meta"].dialog = get_loading_dialog()
    await q.page.save()

    random_task = await get_random_ab_task_for_user()

    if not random_task:
        q.page["meta"].dialog = None
        await q.page.save()
        return

    q.client.prompt_id = random_task["prompt_id"]  # type: ignore
    q.client.ab_test_id = random_task["ab_test_id"]  # type: ignore

    prompt_text = random_task["prompt_text"]  # type: ignore
    model_a_id = random_task["responses"][0]["model_id"]
    model_b_id = random_task["responses"][1]["model_id"]

    q.client.model_names = {
        f"{str(model_a_id)}": random_task["responses"][0]["model_name"],
        f"{str(model_b_id)}": random_task["responses"][1]["model_name"],
    }

    model_a_response = random_task["responses"][0]["response_text"]
    model_b_response = random_task["responses"][1]["response_text"]

    # Done ...

    q.page["meta"].dialog = None

    q.page["model_a"] = get_response_card(
        title="Model A", content=model_a_response, box="model_left"
    )
    q.page["model_b"] = get_response_card(
        title="Model B", content=model_b_response, box="model_right"
    )
    q.page["actions"] = get_ab_test_mini_buttons(
        model_a=model_a_id,
        model_b=model_b_id,
    )

    q.page["prompt"] = get_prompt_card(
        prompt=prompt_text,  # type: ignore
        model_a=model_a_id,
        model_b=model_b_id,
    )

    await q.page.save()


@on()
async def ab_test(q: Q):
    q.page["side_nav"].value = "ab_test"

    if q.client.current_layout != "ab_test":
        q.page["meta"] = get_meta(q)
        q.client.current_layout = "ab_test"

    del q.page["admin_users"]
    del q.page["admin_models"]
    del q.page["admin_ab_tests"]
    del q.page["admin_prompts"]

    del q.page["model_elo_leaderboard"]
    del q.page["user_leaderboard"]

    await load_ab_test(q)


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


@on()
async def ab_test_result(q: Q):
    q.page["meta"].dialog = get_loading_dialog()
    await q.page.save()

    submitted_by = UUID(q.user.user_id)

    now = datetime.now(tz=timezone.utc)

    if q.args.ab_test_result is not None and q.args.ab_test_result in [
        "tie",
        "both_bad",
    ]:
        selected_model = None
        other_response = q.args.ab_test_result
    else:
        if q.args.ab_test_result is not None:
            selected_model = UUID(q.args.ab_test_result)
        else:
            selected_model = None

        other_response = None

    eval_by_human_id = await insert_eval_by_human_into_db(
        ab_test_id=q.client.ab_test_id,
        prompt_id=q.client.prompt_id,
        submitted_by=submitted_by,
        submitted_at=now,
        selected_model=selected_model,
        other_response=other_response,
        flags=q.args.flags,
        additional_feedback=q.args.additional_feedback,
    )

    logger.info(f"eval_by_human_id: {eval_by_human_id}")
    q.page["meta"].dialog = None

    model_a_name, model_b_name = list(q.client.model_names.values())

    q.page["model_a"].items[0] = ui.text_l(f"Model A: {model_a_name.split('/')[-1]}")
    q.page["model_b"].items[0] = ui.text_l(f"Model B: {model_b_name.split('/')[-1]}")

    q.page["actions"].items[0].inline.items[3].button.disabled = True
    q.page["actions"].items[0].inline.items[5].button.disabled = True
    q.page["actions"].items[0].inline.items[7].button.disabled = True
    q.page["actions"].items[0].inline.items[9].button.disabled = True

    if (
        q.args.ab_test_result is not None
        and q.client.model_names.get(q.args.ab_test_result) == model_a_name
    ):
        q.page["actions"].items[0].inline.items[3].button.primary = True
    elif (
        q.args.ab_test_result is not None
        and q.client.model_names.get(q.args.ab_test_result) == model_b_name
    ):
        q.page["actions"].items[0].inline.items[5].button.primary = True
    elif q.args.ab_test_result == "tie":
        q.page["actions"].items[0].inline.items[7].button.primary = True
    elif q.args.ab_test_result == "both_bad":
        q.page["actions"].items[0].inline.items[9].button.primary = True

    q.client.model_names = None
    q.client.prompt_id = None
    q.client.ab_test_id = None

    await q.page.save()


@on()
async def next_ab_test(q: Q):
    # Loading ....

    q.page["meta"].dialog = get_loading_dialog()
    await q.page.save()

    random_task = await get_random_ab_task_for_user_no_repeat_v1(
        llm_user_id=UUID(q.user.user_id)
    )
    if not random_task:
        q.page["meta"].dialog = None
        await q.page.save()
        return

    q.client.prompt_id = random_task["prompt_id"]  # type: ignore
    q.client.ab_test_id = random_task["ab_test_id"]  # type: ignore

    prompt_text = random_task["prompt_text"]  # type: ignore
    model_a_id = random_task["responses"][0]["model_id"]
    model_b_id = random_task["responses"][1]["model_id"]

    q.client.model_names = {
        f"{str(model_a_id)}": random_task["responses"][0]["model_name"],
        f"{str(model_b_id)}": random_task["responses"][1]["model_name"],
    }

    model_a_response = random_task["responses"][0]["response_text"]
    model_b_response = random_task["responses"][1]["response_text"]

    # Done ...

    q.page["meta"].dialog = None

    q.page["model_a"].items[0] = ui.text_xl("Model A")
    q.page["model_b"].items[0] = ui.text_xl("Model B")

    q.page["model_a"].items[2].text.content = model_a_response
    q.page["model_b"].items[2].text.content = model_b_response

    q.page["actions"].items[0].inline.items[3].button.disabled = False
    q.page["actions"].items[0].inline.items[5].button.disabled = False
    q.page["actions"].items[0].inline.items[7].button.disabled = False
    q.page["actions"].items[0].inline.items[9].button.disabled = False

    q.page["actions"].items[0].inline.items[3].button.primary = False
    q.page["actions"].items[0].inline.items[5].button.primary = False
    q.page["actions"].items[0].inline.items[7].button.primary = False
    q.page["actions"].items[0].inline.items[9].button.primary = False

    q.page["actions"].items[0].inline.items[3].button.value = str(model_a_id)
    q.page["actions"].items[0].inline.items[5].button.value = str(model_b_id)

    q.page["prompt"].items[1].text.content = f"**{prompt_text}**"

    await q.page.save()


@on()
async def admin_prompts_v1(q: Q):
    q.page["side_nav"].value = "admin_prompts_v1"

    if q.client.current_layout != "admin":
        set_full_page_layout(q)
        q.client.current_layout = "admin"

    # Loading ....
    del q.page["model_a"]
    del q.page["model_b"]
    del q.page["prompt"]

    del q.page["admin_models"]
    del q.page["admin_users"]
    del q.page["admin_ab_tests"]

    del q.page["user_leaderboard"]
    del q.page["model_elo_leaderboard"]

    q.page["meta"].dialog = get_loading_dialog()
    await q.page.save()

    prompt_rows = await get_all_prompts_v1_with_tags()
    prompts = []
    for r in prompt_rows:
        prompts.append(r)

    q.page["meta"].dialog = None

    admin_prompts_table = get_admin_prompts_table(prompts=prompts)
    q.page["admin_prompts"] = ui.form_card(
        box=ui.box("main"),
        items=[
            ui.text_xl("Prompts"),
            admin_prompts_table,
        ],
    )
    await q.page.save()


@on()
async def eval_method(q: Q):
    q.page["side_nav"].value = "eval_method"
    if q.client.current_layout != "admin":
        set_full_page_layout(q)
        q.client.current_layout = "admin"

    # Loading ....
    del q.page["model_a"]
    del q.page["model_b"]
    del q.page["prompt"]

    del q.page["admin_models"]
    del q.page["admin_users"]
    del q.page["admin_ab_tests"]
    del q.page["admin_prompts"]

    del q.page["model_elo_leaderboard"]

    del q.page["user_leaderboard"]

    q.page["meta"].dialog = None

    q.page["model_elo_leaderboard"] = ui.form_card(
        box=ui.box("main"),
        items=[
            ui.text(content),
            ui.text(references),
            ui.expander(
                name="elo_lb_system_prompt_expander",
                expanded=False,
                items=[
                    ui.text(system_prompt_and_api_call),
                ],
            ),
        ],
    )

    await q.page.save()


@on()
async def model_elo_leaderboard(q: Q):
    q.page["side_nav"].value = "model_elo_leaderboard"
    if q.client.current_layout != "admin":
        set_full_page_layout(q)
        q.client.current_layout = "admin"

    # Loading ....
    del q.page["model_a"]
    del q.page["model_b"]
    del q.page["prompt"]

    del q.page["admin_models"]
    del q.page["admin_users"]
    del q.page["admin_ab_tests"]
    del q.page["admin_prompts"]

    del q.page["user_leaderboard"]

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


@on()
async def admin_responses(q: Q):
    if q.client.current_layout != "admin_responses":
        layouts = [
            ui.layout(
                breakpoint="xs",
                min_height="100vh",
                zones=get_zones4(),
            ),
        ]
        q.page["meta"] = get_meta(q, layouts=layouts)
        q.client.current_layout = "admin_responses"

    q.page["side_nav"].value = "admin_responses"

    # Loading ....
    del q.page["model_a"]
    del q.page["model_b"]
    del q.page["prompt"]
    del q.page["actions"]

    del q.page["admin_users"]
    del q.page["admin_prompts"]
    del q.page["admin_models"]
    del q.page["admin_ab_tests"]
    del q.page["admin_auto_evals"]

    del q.page["user_leaderboard"]
    del q.page["model_elo_leaderboard"]

    q.page["meta"].dialog = get_loading_dialog()
    await q.page.save()

    active_model_rows = await get_all_model_names_ids()
    q.client.models = {}
    for r in active_model_rows:
        m = dict(
            model_id=r[0],
            model_name=r[1],
        )
        q.client.models[str(m["model_id"])] = m

    q.client.selected_model_ids = list(q.client.models.keys())

    if len(q.client.selected_model_ids) >= 2:
        q.client.selected_model_ids_eval = q.client.selected_model_ids[:2]
    else:
        q.client.selected_model_ids_eval = q.client.selected_model_ids

    prompt_rows = await get_all_prompts_sha_v1(benchmark_name="v1")

    prompts = {}
    prompts_sha = {}
    for r in prompt_rows:
        p = dict(
            prompt_id=str(r[0]),
            prompt_text=r[1],
            prompt_sha=r[2],
        )
        prompts[str(p["prompt_id"])] = p
        prompts_sha[p["prompt_sha"]] = p

    q.client.prompt_ids = list(prompts.keys())
    q.client.prompts = prompts
    q.client.prompts_sha = prompts_sha

    q.client.current_prompt_idx = 0
    q.client.selected_prompt_id = q.client.prompt_ids[q.client.current_prompt_idx]

    q.client.eval_model_name = "gpt-4-0613"
    q.client.eval_model_id = UUID("10596d4c-4bbe-4287-b781-c4f04a13ab5d")

    q.page["prompt"] = get_prompt_model_selection_card(q)
    await make_model_response_cards(q)

    q.page["meta"].dialog = None
    await q.page.save()


@on()
async def select_new_prompt(q: Q):
    q.page["meta"].dialog = ui.dialog(
        title="Select New Prompt",
        closable=False,
        blocking=True,
        width="900px",
        items=[
            ui.combobox(
                name="selected_prompt_text",
                width="800px",
                choices=[v["prompt_text"] for v in q.client.prompts.values()],
                trigger=False,
                value=q.client.prompts[q.client.selected_prompt_id]["prompt_text"],
            ),
            ui.text_xl(WhiteSpace.em),
            ui.buttons(
                justify="end",
                items=[
                    ui.button(name="close_dialog", label="Close"),
                    ui.button(name="select_new_prompt_now", label="Save", primary=True),
                ],
            ),
        ],
    )
    await q.page.save()


@on()
async def select_models_to_compare(q: Q):
    q.page["meta"].dialog = ui.dialog(
        title="Select Models",
        closable=False,
        blocking=True,
        items=[
            ui.checklist(
                name="selected_model_ids",
                label="Select Models",
                values=q.client.selected_model_ids,
                choices=[
                    ui.choice(name=k, label=v["model_name"].split("/")[-1])
                    for k, v in q.client.models.items()
                ],
            ),
            ui.buttons(
                justify="end",
                items=[
                    ui.button(name="close_dialog", label="Close"),
                    ui.button(
                        name="select_models_to_compare_now", label="Save", primary=True
                    ),
                ],
            ),
        ],
    )
    await q.page.save()


@on()
async def select_models_to_compare_now(q: Q):
    num_max_models = 10

    if q.args.selected_model_ids:
        q.client.selected_model_ids = q.args.selected_model_ids[
            : min(num_max_models, len(q.args.selected_model_ids))
        ]

    q.page["meta"].dialog = get_loading_dialog()
    await q.page.save()

    await make_model_response_cards(q)

    q.page["meta"].dialog = None
    await q.page.save()


@on()
async def select_new_prompt_now(q: Q):
    prompt_text = q.args.selected_prompt_text

    q.page["meta"].dialog = get_loading_dialog()
    await q.page.save()

    prompt_sha = get_sha256(prompt_text)

    selected_prompt = q.client.prompts_sha[prompt_sha]
    selected_prompt_text = selected_prompt["prompt_text"]

    assert selected_prompt_text == prompt_text

    q.client.selected_prompt_id = selected_prompt["prompt_id"]
    q.client.current_prompt_idx = q.client.prompt_ids.index(q.client.selected_prompt_id)

    q.page["prompt"] = get_prompt_model_selection_card(q)
    await make_model_response_cards(q)

    q.page["meta"].dialog = None
    await q.page.save()


@on()
async def show_next_prompt(q: Q):
    q.client.current_prompt_idx = min(
        len(q.client.prompt_ids) - 1, q.client.current_prompt_idx + 1
    )
    q.client.selected_prompt_id = q.client.prompt_ids[q.client.current_prompt_idx]

    q.page["meta"].dialog = get_loading_dialog()
    await q.page.save()

    q.page["prompt"] = get_prompt_model_selection_card(q)
    await make_model_response_cards(q)

    q.page["meta"].dialog = None
    await q.page.save()


@on()
async def show_previous_prompt(q: Q):
    q.client.current_prompt_idx = max(0, q.client.current_prompt_idx - 1)
    q.client.selected_prompt_id = q.client.prompt_ids[q.client.current_prompt_idx]

    q.page["meta"].dialog = get_loading_dialog()
    await q.page.save()

    q.page["prompt"] = get_prompt_model_selection_card(q)
    await make_model_response_cards(q)

    q.page["meta"].dialog = None
    await q.page.save()


@on()
async def show_gpt_eval(q: Q):
    q.page["meta"].dialog = ui.dialog(
        title="GPT Eval",
        closable=False,
        blocking=True,
        items=[
            ui.dropdown(
                name="model_a",
                label="Model A",
                value=q.client.selected_model_ids[0],
                choices=[
                    ui.choice(name=k, label=v["model_name"].split("/")[-1])
                    for k, v in q.client.models.items()
                    if k in q.client.selected_model_ids
                ],
            ),
            ui.dropdown(
                name="model_b",
                label="Model B",
                value=q.client.selected_model_ids[1],
                choices=[
                    ui.choice(name=k, label=v["model_name"].split("/")[-1])
                    for k, v in q.client.models.items()
                    if k in q.client.selected_model_ids
                ],
            ),
            ui.separator(),
            ui.buttons(
                justify="end",
                items=[
                    ui.button(name="close_dialog", label="Close", primary=False),
                    ui.button(
                        name="show_gpt_eval_now", label="Show GPT Eval", primary=True
                    ),
                ],
            ),
        ],
    )
    await q.page.save()


@on()
async def show_gpt_eval_now(q: Q):
    model_a = q.args.model_a
    model_b = q.args.model_b

    if model_a == model_b:
        q.page["meta"].dialog = ui.dialog(
            title="GPT Eval",
            closable=False,
            blocking=True,
            items=[
                ui.text("Model A and Model B must be different"),
                ui.text_xl(WhiteSpace.em),
                ui.buttons(
                    justify="end",
                    items=[
                        ui.button(name="close_dialog", label="Close", primary=True),
                    ],
                ),
            ],
        )
        await q.page.save()
        return

    ab_test_id, *_ = await get_ab_test_by_model_ids(
        model_a=UUID(model_a),
        model_b=UUID(model_b),
    )

    gpt_eval, *_ = await get_evals_by_model_for_eval_model_ab_test_prompt(
        ab_test_id=ab_test_id,
        prompt_id=q.client.selected_prompt_id,
    )

    model_a_name = gpt_eval.get("model_a_name").split("/")[-1]
    model_b_name = gpt_eval.get("model_b_name").split("/")[-1]
    winner = gpt_eval.get("winner").split("/")[-1]

    q.page["meta"].dialog = ui.dialog(
        title="GPT Eval",
        closable=False,
        blocking=True,
        width="700px",
        items=[
            ui.label("Model A:"),
            ui.text(model_a_name),
            ui.text_xl(WhiteSpace.em),
            ui.label("Model B:"),
            ui.text(model_b_name),
            ui.text_xl(WhiteSpace.em),
            ui.label("Winner:"),
            ui.text(winner),
            ui.text_xl(WhiteSpace.em),
            ui.label("Model A Score:"),
            ui.text(str(gpt_eval.get("model_a_score"))),
            ui.text_xl(WhiteSpace.em),
            ui.label("Model B Score:"),
            ui.text(str(gpt_eval.get("model_b_score"))),
            ui.text_xl(WhiteSpace.em),
            ui.label("Reason:"),
            ui.text(gpt_eval.get("reason")),
            ui.text_xl(WhiteSpace.em),
            ui.separator(),
            ui.buttons(
                justify="end",
                items=[
                    ui.button(name="close_dialog", label="Close", primary=True),
                ],
            ),
        ],
    )
    await q.page.save()
