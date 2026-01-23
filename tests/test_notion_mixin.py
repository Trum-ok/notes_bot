from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from pydantic import BaseModel

from notes.notion.errors import (
    NotionAPIError,
    NotionAuthError,
    NotionRateLimitError,
    NotionRequestError,
    NotionServerError,
)
from notes.notion.mixin import HttpxClientMixin


class SampleModel(BaseModel):
    id: str
    name: str


class MockClient(HttpxClientMixin):
    def __init__(self) -> None:
        self._client = AsyncMock(spec=httpx.AsyncClient)


class TestHttpxClientMixin:
    @pytest.fixture
    def client(self) -> MockClient:
        return MockClient()

    def test_map_http_error_401(self, client: MockClient) -> None:
        response = MagicMock()
        response.status_code = 401
        response.text = "Unauthorized"
        exc = httpx.HTTPStatusError("error", request=MagicMock(), response=response)

        result = client._map_http_error(exc)
        assert isinstance(result, NotionAuthError)
        assert "401" in str(result)

    def test_map_http_error_403(self, client: MockClient) -> None:
        response = MagicMock()
        response.status_code = 403
        response.text = "Forbidden"
        exc = httpx.HTTPStatusError("error", request=MagicMock(), response=response)

        result = client._map_http_error(exc)
        assert isinstance(result, NotionAuthError)

    def test_map_http_error_429(self, client: MockClient) -> None:
        response = MagicMock()
        response.status_code = 429
        response.text = "Rate limited"
        exc = httpx.HTTPStatusError("error", request=MagicMock(), response=response)

        result = client._map_http_error(exc)
        assert isinstance(result, NotionRateLimitError)

    def test_map_http_error_500(self, client: MockClient) -> None:
        response = MagicMock()
        response.status_code = 500
        response.text = "Internal Server Error"
        exc = httpx.HTTPStatusError("error", request=MagicMock(), response=response)

        result = client._map_http_error(exc)
        assert isinstance(result, NotionServerError)

    def test_map_http_error_503(self, client: MockClient) -> None:
        response = MagicMock()
        response.status_code = 503
        response.text = "Service Unavailable"
        exc = httpx.HTTPStatusError("error", request=MagicMock(), response=response)

        result = client._map_http_error(exc)
        assert isinstance(result, NotionServerError)

    def test_map_http_error_400(self, client: MockClient) -> None:
        response = MagicMock()
        response.status_code = 400
        response.text = "Bad Request"
        exc = httpx.HTTPStatusError("error", request=MagicMock(), response=response)

        result = client._map_http_error(exc)
        assert isinstance(result, NotionAPIError)
        assert not isinstance(result, NotionAuthError)
        assert not isinstance(result, NotionRateLimitError)
        assert not isinstance(result, NotionServerError)

    @pytest.mark.asyncio
    async def test_request_success(self, client: MockClient) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_response.raise_for_status = MagicMock()
        client._client.request.return_value = mock_response

        result = await client._request("GET", "/test")
        assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_request_http_error(self, client: MockClient) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=mock_response
        )
        client._client.request.return_value = mock_response

        with pytest.raises(NotionAuthError):
            await client._request("GET", "/test")

    @pytest.mark.asyncio
    async def test_request_network_error(self, client: MockClient) -> None:
        client._client.request.side_effect = httpx.RequestError("Connection failed")

        with pytest.raises(NotionRequestError):
            await client._request("GET", "/test")

    @pytest.mark.asyncio
    async def test_get_with_model(self, client: MockClient) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "123", "name": "Test"}
        mock_response.raise_for_status = MagicMock()
        client._client.request.return_value = mock_response

        result = await client.get("/test", model=SampleModel)
        assert isinstance(result, SampleModel)
        assert result.id == "123"
        assert result.name == "Test"

    @pytest.mark.asyncio
    async def test_get_without_model(self, client: MockClient) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "123", "name": "Test"}
        mock_response.raise_for_status = MagicMock()
        client._client.request.return_value = mock_response

        result = await client.get("/test")
        assert isinstance(result, dict)
        assert result["id"] == "123"

    @pytest.mark.asyncio
    async def test_post_method(self, client: MockClient) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"created": True}
        mock_response.raise_for_status = MagicMock()
        client._client.request.return_value = mock_response

        result = await client.post("/test", json={"data": "value"})
        assert result == {"created": True}
        client._client.request.assert_called_with(
            "POST", "/test", json={"data": "value"}
        )
