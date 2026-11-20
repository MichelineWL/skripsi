from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import BusinessRuleError
from app.services.embedding_service import EmbeddingService


def create_mock_client(embedding_values=None):
    client = MagicMock()

    if embedding_values is None:
        embedding_values = [0.1, 0.2, 0.3]

    response = SimpleNamespace(
        embeddings=[
            SimpleNamespace(
                values=embedding_values
            )
        ]
    )

    client.models.embed_content.return_value = response

    return client


def test_embed_text_returns_float_vector():
    client = create_mock_client(
        embedding_values=[0.1, 0.2, 0.3]
    )
    service = EmbeddingService(client=client)

    result = service.embed_text("Test document")

    assert result == [0.1, 0.2, 0.3]
    assert all(isinstance(value, float) for value in result)


def test_embed_text_calls_gemini_with_configured_model():
    client = create_mock_client()
    service = EmbeddingService(client=client)

    service.embed_text("Test document")

    client.models.embed_content.assert_called_once_with(
        model=service.model,
        contents="Test document",
    )


def test_embed_text_strips_whitespace():
    client = create_mock_client()
    service = EmbeddingService(client=client)

    service.embed_text("  Test document  ")

    client.models.embed_content.assert_called_once_with(
        model=service.model,
        contents="Test document",
    )


def test_embed_text_rejects_empty_input():
    service = EmbeddingService(
        client=create_mock_client()
    )

    with pytest.raises(BusinessRuleError):
        service.embed_text("   ")


def test_embed_text_rejects_non_string_input():
    service = EmbeddingService(
        client=create_mock_client()
    )

    with pytest.raises(BusinessRuleError):
        service.embed_text(None)


def test_embed_text_rejects_empty_embedding_response():
    client = MagicMock()
    client.models.embed_content.return_value = (
        SimpleNamespace(embeddings=[])
    )

    service = EmbeddingService(client=client)

    with pytest.raises(BusinessRuleError):
        service.embed_text("Test document")


def test_embed_text_rejects_empty_vector():
    client = MagicMock()
    client.models.embed_content.return_value = (
        SimpleNamespace(
            embeddings=[
                SimpleNamespace(values=[])
            ]
        )
    )

    service = EmbeddingService(client=client)

    with pytest.raises(BusinessRuleError):
        service.embed_text("Test document")


def test_embed_text_wraps_provider_error():
    client = MagicMock()
    client.models.embed_content.side_effect = (
        RuntimeError("API connection failed")
    )

    service = EmbeddingService(client=client)

    with pytest.raises(
        BusinessRuleError,
        match="Embedding generation failed.",
    ):
        service.embed_text("Test document")