import json
import logging
import os
from typing import Annotated, Any

from fastapi import Depends, Request
from redis import asyncio as aioredis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


async def create_redis():
    # Timeouts courts : si Redis est indisponible, on échoue vite et on
    # retombe sur la base de données au lieu de bloquer la requête.
    return aioredis.from_url(
        REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=1,
        socket_timeout=1,
    )


async def get_redis(request: Request) -> aioredis.Redis:
    return request.app.state.redis


RedisDep = Annotated[aioredis.Redis, Depends(get_redis)]


# ---------- Helpers de cache : une panne Redis ne casse jamais la route ----------

async def cache_get(redis: aioredis.Redis, cle: str) -> Any | None:
    try:
        valeur = await redis.get(cle)
        return json.loads(valeur) if valeur is not None else None
    except (RedisError, OSError, ValueError) as ex:
        logger.warning("Cache indisponible (get %s) : %s", cle, ex)
        return None


async def cache_set(redis: aioredis.Redis, cle: str, data: Any, ttl: int = 60) -> None:
    try:
        await redis.set(cle, json.dumps(data), ex=ttl)
    except (RedisError, OSError, TypeError, ValueError) as ex:
        logger.warning("Cache indisponible (set %s) : %s", cle, ex)


async def cache_delete(redis: aioredis.Redis, cle: str) -> None:
    try:
        await redis.delete(cle)
    except (RedisError, OSError) as ex:
        logger.warning("Cache indisponible (delete %s) : %s", cle, ex)


async def cache_delete_pattern(redis: aioredis.Redis, motif: str) -> None:
    try:
        async for cle in redis.scan_iter(motif):
            await redis.delete(cle)
    except (RedisError, OSError) as ex:
        logger.warning("Cache indisponible (delete %s) : %s", motif, ex)