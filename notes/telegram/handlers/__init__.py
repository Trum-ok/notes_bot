from aiogram import Router

from .inline import inline_router
from .message import message_router

routers: set[Router] = {
    inline_router,
    message_router,
}
