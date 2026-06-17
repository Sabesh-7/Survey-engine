from app.ai.embeddings.bge_m3_client import BgeM3Client
from app.core.config import get_settings
from app.repositories.embedding_repository import EmbeddingRepository
from app.utils.errors import ServiceError


class EmbeddingService:
    def __init__(self, client: BgeM3Client, repository: EmbeddingRepository) -> None:
        self._client = client
        self._repository = repository
        self._settings = get_settings()

    async def embed(self, text: str, language: str) -> list[float]:
        embedding = await self._client.embed(text=text, language=language)
        self._validate_embedding_dim(embedding)
        return embedding

    async def embed_batch(self, texts: list[str], languages: list[str] | None = None) -> list[list[float]]:
        embeddings = await self._client.embed_batch(texts=texts, languages=languages)
        for embedding in embeddings:
            self._validate_embedding_dim(embedding)
        return embeddings

    async def embed_and_store_question(self, question_id: str, text: str, language: str) -> list[float]:
        embedding = await self.embed(text=text, language=language)
        self._repository.upsert_question_embedding(
            question_id=question_id,
            model_name=self._settings.embeddings_model_name,
            embedding=embedding,
        )
        return embedding

    async def store_embeddings(self, question_embeddings: list[dict]) -> None:
        if not question_embeddings:
            return

        for item in question_embeddings:
            self._validate_embedding_dim(item["embedding"])

        model_name = self._settings.embeddings_model_name
        self._repository.upsert_question_embeddings(
            question_embeddings=question_embeddings,
            model_name=model_name,
        )

    def store_question_embedding(
        self,
        question_id: str,
        embedding: list[float],
        commit: bool = True,
    ) -> None:
        self._repository.upsert_question_embedding(
            question_id=question_id,
            model_name=self._settings.embeddings_model_name,
            embedding=embedding,
            commit=commit,
        )

    @property
    def model_name(self) -> str:
        return self._settings.embeddings_model_name

    async def warm_up(self) -> None:
        await self._client.warm_up()

    def _validate_embedding_dim(self, embedding: list[float]) -> None:
        if len(embedding) != self._settings.embeddings_dim:
            raise ServiceError(
                "Embedding dimension mismatch. "
                f"expected={self._settings.embeddings_dim} actual={len(embedding)}"
            )
