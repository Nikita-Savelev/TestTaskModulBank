import os
import asyncio
from typing import Optional, Annotated
from fastapi import FastAPI, APIRouter
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import desc, and_
from sqlalchemy import update, select, func
from uvicorn import Server, Config
from models import Base, UserMessages
from dotenv import load_dotenv
from schemas import UserBodyRequestToDB, UserBodyAll, MessagesCount
from fastapi import Depends

load_dotenv()

db_engine = create_async_engine(
    f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")
async_session = async_sessionmaker(db_engine, expire_on_commit=False)


async def create_db():
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class MessageRepository:
    lock = asyncio.Lock()

    @classmethod
    async def add_message_get_lst_ten(cls, user_post: UserBodyRequestToDB):
        async with cls.lock:
            async with async_session() as session:
                user_dict: dict = user_post.model_dump()
                message_query = select(UserMessages).filter(
                    UserMessages.name == user_dict.get('name'))
                message_query = await session.execute(message_query)
                message_query = message_query.scalars().all()
                cnt = len(message_query)
                new_message = UserMessages(**user_dict)
                new_message.count = cnt + 1
                session.add(new_message)
                await session.flush()
                await session.commit()

                query = select(UserMessages).filter(
                    UserMessages.name == new_message.name).order_by(desc(UserMessages.id)).limit(10)
                result = await session.execute(query)
                last_ten_messages = result.scalars().all()
                messages = [UserBodyAll.model_validate(
                    message) for message in last_ten_messages]
        return {'messages': messages, 'count_messages': MessagesCount.model_validate(last_ten_messages[0])}


message_route = APIRouter()

@message_route.post('/add_message')
async def add_message(user_post: Annotated[UserBodyRequestToDB, Depends()]):
    last_ten_mess = await MessageRepository.add_message_get_lst_ten(user_post)
    return last_ten_mess


def create_app():

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try: await create_db()
        except: pass
        yield

    app = FastAPI(lifespan=lifespan)
    app.include_router(message_route)
    return app


app = create_app()

class MyServer(Server):
    async def run(self, sockets=None):
        self.config.setup_event_loop()
        return await self.serve(sockets=sockets)


async def run():
    app_ports = [5001, 5002]
    apps = []
    for cfg in app_ports:
        config = Config("server:app", host="127.0.0.1",
                        port=cfg, reload=True)
        server = MyServer(config=config)
        apps.append(server.run())
    return await asyncio.gather(*apps)


if __name__ == '__main__':
    asyncio.run(run())