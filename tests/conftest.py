import pytest, asyncio
from motor.motor_asyncio import AsyncIOMotorClient

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def mongo_client():
    client = AsyncIOMotorClient("mongodb://mongo:27017/test")
    yield client
    await client.drop_database("test")
    client.close()
