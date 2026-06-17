ALTER TABLE ai_runs
    ADD COLUMN IF NOT EXISTS run_status TEXT NULL,
    ADD COLUMN IF NOT EXISTS started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ADD COLUMN IF NOT EXISTS finished_at TIMESTAMPTZ NULL,
    ADD COLUMN IF NOT EXISTS duration_ms INTEGER NULL,
    ADD COLUMN IF NOT EXISTS request_id TEXT NULL,
    ADD COLUMN IF NOT EXISTS trace_id TEXT NULL,
    ADD COLUMN IF NOT EXISTS input_metadata JSONB NULL,
    ADD COLUMN IF NOT EXISTS output_metadata JSONB NULL;

CREATE INDEX IF NOT EXISTS idx_ai_runs_status ON ai_runs(run_status);
CREATE INDEX IF NOT EXISTS idx_ai_runs_request_id ON ai_runs(request_id);

ALTER TABLE ai_run_items
    ADD COLUMN IF NOT EXISTS stage TEXT NULL,
    ADD COLUMN IF NOT EXISTS item_type TEXT NULL,
    ADD COLUMN IF NOT EXISTS status TEXT NULL,
    ADD COLUMN IF NOT EXISTS reason TEXT NULL;

CREATE INDEX IF NOT EXISTS idx_ai_run_items_stage ON ai_run_items(stage);
CREATE INDEX IF NOT EXISTS idx_ai_run_items_status ON ai_run_items(status);
