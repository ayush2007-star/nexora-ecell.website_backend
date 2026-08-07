from app.database.mongodb import get_database


class CounterRepository:

    @staticmethod
    async def next_sequence(name: str):

        db = get_database()

        if db is None:
            raise RuntimeError("MongoDB is not connected yet.")

        counters = db["counters"]

        document = await counters.find_one_and_update(
            {"_id": name},
            {"$inc": {"sequence": 1}},
            upsert=True,
            return_document=True
        )

        return document["sequence"]
