from typing import Any, ClassVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base


class BaseDAO[ModelT: Base]:
    model: ClassVar[type[Base]]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, **values: Any) -> ModelT:
        obj = self.model(**values)
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def add_many(self, rows: list[dict[str, Any]]) -> list[ModelT]:
        objects = [self.model(**values) for values in rows]
        self.session.add_all(objects)
        await self.session.flush()
        return objects
