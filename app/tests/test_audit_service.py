from app.services.audit_service import AuditService


class Repo:
    def __init__(self) -> None:
        self.started = []
        self.items = []
        self.finished = []

    def start_run(self, **kwargs):
        self.started.append(kwargs)
        return type("Run", (), {"run_id": "run-1"})()

    def add_item(self, **kwargs):
        self.items.append(kwargs)

    def finish_run(self, **kwargs):
        self.finished.append(kwargs)


def test_audit_service_records_start_stage_finish():
    repo = Repo()
    service = AuditService(repo)

    run = service.start_run("recommendation", "prompt", "en", None, None, None, {"foo": "bar"})
    service.add_stage(run.run_id, "retrieval", "ok", {"retrieved": 1})
    service.finish_run(run.run_id, "completed", 12, {"done": True})

    assert repo.started[0]["run_type"] == "recommendation"
    assert repo.items[0]["stage"] == "retrieval"
    assert repo.finished[0]["run_status"] == "completed"
