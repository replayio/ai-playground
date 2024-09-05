from asyncio import Queue
from typing import TypeVar, Generic

T = TypeVar("T")


class TypedQueue(Queue, Generic[T]):
    def __init__(self, maxsize: int = 0):
        super().__init__(maxsize=maxsize)

    async def put(self, item: T) -> None:
        await super().put(item)

    async def get(self) -> T:
        return await super().get()
