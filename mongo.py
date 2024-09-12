from motor import motor_asyncio


class Mongo:
    def __init__(self, table):
        client = motor_asyncio.AsyncIOMotorClient(
            "mongodb://username:password@mongodb:27017")

        # Создание базы данных
        mydb = client["mydatabase"]

        # Создание коллекции (аналог таблицы в реляционных базах данных)
        self.mycollection = mydb[table]
        
 
    async def add(self, dictionary: dict):
        await self.mycollection.insert_one(dictionary)
    
    async def delete(self, key, value):
        await self.mycollection.delete_one({f"{key}": value})

    async def delete_all(self):
        await self.mycollection.delete_many({})

    async def get_all(self):
        return await self.mycollection.find().to_list(length=None)

    async def get(self, key, value): 
        return await self.mycollection.find_one({key: value})

    async def update(self, key, value, dictionary):
        await self.mycollection.update_one({key: value}, {"$set": dictionary})
    
    async def count(self, key, value):
        return await self.mycollection.count_documents({f"{key}": value})



 

trades_db = Mongo("trades")
settings_db = Mongo("settings")
goplus_db = Mongo("goplus")

