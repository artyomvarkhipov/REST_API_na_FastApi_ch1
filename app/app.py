from typing import Annotated, Optional

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas
from dependencies import get_db_session
from lifespan import lifespan
from services import add_item, get_item, update_item, delete_item, search_items

app = FastAPI(
    title="My Advertisement App",
    description="This is a very simple advertisement application API",
    version="0.0.1",
    lifespan=lifespan
)

# Создаём тип для зависимости сессии
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


@app.post("/advertisement", response_model=schemas.CreateAdvertisementResponse, summary="Создать новое объявление")
async def create_advertisement(
        advertisement_data: schemas.CreateAdvertisementRequest,
        session: SessionDep
):
    # Используем сервисную функцию
    new_advertisement = await add_item(session, models.Advertisement, advertisement_data)
    return schemas.CreateAdvertisementResponse(id=new_advertisement.id)


@app.get("/advertisement/{advertisement_id}", response_model=schemas.GetAdvertisementResponse,
         summary="Получить объявление по ID")
async def get_advertisement(
        advertisement_id: int,
        session: SessionDep
):
    advertisement = await get_item(session, models.Advertisement, advertisement_id)
    # Преобразуем ORM-модель в словарь и затем в Pydantic-схему
    return schemas.GetAdvertisementResponse(**advertisement.to_dict())


@app.get("/advertisement", response_model=list[schemas.GetAdvertisementResponse],
         summary="Поиск объявлений по полям")
async def search_advertisement(
        session: SessionDep,
        title: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        author: Optional[str] = None
):
    advertisements = await search_items(
        session,
        models.Advertisement,
        title=title,
        description=description,
        price=price,
        author=author
    )
    return [schemas.GetAdvertisementResponse(**item.to_dict()) for item in advertisements]


@app.patch("/advertisement/{advertisement_id}", response_model=schemas.UpdateAdvertisementResponse,
           summary="Обновить объявление")
async def update_advertisement(
        advertisement_id: int,
        update_data: schemas.UpdateAdvertisementRequest,
        session: SessionDep
):
    updated_advertisement = await update_item(session, models.Advertisement, advertisement_id, update_data)
    return schemas.UpdateAdvertisementResponse(**updated_advertisement.to_dict())


@app.delete("/advertisement/{advertisement_id}", response_model=schemas.OKResponse, summary="Удалить объявление")
async def delete_advertisement(
        advertisement_id: int,
        session: SessionDep
):
    await delete_item(session, models.Advertisement, advertisement_id)
    return schemas.OKResponse()
