from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.settings import settings
from core.logger import init_logger, logger
from core.postgres.initialization import PostgresClient
from core.redis.initialization import RedisClient
from core.roboflow.initialization import RoboflowClient
from services import init_routers


# Lifespan для инициализации и закрытия ресурсов
@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_logger()
    await PostgresClient.init_postgres()
    await RedisClient.init_redis()
    await RoboflowClient.init_roboflow()
    logger.info("All resources have been successfully initialized")
    yield
    await PostgresClient.close_postgres()
    await RedisClient.close_redis()
    await RoboflowClient.close_roboflow()
    logger.info("All resources have been successfully closed")


# Инициализация приложения
def init_app() -> FastAPI:
    _app = FastAPI(
        title="Etalon API",
        version="1.0.0",
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        lifespan=lifespan,
    )
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    init_routers(_app)
    return _app


app = init_app()

# Запуск сервера
if __name__ == "__main__":
    host, port = settings.server_address.split(":")
    uvicorn.run(app, host=host, port=int(port))
