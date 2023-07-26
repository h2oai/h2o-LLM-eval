import os
import random
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from psycopg.rows import dict_row

from .psql_utils import (
    PSQLConfig,
    insert_into,
    select_from,
)


async def get_random_prompt_v1():
    sql_select_from = """
    SELECT
        prompt_id,
        prompt_text
    FROM
        prompt_v1
        JOIN benchmark ON prompt_v1.benchmark_id = benchmark.benchmark_id
    WHERE
        benchmark.benchmark_name = 'v1'
    ORDER BY
        random()
    LIMIT
        1;
    """
    rows = await select_from(
        db_config=PSQLConfig.from_env(), sql_select_from=sql_select_from
    )
    return rows[0]


async def get_random_active_ab_test():
    sql_select_from = """
        SELECT
            ab_test_id,
            model_a,
            model_b
        FROM
            ab_test
        WHERE
            is_active is TRUE
        ORDER BY
            random()
        LIMIT
            1;
    """
    rows = await select_from(
        db_config=PSQLConfig.from_env(), sql_select_from=sql_select_from
    )
    if rows:
        return rows[0]


async def get_responses_for_models_prompt_v1(
    model_a: UUID, model_b: UUID, prompt_id: UUID
):
    sql_select_from = f"""
    SELECT
        response_temp_id,
        response_text,
        created_by_model,
        model_name,
        prompt_id
    FROM response_temp r
        JOIN model m ON r.created_by_model = m.model_id
    WHERE
        created_by_model IN ('{model_a}', '{model_b}')
        AND prompt_id = '{prompt_id}'
    ;
    """
    rows = await select_from(
        db_config=PSQLConfig.from_env(), sql_select_from=sql_select_from
    )
    return rows


async def get_random_prompt_ab_test_for_user_no_repeat_v1(llm_user_id: UUID):
    benchmark_id = os.getenv("V1_BENCHMARK_ID", "")
    sql_select_from = f"""
    WITH non_evaluated_combinations AS (
        SELECT
            prompt_v1.prompt_id,
            ab_test.ab_test_id
        FROM
            prompt_v1
            CROSS JOIN ab_test
        WHERE
            ab_test.is_active = TRUE
            AND prompt_v1.benchmark_id = '{benchmark_id}'
            AND NOT EXISTS (
                SELECT 1
                FROM eval_by_human
                WHERE eval_by_human.prompt_id = prompt_v1.prompt_id
                AND eval_by_human.ab_test_id = ab_test.ab_test_id
                AND eval_by_human.submitted_by = '{llm_user_id}'
            )
    )
    SELECT
        prompt_id,
        ab_test_id
    FROM
        non_evaluated_combinations
    ORDER BY
        RANDOM()
    LIMIT
        1
    ;
    """
    rows = await select_from(
        db_config=PSQLConfig.from_env(), sql_select_from=sql_select_from
    )
    if rows:
        return rows[0]


async def get_random_prompt_ab_test_v1():
    benchmark_id = os.getenv("V1_BENCHMARK_ID", "")
    sql_select_from = f"""
    WITH all_combinations AS (
        SELECT
            prompt_v1.prompt_id,
            ab_test.ab_test_id
        FROM
            prompt_v1
            CROSS JOIN ab_test
        WHERE
            ab_test.is_active = TRUE
            AND prompt_v1.benchmark_id = '{benchmark_id}'
    )
    SELECT
        prompt_id,
        ab_test_id
    FROM
        all_combinations
    ORDER BY
        RANDOM()
    LIMIT
        1;
    """
    rows = await select_from(
        db_config=PSQLConfig.from_env(), sql_select_from=sql_select_from
    )
    return rows[0]


async def get_prompt_by_id_v1(prompt_id: UUID):
    sql_select_from = f"""
    SELECT
        prompt_id,
        prompt_text
    FROM
        prompt_v1
    WHERE
        prompt_id = '{prompt_id}'
    LIMIT
        1
    ;
    """
    rows = await select_from(
        db_config=PSQLConfig.from_env(), sql_select_from=sql_select_from
    )
    return rows[0]


async def get_ab_test_by_id(ab_test_id: UUID):
    sql_select_from = f"""
    SELECT
        ab_test_id,
        model_a,
        model_b,
        is_active
    FROM
        ab_test
    WHERE
        ab_test_id = '{ab_test_id}'
    LIMIT
        1
    ;
    """
    rows = await select_from(
        db_config=PSQLConfig.from_env(), sql_select_from=sql_select_from
    )
    return rows[0]


