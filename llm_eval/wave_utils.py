from dataclasses import dataclass
from h2o_wave import Q, ui


async def ui_crash_card(q: Q, app_name, card_name, box):
    q.page[card_name] = ui.form_card(
        box=box,
        items=[
            ui.text_xl("Error!"),
            ui.text_l(
                "Sorry for the Inconvenience. "
                f"Please refresh your browser to restart {app_name}."
            ),
        ],
    )
    await q.page.save()


async def handle_crash(q: Q):
    # Keep this code very minimal.
    # Errors in this code will show stack traces in the UI.
    # Check and avoid error in this code.

    # Remove the existing page
    q.page.drop()

    # Redefine Meta Card with a single Zone
    q.page["meta"] = ui.meta_card(
        box="",
        title="H2O LLM Eval",
        layouts=[
            ui.layout(
                breakpoint="xs",
                width="1200px",
                zones=[
                    ui.zone("main"),
                ],
            )
        ],
    )

    # Create a Form Card to inform the user that something went wrong
    await ui_crash_card(
        q,
        app_name="H2O LLM Eval",
        card_name="__crash_card__",
        box="main",
    )


@dataclass
class WhiteSpace:
    # https://qwerty.dev/whitespace/
    zero_width: str = "​"
    hair: str = " "
    six_per_em: str = " "
    thin: str = " "
    punctuation: str = " "
    four_per_em: str = " "
    three_per_em: str = " "
    figure: str = " "
    en: str = " "
    em: str = " "
    braille: str = "⠀"


@dataclass
class WaveColors:
    amber: str = "#ffc107"
    azure: str = "#03a9f4"
    black: str = "#000"
    blue: str = "#2196f3"
    brown: str = "#795548"
    cyan: str = "#00bcd4"
    gray: str = "#9e9e9e"
    green: str = "#8bc34a"
    indigo: str = "#3f51b5"
    lime: str = "#cddc39"
    mint: str = "#4caf50"
    orange: str = "#ff9800"
    pink: str = "#e91e63"
    purple: str = "#9c27b0"
    red: str = "#f44336"
    tangerine: str = "#ff5722"
    teal: str = "#009688"
    violet: str = "#673ab7"
    white: str = "#fff"
    yellow: str = "#ffeb3b"
