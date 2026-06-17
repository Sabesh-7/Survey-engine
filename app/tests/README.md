# Test Execution

Run the full suite:

```bash
pytest -q
```

Run a subset:

```bash
pytest -q app/tests/test_intent_analyzer.py
pytest -q app/tests/test_retrieval_service.py
pytest -q app/tests/test_generation_json_repair.py
```

If you have a real PostgreSQL database configured, export `DATABASE_URL` before running integration-style tests that are marked to use it.