async def get_num_wins_by_model_prompt(model_id: UUID, prompt_id: UUID):
    sql_select_from = f"""
    SELECT
        COUNT(*) AS num_wins
    FROM
        eval_by_model ebm
    WHERE
        ebm.prompt_id = '{prompt_id}'
        AND ebm.selected_model = '{model_id}'
    ;
    """
    rows = await select_from(
        db_config=PSQLConfig.from_env(),
        sql_select_from=sql_select_from,
    )
    return rows[0][0]


async def get_num_games_by_model_prompt(model_id: UUID, prompt_id: UUID):
    sql_select_from = f"""
    SELECT
        COUNT(*) AS num_games
    FROM
        eval_by_model ebm
        JOIN ab_test abt ON ebm.ab_test_id = abt.ab_test_id
    WHERE
        ebm.prompt_id = '{prompt_id}'
        AND (abt.model_a = '{model_id}' OR abt.model_b = '{model_id}')
    ;
    """
    rows = await select_from(
        db_config=PSQLConfig.from_env(),
        sql_select_from=sql_select_from,
    )
    return rows[0][0]


async def get_responses_for_model_prompt_v1(model_id: UUID, prompt_id: UUID):
    sql_select_from = f"""
    SELECT
        response_temp_id,
        response_text,
        created_by_model,
        m.model_name,
        prompt_id,
        response_received_at
    FROM response_temp r
        JOIN model m ON r.created_by_model = m.model_id
    WHERE
        created_by_model = '{model_id}'
        AND prompt_id = '{prompt_id}'
    ;
    """
    rows = await select_from(
        db_config=PSQLConfig.from_env(), sql_select_from=sql_select_from
    )
    return rows[0]


async def get_elo_scores_new():
    sql_select_from = """
    SELECT
        model_id,
        model_name,
        model.hf_url AS model_hf_url,
        elo_score,
        license,
        elo_score_delta
    FROM
        model
    WHERE
        elo_score IS NOT NULL
        AND use_in_ab_tests IS TRUE
        AND show_on_public_elo_lb IS TRUE
    ORDER BY
        elo_score DESC
    ;
    """
    rows = await select_from(
        db_config=PSQLConfig.from_env(),
        sql_select_from=sql_select_from,
        row_factory=dict_row,
    )
    return rows


async def get_ab_test_by_model_ids(model_a: UUID, model_b: UUID):
    sql_select_from = f"""
    SELECT
        ab_test_id,
        model_a,
        model_b
    FROM
        ab_test
    WHERE
        (
            model_a = '{model_a}'
            AND model_b = '{model_b}'
        )
        OR (
            model_a = '{model_b}'
            AND model_b = '{model_a}'
        )
    LIMIT
        1;
    """
    rows = await select_from(
        db_config=PSQLConfig.from_env(), sql_select_from=sql_select_from
    )
    return rows[0]


async def get_all_model_names_ids():
    sql_select_from = """
    SELECT
        model_id,
        model_name,
        short_name
    FROM
        model
    WHERE
        use_in_ab_tests IS TRUE
    ;
    """
    rows = await select_from(
        db_config=PSQLConfig.from_env(), sql_select_from=sql_select_from
    )
    return rows


async def get_all_prompts_sha_v1(benchmark_name: str):
    sql_select_from = f"""
    SELECT
        prompt_id,
        prompt_text,
        prompt_sha256
    FROM
        prompt_v1
        JOIN benchmark ON prompt_v1.benchmark_id = benchmark.benchmark_id
    WHERE
        benchmark.benchmark_name = '{benchmark_name}'
    ;
    """
    rows = await select_from(
        db_config=PSQLConfig.from_env(), sql_select_from=sql_select_from
    )
    return rows


async def get_all_prompts_v1_with_tags():
    benchmark_id = os.getenv("V1_BENCHMARK_ID", "")
    sql_select_from = f"""
    SELECT
        prompt_id,
        prompt_text,
        categories,
        tags,
        difficulty
    FROM
        prompt_v1
    WHERE
        benchmark_id = '{benchmark_id}'
    ;
    """
    rows = await select_from(
        db_config=PSQLConfig.from_env(),
        sql_select_from=sql_select_from,
        row_factory=dict_row,
    )
    return rows


