import sqlalchemy as sa
from app import db
from app.models import Character
from flask_login import current_user


def active_finder():
    active_char = db.session.scalar(
        sa.select(Character)
        .where(Character.players == current_user)
        .where(Character.active == True)
    )
    return active_char
