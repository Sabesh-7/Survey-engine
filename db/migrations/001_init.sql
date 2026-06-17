CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'question_source') THEN
        CREATE TYPE question_source AS ENUM ('standard', 'historical', 'ai_generated', 'manual');
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS question_groups (
    question_group_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_label TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS questions (
    question_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_group_id UUID NULL REFERENCES question_groups(question_group_id),
    canonical_question_id UUID NULL REFERENCES questions(question_id),
    text TEXT NOT NULL,
    language VARCHAR(16) NOT NULL,
    category VARCHAR(128) NULL,
    source question_source NOT NULL,
    source_reference TEXT NULL,
    created_by TEXT NULL,
    confidence_score REAL NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_questions_language ON questions(language);
CREATE INDEX IF NOT EXISTS idx_questions_source ON questions(source);
CREATE INDEX IF NOT EXISTS idx_questions_category ON questions(category);
CREATE INDEX IF NOT EXISTS idx_questions_group ON questions(question_group_id);

CREATE TABLE IF NOT EXISTS question_versions (
    question_version_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    text TEXT NOT NULL,
    language VARCHAR(16) NOT NULL,
    changed_by TEXT NULL,
    change_reason TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (question_id, version_number)
);

CREATE INDEX IF NOT EXISTS idx_question_versions_question ON question_versions(question_id);

CREATE TABLE IF NOT EXISTS question_embeddings (
    embedding_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    model_name TEXT NOT NULL,
    embedding vector(1024) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (question_id, model_name)
);

CREATE INDEX IF NOT EXISTS idx_question_embeddings_question ON question_embeddings(question_id);
CREATE INDEX IF NOT EXISTS idx_question_embeddings_vector ON question_embeddings USING hnsw (embedding vector_cosine_ops);

CREATE TABLE IF NOT EXISTS question_classifications (
    classification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    tag TEXT NULL,
    classification_code TEXT NULL,
    source TEXT NULL,
    confidence_score REAL NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_question_classifications_question ON question_classifications(question_id);
CREATE INDEX IF NOT EXISTS idx_question_classifications_code ON question_classifications(classification_code);

CREATE TABLE IF NOT EXISTS question_duplicates (
    duplicate_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    duplicate_question_id UUID NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    similarity_score REAL NOT NULL,
    method TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (question_id, duplicate_question_id)
);

CREATE INDEX IF NOT EXISTS idx_question_duplicates_question ON question_duplicates(question_id);
CREATE INDEX IF NOT EXISTS idx_question_duplicates_candidate ON question_duplicates(duplicate_question_id);
CREATE INDEX IF NOT EXISTS idx_question_duplicates_score ON question_duplicates(similarity_score);

CREATE TABLE IF NOT EXISTS surveys (
    survey_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    version TEXT NULL,
    language VARCHAR(16) NULL,
    source TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_surveys_name ON surveys(name);

CREATE TABLE IF NOT EXISTS survey_questions (
    survey_question_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    survey_id UUID NOT NULL REFERENCES surveys(survey_id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    is_required BOOLEAN NOT NULL DEFAULT TRUE,
    metadata JSONB NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (survey_id, question_id)
);

CREATE INDEX IF NOT EXISTS idx_survey_questions_survey ON survey_questions(survey_id);
CREATE INDEX IF NOT EXISTS idx_survey_questions_question ON survey_questions(question_id);

CREATE TABLE IF NOT EXISTS ai_runs (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_type TEXT NOT NULL,
    prompt TEXT NULL,
    language VARCHAR(16) NULL,
    model_name TEXT NULL,
    metadata JSONB NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ai_runs_type ON ai_runs(run_type);
CREATE INDEX IF NOT EXISTS idx_ai_runs_created_at ON ai_runs(created_at);

CREATE TABLE IF NOT EXISTS ai_run_items (
    run_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES ai_runs(run_id) ON DELETE CASCADE,
    question_id UUID NULL REFERENCES questions(question_id) ON DELETE SET NULL,
    score REAL NULL,
    payload JSONB NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ai_run_items_run ON ai_run_items(run_id);
CREATE INDEX IF NOT EXISTS idx_ai_run_items_question ON ai_run_items(question_id);
