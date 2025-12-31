from typing import Any, TypeVar, overload

import httpx
from pydantic import BaseModel

from notes.notion.errors import (
    NotionAPIError,
    NotionAuthError,
    NotionRateLimitError,
    NotionRequestError,
    NotionServerError,
)

T = TypeVar("T", bound=BaseModel)


class HttpxClientMixin:
    _client: httpx.AsyncClient

    async def _request_raw(
        self, method: str, url: str, **kwargs: Any
    ) -> httpx.Response:
        return await self._client.request(method, url, **kwargs)

    def _map_http_error(self, exc: httpx.HTTPStatusError) -> NotionAPIError:
        status = exc.response.status_code
        body = exc.response.text

        if status in (401, 403):
            return NotionAuthError(f"{status}: {body}")
        if status == 429:
            return NotionRateLimitError(f"{status}: {body}")
        if 500 <= status:
            return NotionServerError(f"{status}: {body}")

        return NotionAPIError(f"{status}: {body}")

    async def _request(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        try:
            response = await self._request_raw(method, url, **kwargs)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as exc:
            raise self._map_http_error(exc) from exc

        except httpx.RequestError as exc:
            raise NotionRequestError(str(exc)) from exc

    @overload
    async def get(
        self,
        url: str,
        *,
        model: type[T],
        **kwargs: Any,
    ) -> T: ...

    @overload
    async def get(
        self,
        url: str,
        *,
        model: None = None,
        **kwargs: Any,
    ) -> dict[str, Any]: ...

    async def get(
        self,
        url: str,
        *,
        model: type[T] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any] | T:
        data = await self._request("GET", url, **kwargs)
        return model.model_validate(data) if model else data

    async def post(
        self,
        url: str,
        *,
        model: type[T] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any] | T:
        data = await self._request("POST", url, **kwargs)
        return model.model_validate(data) if model else data

    async def patch(
        self,
        url: str,
        *,
        model: type[T] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any] | T:
        data = await self._request("PATCH", url, **kwargs)
        return model.model_validate(data) if model else data

    async def delete(
        self,
        url: str,
        *,
        model: type[T] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any] | T:
        data = await self._request("DELETE", url, **kwargs)
        return model.model_validate(data) if model else data
