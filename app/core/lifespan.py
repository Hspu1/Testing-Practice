from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis import ConnectionError, ResponseError, RedisError

from app.infrastructure.cache_config import redis_cache
from app.infrastructure.queue_config import broker
from app.utils import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        if not broker.is_worker_process:
            await broker.startup()

        app.state.redis_cache = redis_cache
        app.state.broker = broker

        yield

        if not broker.is_worker_process:
            await broker.shutdown()
        await app.state.redis_cache.aclose()

    except (ConnectionError, ResponseError) as e:
        logger.critical(f"Redis startup failed: {e}")
        raise

    except RedisError as e:
        logger.critical(f"Redis startup failed (RedisError): {e}")
        raise