async def get_evals_by_model_for_eval_model_ab_test_prompt(
    ab_test_id: UUID,
    prompt_id: UUID,
):
    sql_select_from = f"""
    SELECT
        ebm.eval_by_model_id,
        ma.model_name AS model_a_name,
        mb.model_name AS model_b_name,
        sm.model_name AS winner,
        ebm.model_a_score,
        ebm.model_b_score,
        ebm.additional_feedback AS reason
    FROM
        eval_by_model ebm
        LEFT JOIN model sm ON ebm.selected_model = sm.model_id
        JOIN model ma ON ebm.model_a = ma.model_id
        JOIN model mb ON ebm.model_b = mb.model_id
    WHERE
        ebm.prompt_id = '{prompt_id}'
        AND ebm.ab_test_id = '{ab_test_id}'
    ;
    """
    rows = await select_from(
        db_config=PSQLConfig.from_env(),
        sql_select_from=sql_select_from,
        row_factory=dict_row,
    )
    return rows


async def get_random_ab_task_for_user():
    prompt_id, prompt_text = await get_random_prompt_v1()

    random_ab_test = await get_random_active_ab_test()

    if not random_ab_test:
        return

    dice = random.random()
    if dice < 0.5:
        ab_test_id, model_a, model_b = random_ab_test
    else:
        ab_test_id, model_b, model_a = random_ab_test

    responses = await get_responses_for_models_prompt_v1(
        model_a=model_a, model_b=model_b, prompt_id=prompt_id
    )
    response_list = []
    for r in responses:
        response_id, response_text, model_id, model_name, p_id = r
        x = dict(
            response_id=response_id,
            response_text=response_text,
            model_id=model_id,
            model_name=model_name,
            prompt_id=p_id,
        )
        response_list.append(x)

    random_task = dict(
        prompt_id=prompt_id,
        prompt_text=prompt_text,
        ab_test_id=ab_test_id,
        responses=response_list,
    )

    return random_task


async def get_random_ab_task_for_user_no_repeat_v1(llm_user_id: UUID):
    rand_row = await get_random_prompt_ab_test_for_user_no_repeat_v1(llm_user_id)
    if not rand_row:
        rand_row = await get_random_prompt_ab_test_v1()

    prompt_id, ab_test_id = rand_row

    prompt_id, prompt_text = await get_prompt_by_id_v1(prompt_id=prompt_id)

    random_ab_test = await get_ab_test_by_id(ab_test_id=ab_test_id)

    if not random_ab_test:
        return

    dice = random.random()
    if dice < 0.5:
        ab_test_id, model_a, model_b, is_active = random_ab_test
    else:
        ab_test_id, model_b, model_a, is_active = random_ab_test

    assert is_active

    responses = await get_responses_for_models_prompt_v1(
        model_a=model_a, model_b=model_b, prompt_id=prompt_id
    )
    response_list = []
    for r in responses:
        response_id, response_text, model_id, model_name, p_id = r
        x = dict(
            response_id=response_id,
            response_text=response_text,
            model_id=model_id,
            model_name=model_name,
            prompt_id=p_id,
        )
        response_list.append(x)

    random_task = dict(
        prompt_id=prompt_id,
        prompt_text=prompt_text,
        ab_test_id=ab_test_id,
        responses=response_list,
    )

    return random_task


async def insert_eval_by_human_into_db(
    ab_test_id: UUID,
    prompt_id: UUID,
    submitted_by: UUID,
    submitted_at: datetime,
    selected_model: Optional[UUID] = None,
    other_response: Optional[str] = None,
    flags: Optional[List[str]] = None,
    additional_feedback: Optional[str] = None,
) -> UUID:
    sql_insert_into = """
    INSERT INTO eval_by_human (
        eval_by_human_id,
        ab_test_id,
        prompt_id,
        submitted_by,
        selected_model,
        other_response,
        flags,
        additional_feedback,
        submitted_at
    )
    VALUES (
        %(eval_by_human_id)s,
        %(ab_test_id)s,
        %(prompt_id)s,
        %(submitted_by)s,
        %(selected_model)s,
        %(other_response)s,
        %(flags)s,
        %(additional_feedback)s,
        %(submitted_at)s
    );
    """
    eval_by_human_id = uuid4()
    values = dict(
        eval_by_human_id=eval_by_human_id,
        ab_test_id=ab_test_id,
        prompt_id=prompt_id,
        submitted_by=submitted_by,
        selected_model=selected_model,
        other_response=other_response,
        flags="#".join(flags) if flags else None,
        additional_feedback=additional_feedback,
        submitted_at=submitted_at,
    )
    await insert_into(
        db_config=PSQLConfig.from_env(), sql_insert_into=sql_insert_into, values=values
    )
    return eval_by_human_id


async def get_model_id_by_name(model_name: str) -> UUID:
    sql_select_from = f"""
    SELECT model_id FROM model WHERE model_name = '{model_name}' LIMIT 1;
    """
    rows = await select_from(
        db_config=PSQLConfig.from_env(), sql_select_from=sql_select_from
    )
    return rows[0][0]


