# Survey Intelligence Engine Test Plan

## Scope
Validate the existing pipeline end-to-end without adding new product features:
Intent Analyzer -> Retrieval -> Duplicate Detection -> Gap Detection -> Qwen Generation -> Validation -> Approval -> Audit Trail.

## Test Layers

### Unit Tests
- Intent Analyzer
- Retrieval Service
- Duplicate Detection
- Gap Detection
- Question Generation
- Question Validation
- Question Approval Service
- Audit Service

### Integration Tests
- Question Ingestion -> Embedding -> Storage
- Embedding -> Retrieval
- Retrieval -> Gap Detection
- Gap Detection -> Generation
- Generation -> Validation
- Validation -> Approval Workflow

### End-to-End Tests
- Multilingual test data for employment, education, health, agriculture, migration
- English, Tamil, Hindi prompts
- Audit trail verification across the full recommendation pipeline

### Failure Tests
- Database unavailable
- Missing embeddings
- Invalid embeddings
- Qwen timeout
- Invalid JSON responses
- Validation failures
- Audit write failures

## Execution Strategy
- Use pytest and shared fixtures.
- Use real service implementations with fakes for external dependencies.
- Prefer deterministic fake embeddings and LLM outputs.
- Keep tests isolated and repeatable.
- Skip true Postgres-dependent integration cases if DATABASE_URL is unavailable.

## Expected Validation
- Generated questions remain `source=ai_generated` and `review_status=pending_review`.
- Rejected items include validation metadata and reasons.
- Approval decisions create review ledger entries.
- Audit trail captures every stage and run status.
