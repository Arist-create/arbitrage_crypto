import aioredis
import json

class RedisFacade:
    def __init__(self, url):
        self.client = aioredis.from_url(url)

    async def get(self, key):
        return await self.client.get(key)

    async def set(self, key, value):
        return await self.client.set(key, value)
    
    async def delete(self, key):
        return await self.client.delete(key)

    async def get_all(self):
        keys = await self.client.keys()
        if not keys:
            return []
        list = await self.client.mget(keys)

        return [json.loads(i) if i else None for i in list]    


redis = RedisFacade('redis://redis:6379/0')
trades_redis = RedisFacade('redis://redis:6379/2')