CREATE TABLE IF NOT EXISTS model (
    model_id UUID PRIMARY KEY,
    model_name VARCHAR(255) NOT NULL,
    published_by VARCHAR(255) NOT NULL,
    license VARCHAR(255),
    model_url TEXT,
    elo_score FLOAT,
    elo_score_delta VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS prompt (
    prompt_id UUID PRIMARY KEY,
    prompt_text TEXT NOT NULL,
    prompt_sha256 VARCHAR(255) NOT NULL,
    categories JSONB,
    tags JSONB,
    difficulty VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS response (
    response_id UUID PRIMARY KEY,
    prompt_id UUID REFERENCES prompt(prompt_id) NOT NULL,
    created_by_model UUID REFERENCES model(model_id) NOT NULL,
    response_text TEXT NOT NULL,
    response_sha256 VARCHAR(255) NOT NULL,
    created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ab_test (
    ab_test_id UUID PRIMARY KEY,
    model_a UUID REFERENCES model(model_id) NOT NULL,
    model_b UUID REFERENCES model(model_id) NOT NULL
);

CREATE TABLE IF NOT EXISTS eval_by_model (
    eval_by_model_id UUID PRIMARY KEY,
    ab_test_id UUID REFERENCES ab_test NOT NULL,
    prompt_id UUID REFERENCES prompt(prompt_id) NOT NULL,
    submitted_by UUID REFERENCES model(model_id) NOT NULL,
    selected_model UUID REFERENCES model(model_id),
    additional_feedback TEXT,
    submitted_at TIMESTAMP NOT NULL,
    model_a UUID REFERENCES model(model_id) NOT NULL,
    model_b UUID REFERENCES model(model_id) NOT NULL,
    model_a_score FLOAT,
    model_b_score FLOAT
);

CREATE TABLE IF NOT EXISTS eval_by_human (
    eval_by_human_id UUID PRIMARY KEY,
    ab_test_id UUID REFERENCES ab_test NOT NULL,
    prompt_id UUID REFERENCES prompt(prompt_id) NOT NULL,
    selected_model UUID REFERENCES model(model_id),
    other_response VARCHAR(255),
    submitted_at TIMESTAMP NOT NULL
);