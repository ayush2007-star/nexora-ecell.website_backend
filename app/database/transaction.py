# from contextlib import asynccontextmanager
# from app.database.mongodb import mongodb


# @asynccontextmanager
# async def transaction():

#     if mongodb.client is None:
#         raise RuntimeError("MongoDB client is not connected yet.")

#     async with await mongodb.client.start_session() as session:

#         async with session.start_transaction():

#             yield session
