
from notes.notion.enums import ParentTypeEnum
from notes.notion.schemas import (
    BlockParent,
    DatabaseParent,
    DataSourceParent,
    Page,
    PageParent,
    User,
    UserListResponse,
    WorkspaceParent,
)


class TestParentSchemas:
    def test_database_parent(self) -> None:
        parent = DatabaseParent(database_id="db-123")
        assert parent.type == ParentTypeEnum.database_id
        assert parent.database_id == "db-123"

    def test_page_parent(self) -> None:
        parent = PageParent(page_id="page-456")
        assert parent.type == ParentTypeEnum.page_id
        assert parent.page_id == "page-456"

    def test_workspace_parent(self) -> None:
        parent = WorkspaceParent()
        assert parent.type == ParentTypeEnum.workspace
        assert parent.workspace is True

    def test_block_parent(self) -> None:
        parent = BlockParent(block_id="block-789")
        assert parent.type == ParentTypeEnum.block_id
        assert parent.block_id == "block-789"

    def test_data_source_parent(self) -> None:
        parent = DataSourceParent(data_source_id="ds-123", database_id="db-456")
        assert parent.type == ParentTypeEnum.data_source_id
        assert parent.data_source_id == "ds-123"
        assert parent.database_id == "db-456"


class TestPageSchema:
    def test_page_with_database_parent(self) -> None:
        parent = DatabaseParent(database_id="db-123")
        page = Page(parent=parent)

        assert page.parent == parent
        assert page.children == []
        assert page.cover is None

    def test_page_serialization(self) -> None:
        parent = DatabaseParent(database_id="db-123")
        page = Page(parent=parent)
        data = page.model_dump()

        assert data["parent"]["type"] == "database_id"
        assert data["parent"]["database_id"] == "db-123"


class TestUserSchema:
    def test_user_minimal(self) -> None:
        user = User(object="user", id="user-123")
        assert user.id == "user-123"
        assert user.name is None
        assert user.type is None

    def test_user_full(self) -> None:
        user = User(
            object="user",
            id="user-456",
            type="person",
            name="John Doe",
            avatar_url="https://example.com/avatar.png",
        )
        assert user.name == "John Doe"
        assert user.avatar_url == "https://example.com/avatar.png"


class TestUserListResponse:
    def test_empty_response(self) -> None:
        response = UserListResponse(object="list", results=[], has_more=False)
        assert len(response.results) == 0
        assert response.has_more is False
        assert response.next_cursor is None

    def test_response_with_users(self) -> None:
        users = [
            User(object="user", id="user-1", name="User 1"),
            User(object="user", id="user-2", name="User 2"),
        ]
        response = UserListResponse(
            object="list",
            results=users,
            has_more=True,
            next_cursor="cursor-123",
        )
        assert len(response.results) == 2
        assert response.has_more is True
        assert response.next_cursor == "cursor-123"
