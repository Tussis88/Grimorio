import sqlalchemy as sa
from flask_login import current_user
from flask import session
from app import db
from app.models import Character


def active_char_setter() -> None:
    """Trova e aggiorna i dati nella sessione relativi al personaggio attivo"""
    char_dict = {
        "id": "0",
        "name": "gigiris",
        "group": "Cazzovuoi",
        "active": False,
        "master": False,
        "editable": False,
        "hidden": False,
        "user_id": "0",
    }
    if current_user:
        active_char = db.session.scalar(
            sa.select(Character)
            .where(Character.players == current_user)
            .where(Character.active == True)
        )
        if active_char:
            char_dict = {
                "id": active_char.id,
                "name": active_char.name,
                "group": active_char.group,
                "active": active_char.active,
                "editable": active_char.editable,
                "hidden": active_char.hidden,
                "master": active_char.master,
                "user_id": active_char.user_id,
            }
    session["active_char"] = char_dict
