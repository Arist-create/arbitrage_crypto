import aioredis

class RedisFacade:
    def __init__(self, url):
        self.client = aioredis.from_url(url)

    async def get(self, key):
        return await self.client.get(key)

    async def set(self, key, value):
        return await self.client.set(key, value)
    
    async def delete(self, key):
        return await self.client.delete(key)
    
redis = RedisFacade('redis://redis:6379/0')