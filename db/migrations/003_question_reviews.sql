CREATE TABLE IF NOT EXISTS question_reviews (
    review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NULL REFERENCES ai_runs(run_id) ON DELETE SET NULL,
    run_item_id UUID NULL REFERENCES ai_run_items(run_item_id) ON DELETE SET NULL,
    question_text TEXT NOT NULL,
    language VARCHAR(16) NOT NULL,
    decision TEXT NOT NULL,
    reviewer TEXT NULL,
    comments TEXT NULL,
    decision_metadata JSONB NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_question_reviews_run ON question_reviews(run_id);
CREATE INDEX IF NOT EXISTS idx_question_reviews_run_item ON question_reviews(run_item_id);
CREATE INDEX IF NOT EXISTS idx_question_reviews_decision ON question_reviews(decision);
