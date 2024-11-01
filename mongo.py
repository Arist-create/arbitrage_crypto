from motor import motor_asyncio


class Mongo:
    def __init__(self, table):
        client = motor_asyncio.AsyncIOMotorClient(
            "mongodb://username:password@mongodb:27017")

        # Создание базы данных
        mydb = client["mydatabase"]

        # Создание коллекции (аналог таблицы в реляционных базах данных)
        self.mycollection = mydb[table]
        
 
    
    async def delete(self, key, value):
        await self.mycollection.delete_one({f"{key}": value})

    async def get_all(self):
        return await self.mycollection.find().to_list(length=None)

    async def get(self, key, value): 
        return await self.mycollection.find_one({key: value})

    async def update(self, key, value, dictionary, upsert=False):
        await self.mycollection.update_one({key: value}, {"$set": dictionary}, upsert=upsert)
        
    async def count(self, key, value):
        return await self.mycollection.count_documents({f"{key}": value})
    
    async def count(self, key, value):
        return await self.mycollection.count_documents({f"{key}": value})



goplus_db = Mongo("goplus")
list_of_pairs_mexc_db = Mongo("list_of_pairs_mexc")
tokens_mexc_by_chains_db = Mongo("tokens_mexc_by_chains")
users_settings_db = Mongo("users_settings")