async def get_all_unevaluated_ab_test_prompts_for_benchmark(benchmark_name: str, eval_model_name: str) -> list[dict]:
    sql_select_from = f"""
    SELECT
        ab.ab_test_id,
        ab.model_a,
        ab.model_b,
        ma.model_id,
        ma.model_name,
        mb.model_id,
        mb.model_name,
        ra.response_temp_id,
        ra.response_text,
        rb.response_temp_id,
        rb.response_text,
        p.prompt_text,
        em.model_id,
        em.model_name
    FROM
        ab_test AS ab
        JOIN model AS ma ON ab.model_a = ma.model_id
        JOIN model AS mb ON ab.model_b = mb.model_id
        CROSS JOIN prompt_v1 AS p
        JOIN response_temp AS ra ON ab.model_a = ra.created_by_model AND p.prompt_id = ra.prompt_id
        JOIN response_temp AS rb ON ab.model_b = rb.created_by_model AND p.prompt_id = rb.prompt_id
        JOIN benchmark AS b ON p.benchmark_id = b.benchmark_id
        CROSS JOIN model as em
    WHERE
        b.benchmark_name = 'v1'
        AND ma.use_in_ab_tests = TRUE
        AND mb.use_in_ab_tests = TRUE
        AND em.model_name = 'gpt-4-0613'
        AND NOT EXISTS (SELECT e.prompt_id, e.ab_test_id
                       FROM   eval_by_model AS e
                            JOIN model AS m ON e.submitted_by = m.model_id
                       WHERE  e.ab_test_id = ab.ab_test_id AND
                              e.prompt_id = p.prompt_id AND
                              e.submitted_by = em.model_id)
    
    """
    rows = await select_from(
        db_config=PSQLConfig.from_env(), sql_select_from=sql_select_from
    )
    return rows


async def insert_eval_by_model_into_db(
    ab_test_id: UUID,
    model_a: UUID,
    model_b: UUID,
    prompt_id: UUID,
    submitted_by: UUID,
    submitted_at: datetime,
    selected_model: Optional[UUID] = None,
    other_response: Optional[str] = None,
    additional_feedback: Optional[str] = None,
    prompt_tokens: Optional[int] = None,
    response_tokens: Optional[int] = None,
    model_a_score: Optional[int] = None,
    model_b_score: Optional[int] = None,
    best_answer: Optional[str] = None,
) -> UUID:
    sql_insert_into = """
    INSERT INTO eval_by_model (
        eval_by_model_id,
        ab_test_id,
        model_a,
        model_b,
        prompt_id,
        submitted_by,
        selected_model,
        other_response,
        additional_feedback,
        prompt_tokens,
        response_tokens,
        model_a_score,
        model_b_score,
        best_answer,
        submitted_at
    )
    VALUES (
        %(eval_by_model_id)s,
        %(ab_test_id)s,
        %(model_a)s,
        %(model_b)s,
        %(prompt_id)s,
        %(submitted_by)s,
        %(selected_model)s,
        %(other_response)s,
        %(additional_feedback)s,
        %(prompt_tokens)s,
        %(response_tokens)s,
        %(model_a_score)s,
        %(model_b_score)s,
        %(best_answer)s,
        %(submitted_at)s
    );
    """
    eval_by_model_id = uuid4()
    values = dict(
        eval_by_model_id=eval_by_model_id,
        ab_test_id=ab_test_id,
        model_a=model_a,
        model_b=model_b,
        prompt_id=prompt_id,
        submitted_by=submitted_by,
        selected_model=selected_model,
        other_response=other_response,
        additional_feedback=additional_feedback,
        prompt_tokens=prompt_tokens,
        response_tokens=response_tokens,
        model_a_score=model_a_score,
        model_b_score=model_b_score,
        best_answer=best_answer,
        submitted_at=submitted_at,
    )
    await insert_into(
        db_config=PSQLConfig.from_env(), sql_insert_into=sql_insert_into, values=values
    )
    return eval_by_model_id


async def is_eval_by_model_in_db(
    eval_model_id: UUID,
    prompt_id: UUID,
    ab_test_id: UUID,
) -> bool:
    sql_select_from = f"""
    SELECT
        *
    FROM
        eval_by_model
    WHERE
        submitted_by = '{eval_model_id}'
        AND prompt_id = '{prompt_id}'
        AND ab_test_id = '{ab_test_id}'
    LIMIT
        1;
    """
    rows = await select_from(db_config=PSQLConfig.from_env(), sql_select_from=sql_select_from)
    return True if rows else False

