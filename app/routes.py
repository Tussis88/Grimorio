import sqlalchemy as sa
from app import app, db
from app.forms import (
    LoginForm,
    RegistrationForm,
    CharacterCreationForm,
    EmptyForm,
    SpellCreationForm,
    GroupChangeForm,
)
from app.models import User, Character, Spell
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit

from app.helpers import active_finder


@app.route("/")
@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    form = CharacterCreationForm()
    characters = db.session.scalars(
        sa.select(Character).where(Character.players == current_user)
    )
    if form.validate_on_submit():
        for character in characters:
            character.active = False
        new_char = Character(
            name=form.name.data.capitalize(),
            group=form.group.data.capitalize(),
            master=form.master.data,
            active=True,
            user_id=current_user.id,
        )
        db.session.add(new_char)
        db.session.commit()
        return redirect(url_for("index"))

    characters = db.session.scalars(
        sa.select(Character).where(Character.players == current_user)
    )
    active_char = active_finder()

    return render_template(
        "index.html",
        title="Home",
        characters=characters,
        form=form,
        active_char=active_char,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        if user is None:
            flash("Username non trovato")
            return redirect(url_for("login"))
        if not user.check_password(form.password.data):
            flash("password errata")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        # urlsplit().netloc verifica se l'utente arriva da un sito esterno.
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Accedi", active_char="empty", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Ti sei registrato con successo!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Registrati", form=form)


@app.route("/incantesimi/<char_name>", methods=["GET", "POST"])
@login_required
def incantesimi(char_name):
    character = db.first_or_404(sa.select(Character).where(Character.name == char_name))
    active_char = active_finder()
    form = SpellCreationForm()
    if form.validate_on_submit():
        new_spell = Spell(
            name=form.name.data.strip().title(),
            level=int(form.level.data),
            id_character=character.id,
        )
        db.session.add(new_spell)
        db.session.commit()
        return redirect(url_for("incantesimi", char_name=active_char.name))

    spells = db.session.scalars(
        sa.select(Spell)
        .where(Spell.spell_chars == character)
        .order_by(Spell.level, Spell.name)
    ).all()
    return render_template(
        "incantesimi.html",
        title=" Incantesimi Preparati",
        active_char=active_char,
        spells=spells,
        character=character,
        form=form,
    )


@app.route("/master/<group_name>")
@login_required
def master(group_name):
    active_char = active_finder()
    members = db.session.scalars(
        sa.select(Character)
        .where(Character.group == group_name)
        .where(Character.master == False)
    )
    return render_template(
        "master.html",
        active_char=active_char,
        title="La Pagina del Master",
        members=members,
    )


@app.route("/activate/<id>", methods=["POST"])
@login_required
def activate(id):
    form = EmptyForm()
    if form.validate_on_submit():
        characters = db.session.scalars(
            sa.select(Character).where(Character.players == current_user)
        )
        for character in characters:
            character.active = False

        new_active = db.session.scalar(sa.select(Character).where(Character.id == id))
        new_active.active = True
        db.session.commit()
    return redirect(url_for("index"))


@app.route("/change_group/<id>", methods=["POST"])
@login_required
def change_group(id):
    form = GroupChangeForm()
    if form.validate_on_submit():
        character = db.session.scalar(sa.select(Character).where(Character.id == id))
        character.group = form.group.data.capitalize()
        db.session.commit()
    return redirect(url_for("index"))



@app.route("/delete/<id>", methods=["POST"])
@login_required
def delete(id):
    form = EmptyForm()
    if form.validate_on_submit():
        character = db.session.scalar(sa.select(Character).where(Character.id == id))
        spells = db.session.scalars(
            sa.select(Spell).where(Spell.spell_chars == character)
        )
        for spell in spells:
            db.session.delete(spell)
        db.session.delete(character)
        db.session.commit()
    return redirect(url_for("index"))


@app.route("/add_prepared/<id>", methods=["POST"])
@login_required
def add_prepared(id):
    form = EmptyForm()
    if form.validate_on_submit():
        spell = db.session.scalar(sa.select(Spell).where(Spell.id == id))
        spell.prepared = spell.prepared + 1
        db.session.commit()

    active_char = active_finder()
    return redirect(url_for("incantesimi", char_name=active_char.name))


@app.route("/subtract_prepared/<id>", methods=["POST"])
@login_required
def subtract_prepared(id):
    form = EmptyForm()
    if form.validate_on_submit():
        spell = db.session.scalar(sa.select(Spell).where(Spell.id == id))
        if spell.prepared > 0:
            spell.prepared = spell.prepared - 1
            db.session.commit()

    active_char = active_finder()
    return redirect(url_for("incantesimi", char_name=active_char.name))


@app.route("/delete_prepared/<id>", methods=["POST"])
@login_required
def delete_prepared(id):
    form = EmptyForm()
    if form.validate_on_submit():
        spell = db.session.scalar(sa.select(Spell).where(Spell.id == id))
        db.session.delete(spell)
        db.session.commit()

    active_char = active_finder()
    return redirect(url_for("incantesimi", char_name=active_char.name))
