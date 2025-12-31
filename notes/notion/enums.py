from enum import StrEnum


class UserObjectEnum(StrEnum):
    user = "user"


class UsersTypeEnum(StrEnum):
    person = "person"
    bot = "bot"


class UserBotOwnerTypeEnum(StrEnum):
    workspace = "workspace"
    user = "user"


class ParentTypeEnum(StrEnum):
    database_id = "database_id"
    data_source_id = "data_source_id"
    page_id = "page_id"
    workspace = "workspace"
    block_id = "block_id"


class PagePropertyTypeEnum(StrEnum):
    title = "title"
    rich_text = "rich_text"
