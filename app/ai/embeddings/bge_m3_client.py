from __future__ import annotations

import threading
from typing import Iterable

import anyio

from app.core.config import get_settings


class BgeM3Client:
    def __init__(
        self,
        model_name: str | None = None,
        device: str | None = None,
        batch_size: int | None = None,
        normalize: bool | None = None,
    ) -> None:
        settings = get_settings()
        self._model_name = model_name or settings.embeddings_model_name
        self._device = device or settings.embeddings_device
        self._batch_size = batch_size or settings.embeddings_batch_size
        self._normalize = normalize if normalize is not None else settings.embeddings_normalize
        self._model = None
        self._lock = threading.Lock()

    async def embed(self, text: str, language: str) -> list[float]:
        embeddings = await self.embed_batch([text], [language])
        return embeddings[0]

    async def warm_up(self) -> None:
        await anyio.to_thread.run_sync(self._load_model)

    async def embed_batch(self, texts: Iterable[str], languages: Iterable[str] | None = None) -> list[list[float]]:
        text_list = list(texts)
        if not text_list:
            return []

        return await anyio.to_thread.run_sync(self._encode_sync, text_list)

    def close(self) -> None:
        with self._lock:
            self._model = None

    def _load_model(self):
        if self._model is None:
            with self._lock:
                if self._model is None:
                    try:
                        from sentence_transformers import SentenceTransformer
                    except ImportError as exc:
                        raise RuntimeError(
                            "sentence-transformers is required for local BGE-M3 embeddings"
                        ) from exc

                    self._model = SentenceTransformer(self._model_name, device=self._device)

        return self._model

    def _encode_sync(self, texts: list[str]) -> list[list[float]]:
        model = self._load_model()
        embeddings = model.encode(
            texts,
            batch_size=self._batch_size,
            normalize_embeddings=self._normalize,
        )
        return [embedding.tolist() for embedding in embeddings]
