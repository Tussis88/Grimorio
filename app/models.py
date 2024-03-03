from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(32), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    chars: so.WriteOnlyMapped["Character"] = so.relationship(back_populates="players")

    def __repr__(self):
        return "<User: {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Character(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    group: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64), index=True)
    plane: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64), index=True)
    master: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    active: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    players: so.Mapped[User] = so.relationship(back_populates="chars")
    spells: so.WriteOnlyMapped["Spell"] = so.relationship(
        back_populates="spell_chars", passive_deletes=True
    )

    def __repr__(self):
        return "<Character: {}, group: {}, master: {}, active: {}>".format(
            self.name, self.group, self.master, self.active
        )


class Spell(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    level: so.Mapped[int] = so.mapped_column(sa.Integer)
    prepared: so.Mapped[int] = so.mapped_column(sa.Integer, default=1)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    id_character: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(Character.id), index=True
    )

    spell_chars: so.Mapped[Character] = so.relationship(back_populates="spells")

    def __repr__(self):
        return "<spell name: {}, level:{}, prepared:{}>".format(
            self.name, self.level, self.prepared
        )
