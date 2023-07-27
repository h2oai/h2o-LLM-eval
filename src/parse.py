from .prompt_templates import SYSTEM_PROMPT, USER_PROMPT
import json
import datetime


def db_game_to_dict(row: tuple) -> dict:
    return {
        "ab_test_id": row[0],
        "model_a_id": row[1],
        "model_b_id": row[2],
        "response_a_id": row[3],
        "response_a_text": row[4],
        "response_b_id": row[5],
        "response_b_text": row[6],
        "prompt_id": row[7],
        "prompt_text": row[8],
        "eval_model_id": row[9],
        "eval_model_name": row[10],
    }


def construct_request(game: dict) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT.format(
                question=game["prompt_text"],
                model_a_response=game["response_a_text"],
                model_b_response=game["response_b_text"]
            )
         }
    ]
    request = {
        "model": game["eval_model_name"],
        "messages": messages,
        "user": str(game["ab_test_id"]) + "_" + str(game["prompt_id"]),
        "temperature": 0.2,
        "max_tokens": 1024,
    }
    return request


def games_list_to_lookup(games: list[dict]) -> dict:
    lookup = {}
    for game in games:
        key = str(game["ab_test_id"]) + "_" + str(game["prompt_id"])
        lookup[key] = game
    return lookup


def parse_result_to_eval_entry(result: tuple[dict], games_lookup: dict) -> dict:
    input, output = result
    game_id = input["user"]
    game = games_lookup[game_id]

    tstamp = output["created"]

    output_text = output["choices"][0]["message"]["content"]
    output_json = json.loads(output_text, strict=False)

    model_a = game["model_a_id"]
    model_b = game["model_b_id"]

    winner = output_json["choice"]
    if winner == "model_a":
        winner = model_a
    elif winner == "model_b":
        winner = model_b
    else:
        raise ValueError(f"Unknown winner {winner}")

    try:
        score_a = output_json["scores"]["model_a"]
        score_b = output_json["scores"]["model_b"]
    except KeyError as e:
        print(e, output_json.keys())
        score_a = None
        score_b = None

    reason = output_json.get("reason")

    return {
        "ab_test_id": game["ab_test_id"],
        "model_a": game["model_a_id"],
        "model_b": game["model_b_id"],
        "prompt_id": game["prompt_id"],
        "submitted_by": game["eval_model_id"],
        "selected_model": winner,
        "additional_feedback": reason,
        "model_a_score": score_a,
        "model_b_score": score_b,
        "submitted_at": datetime.datetime.fromtimestamp(tstamp),
    }


def db_battle_to_dict(db_battle: list[tuple]) -> dict:
    battle = {
        'model_a': db_battle[0],
        'model_b': db_battle[1],
        'win': db_battle[2],
        'tstamp': db_battle[3],
    }
    return battle

