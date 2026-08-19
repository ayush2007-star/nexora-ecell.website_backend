import asyncio
from datetime import datetime, timezone

from app.database.mongodb import connect_db
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password


async def create_admin():
    print("\n================================")
    print("      NEXORA ADMIN CREATOR")
    print("================================\n")

    full_name = input("Admin full name: ").strip()
    email = input("Admin email: ").strip().lower()
    phone = input("Admin phone (10 digits): ").strip()
    password = input("Admin password: ").strip()

    if not full_name:
        print("❌ Full name is required.")
        return

    if not email:
        print("❌ Email is required.")
        return

    if not phone.isdigit() or len(phone) != 10:
        print("❌ Phone must contain exactly 10 digits.")
        return

    if len(password) < 8:
        print("❌ Password must be at least 8 characters.")
        return

    await connect_db()

    existing_email = await UserRepository.find_by_email(email)

    if existing_email:
        print("❌ This email is already registered.")
        return

    users = UserRepository

    # Check phone uniqueness because users.phone has a unique index.
    from app.database.collections import get_collections

    existing_phone = await get_collections()["users"].find_one(
        {"phone": phone}
    )

    if existing_phone:
        print("❌ This phone number is already registered.")
        return

    now = datetime.now(timezone.utc)

    admin = {
        "userId": f"ADMIN-{int(now.timestamp() * 1000)}",

        "fullName": full_name,
        "email": email,
        "phone": phone,

        "college": "",
        "department": "",
        "year": "",
        "rollNumber": "",

        "role": "admin",

        "password": hash_password(password),

        "status": "Approved",
        "isApproved": True,

        "approvedBy": None,
        "approvedAt": now,

        "isActive": True,

        "createdAt": now,
        "updatedAt": now,
    }

    await UserRepository.create(admin)

    print("\n================================")
    print("✅ ADMIN CREATED SUCCESSFULLY")
    print("================================")
    print(f"Name : {full_name}")
    print(f"Email: {email}")
    print(f"Phone: {phone}")
    print("Role : admin")
    print("\nLogin:")
    print("http://localhost:5173/admin/login")


if __name__ == "__main__":
    asyncio.run(create_admin())