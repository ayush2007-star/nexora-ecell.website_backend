from app.repositories.counter_repository import CounterRepository


async def generate_user_id():

    number = await CounterRepository.next_sequence("user")

    return f"USR{number:06d}"


async def generate_team_id():

    number = await CounterRepository.next_sequence("team")

    return f"TEAM{number:06d}"


async def generate_project_id():

    number = await CounterRepository.next_sequence("project")

    return f"PRJ{number:06d}"


async def generate_certificate_id():

    number = await CounterRepository.next_sequence("certificate")

    return f"CERT{number:06d}"
async def generate_management_update_id():

    number = await CounterRepository.next_sequence(
        "management_update"
    )

    return f"UPD{number:06d}"