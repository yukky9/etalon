import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import desc
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert

from services.objects.schemes.objects import Objects, ObjectsListRs, ObjectsCreateRs, ObjectsCreateRq
from services.objects.models.objects import ObjectModel


# Репозиторий объекта. Отвечает за взаимодействие с базой данных
class ObjectsRepository:
    # Инициализация
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    # Создание объекта в базе данных
    async def create(
            self,
            request: ObjectsCreateRq
    ) -> ObjectsCreateRs:
        name = request.name
        id_ = str(uuid.uuid4())

        stmt = insert(ObjectModel).values(
            id=id_,
            name=name
        )
        await self.db_session.execute(stmt)
        await self.db_session.commit()

        return ObjectsCreateRs(
            id=id_
        )

    # Получение списка объектов из базы данных
    async def list(
            self
    ) -> ObjectsListRs:
        result = await self.db_session.execute(
            select(
                ObjectModel.id,
                ObjectModel.name
            )
            .order_by(
                desc(ObjectModel.updated_at)
            )
        )
        objects = result.fetchall()

        response = []
        for object_ in objects:
            response.append(
                Objects(
                    id=object_.id,
                    name=object_.name
                )
            )

        return ObjectsListRs(
            objects=response
        )
