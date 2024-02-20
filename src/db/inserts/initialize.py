import json

from sqlalchemy import select, func, insert

from src.db.db_helpers import current_session
from src.db.models import RadioStates, Radios, RadioAdTime


def insert_init():
    session = current_session.get()

    stmt = select(func.count()).select_from(RadioStates)
    cnt = session.scalar(stmt)
    if cnt > 0:
        return

    with open("/app/database/states.json") as f:
        session.execute(
            insert(RadioStates),
            json.load(f)
        )

    with open("/app/database/radios.json") as f:
        session.execute(
            insert(Radios),
            json.load(f)
        )

    with open("/app/database/radio_ad_times.json") as f:
        session.execute(
            insert(RadioAdTime),
            json.load(f)
        )
