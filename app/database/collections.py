from app.database.mongodb import get_database


def get_collections():

    db = get_database()

    if db is None:
        return {
            "admins": None,
            "users": None,
            "teams": None,
            "members": None,
            "projects": None,
            "certificates": None,
            "notifications": None,
            "activity_logs": None,
            "settings": None,
            "counters": None,
            "events": None,
            "certificate_templates": None
        }

    return {
        "admins": db["admins"],
        "users": db["users"],
        "teams": db["teams"],
        "members": db["members"],
        "projects": db["projects"],
        "certificates": db["certificates"],
        "notifications": db["notifications"],
        "activity_logs": db["activity_logs"],
        "settings": db["settings"],
        "counters": db["counters"],
        "events": db["events"],
        "certificate_templates": db["certificate_templates"]
    }