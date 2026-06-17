import asyncio


def test_intent_analyzer_employment(intent_service):
    result = asyncio.run(intent_service.analyze(type("Req", (), {"prompt": "Employment survey", "language": "en"})()))
    assert result.intent.value in {"topic_scope", "question_request"}
    assert "employment" in result.topics


def test_intent_analyzer_tamil_employment(intent_service):
    result = asyncio.run(intent_service.analyze(type("Req", (), {"prompt": "வேலைவாய்ப்பு கணக்கெடுப்பு", "language": "ta"})()))
    assert result.topics == ["employment"]
