import pymongo


class Mongo:
    def __init__(self, table):
        client = pymongo.MongoClient(
            "mongodb://username:password@mongodb:27017")

        # Создание базы данных
        mydb = client["mydatabase"]

        # Создание коллекции (аналог таблицы в реляционных базах данных)
        self.mycollection = mydb[table]
        

    def add(self, dictionary: dict):
        self.mycollection.insert_one(dictionary)
    
    def delete(self, key, value):
        self.mycollection.delete_one({f"{key}": value})

    def get_all(self):
        return self.mycollection.find()


    def get(self, key, value):
        return self.mycollection.find_one({f"{key}": value})

    def update(self, key, value, dictionary):
        self.mycollection.update_one({key: value}, {"$set": dictionary})

 

trades_db = Mongo("trades")
settings_db = Mongo("settings")

