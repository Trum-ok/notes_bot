from pydantic import BaseModel, Field

from notes.notion.enums import (
    PagePropertyTypeEnum,
    ParentTypeEnum,
    UserBotOwnerTypeEnum,
    UserObjectEnum,
    UsersTypeEnum,
)


class Parent(BaseModel):
    pass


class DatabaseParent(Parent):
    type: ParentTypeEnum = ParentTypeEnum.database_id
    database_id: str


class DataSourceParent(Parent):
    type: ParentTypeEnum = ParentTypeEnum.data_source_id
    data_source_id: str
    database_id: str


class PageParent(Parent):
    type: ParentTypeEnum = ParentTypeEnum.page_id
    page_id: str


class WorkspaceParent(Parent):
    type: ParentTypeEnum = ParentTypeEnum.workspace
    workspace: bool = True


class BlockParent(Parent):
    type: ParentTypeEnum = ParentTypeEnum.block_id
    block_id: str


class UserPerson(BaseModel):
    email: str | None = None


class UserBotOwner(BaseModel):
    type: UserBotOwnerTypeEnum


class UserWorkspaceLimits(BaseModel):
    max_file_upload_size_in_bytes: int = 5242880


class User(BaseModel):
    object: UserObjectEnum
    id: str
    type: UsersTypeEnum | None = None
    name: str | None = None
    avatar_url: str | None = None
    person: UserPerson | None = None
    bot: dict = Field(default_factory=dict)
    owner: UserBotOwner | None = None
    workspace_name: str | None = None
    workspace_id: str | None = None
    workspace_limits: UserWorkspaceLimits = Field(default_factory=dict)


class BasePageProperty(BaseModel):
    id: str
    name: str
    type: PagePropertyTypeEnum


class TitleProperty(BasePageProperty):
    id: PagePropertyTypeEnum = PagePropertyTypeEnum.title
    type: PagePropertyTypeEnum = PagePropertyTypeEnum.title
    name: str | None = None
    title: list = Field(default_factory=list)


class PageTemplate(BaseModel):
    type: str = "none"
    template_id: str | None = None


class Page(BaseModel):
    parent: (
        Parent
        | DatabaseParent
        | DataSourceParent
        | PageParent
        | WorkspaceParent
        | BlockParent
    )
    # properties: dict[str, TitleProperty] = Field(default_factory=dict)  # TODO
    children: list = Field(default_factory=list)
    cover: dict | None = None
    template: PageTemplate = PageTemplate()


class CreatedPage(BaseModel):
    properties: dict[str, BasePageProperty]


class UserListResponse(BaseModel):
    object: str = "list"
    results: list[User] = Field(default_factory=list)
    next_cursor: str | None = None
    has_more: bool
