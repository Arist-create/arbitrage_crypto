import aioredis

class RedisFacade:
    def __init__(self, url):
        self.client = aioredis.from_url(url)
        self.client.config_set("read-only", 0)

    async def get(self, key):
        return await self.client.get(key)

    async def set(self, key, value):
        return await self.client.set(key, value)
    
redis = RedisFacade('redis://redis:6379')