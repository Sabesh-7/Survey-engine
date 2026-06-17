from collections import defaultdict


class MetricsService:
    def __init__(self) -> None:
        self._counters: dict[str, int] = defaultdict(int)

    def incr(self, key: str, value: int = 1) -> None:
        self._counters[key] += value

    def snapshot(self) -> dict[str, int]:
        return dict(self._counters)
