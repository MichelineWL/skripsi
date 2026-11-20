from google import genai

from app.core.config import settings
from app.core.exceptions import BusinessRuleError


class EmbeddingService:
    def __init__(self, client=None):
        if client is not None:
            self.client = client
        else:
            if not settings.gemini_api_key:
                raise BusinessRuleError(
                    "Gemini API key is not configured."
                )

            self.client = genai.Client(
                api_key=settings.gemini_api_key
            )

        self.model = settings.gemini_embedding_model

    def embed_text(self, text: str) -> list[float]:
        if not isinstance(text, str):
            raise BusinessRuleError(
                "Embedding input must be a string."
            )

        text = text.strip()

        if not text:
            raise BusinessRuleError(
                "Embedding input cannot be empty."
            )

        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=text,
            )

            if not response.embeddings:
                raise BusinessRuleError(
                    "Gemini returned no embedding."
                )

            embedding = response.embeddings[0].values

            if not embedding:
                raise BusinessRuleError(
                    "Gemini returned an empty embedding."
                )

            return [float(value) for value in embedding]

        except BusinessRuleError:
            raise

        except Exception as exc:
            raise BusinessRuleError(
                "Embedding generation failed."
            ) from exc