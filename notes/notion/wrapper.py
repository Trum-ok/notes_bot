from notes.notion.client import NotionClient
from notes.notion.schemas import DatabaseParent, UserListResponse


class NotionWrapper:
    def __init__(self, client: NotionClient) -> None:
        self.client = client

    async def get_users(self, page_size: int) -> UserListResponse:
        return await self.client.get_users(page_size=page_size)

    async def create_note(self, database_id: str, note: str) -> None:
        parent = DatabaseParent(database_id=database_id)
        # properties = {
        #     f"{note}": TitleProperty(title=[note]),
        # }

        await self.client.create_page(
            parent=parent,
            # properties=properties,
            title=note,
        )

        # TODO


async def setup_notion_connection(token: str) -> NotionWrapper:
    client = NotionClient(token=token)
    await client.get_users(page_size=1)
    return NotionWrapper(client=client)
