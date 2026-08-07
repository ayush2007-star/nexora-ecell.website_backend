from datetime import datetime

from app.utils.id_generator import generate_user_id


async def create_user(data: dict):

    user_id = await generate_user_id()

    return {
        "userId": user_id,
        "fullName": data["fullName"],
        "email": data["email"].lower(),
        "phone": data["phone"],
        "college": data["college"],
        "department": data["department"],
        "year": data["year"],
        "rollNumber": data["rollNumber"],

        "role": "leader",

        "password": None,

        "status": "Pending",

        "isApproved": False,

        "approvedBy": None,

        "approvedAt": None,

        "isActive": True,

        "createdAt": datetime.utcnow(),

        "updatedAt": datetime.utcnow()
    }