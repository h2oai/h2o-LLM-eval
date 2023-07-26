from .prompt_templates import SYSTEM_PROMPT, USER_PROMPT
import json
import datetime


def db_game_to_dict(row: tuple) -> dict:
    return {
        "ab_test_id": row[0],
        "model_a": row[1],
        "model_b": row[2],
        "model_a_id": row[3],
        "model_a_name": row[4],
        "model_b_id": row[5],
        "model_b_name": row[6],
        "response_a_id": row[7],
        "response_a_text": row[8],
        "response_b_id": row[9],
        "response_b_text": row[10],
        "prompt_id": row[11],
        "prompt_text": row[12],
        "eval_model_id": row[13],
        "eval_model_name": row[14],
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


def parse_result_to_battle(result: tuple[dict], games_lookup: dict) -> dict:
    input, output = result
    game_id = input["user"]
    game = games_lookup[game_id]

    eval_model_name = input["model"]
    tstamp = output["created"]

    output_text = output["choices"][0]["message"]["content"]
    output_json = json.loads(output_text, strict=False)

    model_a = game["model_a_name"]
    model_b = game["model_b_name"]

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

    try:
        prompt_tokens = output["usage"]["prompt_tokens"]
        response_tokens = output["usage"]["completion_tokens"]
    except KeyError as e:
        print(e, output.keys())
        if "usage" in output:
            print(output["usage"].keys())
        prompt_tokens = None
        response_tokens = None

    return {
        "game_id": game_id,
        "eval_model_name": eval_model_name,
        'model_a': model_a,
        'model_b': model_b,
        'win': winner,
        'score_a': score_a,
        'score_b': score_b,
        'other_response': None,
        'additional_feedback': reason,
        'prompt_tokens': prompt_tokens,
        'response_tokens': response_tokens,
        'submitted_at': tstamp,
    }


def battle_to_eval_entry(battle: dict, games_lookup: dict) -> dict:
    game = games_lookup[battle["game_id"]]
    eval_entry = {
        "ab_test_id": game["ab_test_id"],
        "model_a": game["model_a_id"],
        "model_b": game["model_b_id"],
        "prompt_id": game["prompt_id"],
        "submitted_by": game["eval_model_id"],
        "selected_model": game["model_a_id"] if battle["win"] == game["model_a_name"] else game["model_b_id"],
        "other_response": battle["other_response"],
        "additional_feedback": battle["additional_feedback"],
        "prompt_tokens": battle["prompt_tokens"],
        "response_tokens": battle["response_tokens"],
        "model_a_score": battle["score_a"],
        "model_b_score": battle["score_b"],
        "best_answer": None,
        "submitted_at": datetime.datetime.fromtimestamp(battle["submitted_at"]),
    }
    return eval_entry

