from motor.motor_asyncio import AsyncIOMotorClient
from v1_app.database.db_utils import DATABASE_URL


# Function to get database Connection URL
async def connect_to_mongo(MONGO_DB=None):
    mongo_uri = DATABASE_URL
    client = AsyncIOMotorClient(mongo_uri)
    db = client[MONGO_DB]
    return db


# Function to close database Connection
async def close_mongo_connection():
    client = get_database()
    client.close()


# Function that will be called in routes to connect to database
async def get_database():
    db = getattr(get_database, "database", None)
    if db is None:
        db = await connect_to_mongo(MONGO_DB="nightclub")
        get_database.db = db
    return db
