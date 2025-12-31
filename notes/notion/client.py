from functools import cached_property
from typing import Any

import httpx

from notes.notion.mixin import HttpxClientMixin
from notes.notion.schemas import (
    BasePageProperty,
    CreatedPage,
    Page,
    Parent,
    UserListResponse,
)
from notes.settings import (
    NOTION_BASE_URL,
    NOTION_CLIENT_TIMEOUT,
    NOTION_VERSION,
    logger_notion,
)


class NotionClient(HttpxClientMixin):
    def __init__(self, token: str) -> None:
        self._token = token
        self._client = httpx.AsyncClient(
            base_url=NOTION_BASE_URL,
            headers=self._headers,
            timeout=NOTION_CLIENT_TIMEOUT,
        )

    @cached_property
    def _headers(self) -> dict:
        return {
            "Authorization": "Bearer " + self._token,
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION,
        }

    async def close(self) -> None:
        await self._client.aclose()
        logger_notion.info("Notion client closed")

    async def get_users(self, page_size: int) -> UserListResponse:
        logger_notion.info("Retrieving users...")
        response = await self.get(
            "/users", params={"page_size": page_size}, model=UserListResponse
        )
        logger_notion.info("%s users retrieved", len(response.results))
        return response

    async def create_page(
        self,
        parent: Parent,
        title: str,
        children: list | None = None,
        icon: Any | None = None,
        template: Any | None = None,
        properties: dict[str, BasePageProperty] | None = None,
    ) -> CreatedPage:
        # TODO
        page = Page(
            parent=parent,
            # properties=properties,
        )

        payload = page.model_dump()
        payload["properties"] = {
            "title": {
                "title": [
                    {"text": {"content": title}},
                ],
            },
        }
        response = await self._client.post(
            "/pages", json=payload, headers=self._headers
        )
        response.raise_for_status()

        return response.json()
