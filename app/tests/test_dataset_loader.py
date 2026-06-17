import json
from pathlib import Path


def test_multilingual_dataset_contains_required_topics(multilingual_dataset):
    categories = {item["category"] for item in multilingual_dataset}
    assert {"employment", "education", "health", "agriculture", "migration"}.issubset(categories)


def test_fixture_file_exists():
    path = Path(__file__).resolve().parent / "fixtures" / "multilingual_questions.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data
