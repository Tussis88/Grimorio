import sqlalchemy as sa
from app import db
from app.models import User, Character, Spell
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, validators
from wtforms.validators import DataRequired, ValidationError, EqualTo


class LoginForm(FlaskForm):
    username = StringField("Nome Utente", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Mantieni l'accesso")
    submit = SubmitField("Accedi")


class RegistrationForm(FlaskForm):
    username = StringField("Nome Utente", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Ripeti la Password", validators=[DataRequired(), EqualTo("password", "le password non sono uguali")]
    )
    submit = SubmitField("Crea Account")

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if username.data.startswith(" ") or username.data.endswith(" "):
            raise ValidationError("Il Nome Utente non può iniziare o finire con degli spazi")
        if user is not None:
            raise ValidationError("Nome Utente già in uso")


class CharacterCreationForm(FlaskForm):
    name = StringField("Nome Personagio", validators=[DataRequired()])
    group = StringField("Nome Gruppo")
    # plane = StringField("Piano di Appartenenza")
    master = BooleanField("Master")
    submit = SubmitField("Salva")

    def validate_name(self, name):
        char_name = db.session.scalar(
            sa.select(Character).where(Character.name == name.data.strip().capitalize())
        )
        if char_name is not None:
            raise ValidationError("Nome Personaggio già in uso")


class SpellCreationForm(FlaskForm):
    name = StringField("Nome Spell", validators=[DataRequired()])
    level = IntegerField("lvl", validators=[DataRequired()])
    submit = SubmitField("aggiungi")


class GroupChangeForm(FlaskForm):
    group_c = StringField("Nome Gruppo", validators=[DataRequired()])
    submit = SubmitField("Cambia")


class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")
