from redis.asyncio import Redis

from src.settings import REDIS_HOST, REDIS_PORT


redis = Redis(host=REDIS_HOST, port=REDIS_PORT)
