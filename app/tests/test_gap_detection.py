import asyncio


def test_gap_detection_missing_migration(gap_service):
    retrieved = [{"category": "employment", "text": "What is your occupation?"}]
    gaps = asyncio.run(gap_service.detect("Please add migration related questions", retrieved))
    assert "migration" in gaps
