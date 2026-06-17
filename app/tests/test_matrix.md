# Test Matrix

| ID | Scenario | Type | Expected Result |
|---|---|---|---|
| UT-01 | Intent Analyzer detects employment | Unit | topic_scope/question_request with employment topic |
| UT-02 | Retrieval returns top-k and filters | Unit | semantic results with metadata |
| UT-03 | Duplicate detection flags similar question | Unit | duplicate candidate returned |
| UT-04 | Gap detection identifies missing migration | Unit | `migration` gap returned |
| UT-05 | Qwen invalid JSON repair/retry | Unit | repaired output accepted |
| UT-06 | Validation rejects low quality question | Unit | rejected with reasons |
| UT-07 | Approval service writes review ledger entry | Unit | approval record created |
| UT-08 | Audit service start/add/finish | Unit | repository writes recorded |
| IT-01 | Ingestion -> embedding -> storage | Integration | question + embedding persisted |
| IT-02 | Embedding -> retrieval | Integration | multilingual retrieval works |
| IT-03 | Retrieval -> gap detection | Integration | missing topic list returned |
| IT-04 | Gap -> generation | Integration | generated questions only for gaps |
| IT-05 | Generation -> validation | Integration | accepted/rejected split |
| IT-06 | Validation -> approval | Integration | approval review ledger entry created |
| E2E-01 | Employment prompt retrieves employment questions | E2E | employment question returned |
| E2E-02 | Tamil employment prompt retrieves English questions | E2E | cross-lingual retrieval works |
| E2E-03 | Duplicate detection works | E2E | duplicate candidate returned |
| E2E-04 | Gap detection identifies migration | E2E | `migration` gap returned |
| E2E-05 | Qwen generates only missing-topic questions | E2E | generation uses gaps only |
| E2E-06 | Invalid Qwen output triggers retry | E2E | repaired or empty after retries |
| E2E-07 | Validation rejects low quality questions | E2E | rejected items returned |
| E2E-08 | Generated questions enter pending_review | E2E | `pending_review` present |
| E2E-09 | Admin approval creates ledger entry | E2E | review entry stored |
| E2E-10 | Audit trail contains every stage | E2E | all run stages recorded |
| FT-01 | Database unavailable | Failure | graceful error + audit failure |
| FT-02 | Missing embeddings | Failure | validation failure surfaced |
| FT-03 | Invalid embeddings | Failure | ServiceError raised |
| FT-04 | Qwen timeout | Failure | error surfaced + audit failure |
| FT-05 | Invalid JSON | Failure | retry then empty/failure |
| FT-06 | Validation failures | Failure | rejected item returned |
| FT-07 | Audit write failures | Failure | error surfaced |
