from urllib.parse import urlsplit
import sqlalchemy as sa
from flask import render_template, flash, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
from app.forms import (
    LoginForm,
    RegistrationForm,
    CharacterCreationForm,
    EmptyForm,
    SpellCreationForm,
    GroupChangeForm,
)
from app.helpers import active_char_setter
from app.models import User, Character, Spell


@app.route("/")
@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    form = CharacterCreationForm()
    form2 = GroupChangeForm()
    characters = db.session.scalars(
        sa.select(Character).where(Character.players == current_user)
    )
    active_char_setter()
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

    return render_template(
        "index.html",
        title="Home",
        characters=characters,
        form=form,
        form2=form2,
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
        active_char_setter()
        print("prova")
        return redirect(next_page)
    return render_template("login.html", title="Accedi", form=form)


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
    form = SpellCreationForm()
    if form.validate_on_submit():
        new_spell = Spell(
            name=form.name.data.strip().title(),
            level=int(form.level.data),
            id_character=character.id,
        )
        db.session.add(new_spell)
        db.session.commit()
        return redirect(url_for("incantesimi", char_name=char_name))

    spells = db.session.scalars(
        sa.select(Spell)
        .where(Spell.spell_chars == character)
        .order_by(Spell.level, Spell.name)
    ).all()
    is_current_editable = character.editable and character.user_id == current_user.id
    current_master = (
        session["active_char"]["master"]
        and session["active_char"]["group"] == character.group
    )

    if is_current_editable or (not character.editable and current_master):
        return render_template(
            "editabili.html",
            title="Modifica Incantesimi",
            spells=spells,
            character=character,
            form=form,
        )
    elif (character.editable and current_master) or (character.user_id == current_user.id and not character.editable) or not character.hidden:
        return render_template(
            "visibili.html",
            title="Incantesimi Preparati",
            spells=spells,
            character=character,
        )
    else:
        return render_template(
            "metapod.html",
            title="Metapod",
            character=character,
        )
    # else:
    #     return render_template(
    #         "visibili.html",
    #         title="Incantesimi Preparati",
    #         spells=spells,
    #         character=character,
    #     )


@app.route("/master/<group_name>")
@login_required
def master(group_name):
    form = EmptyForm()
    members = db.session.scalars(
        sa.select(Character)
        .where(Character.group == group_name)
        .where(Character.name != session["active_char"]["name"])
    )
    return render_template(
        "master.html",
        title="La Pagina del Master",
        members=members,
        form=form,
    )


@app.post("/activate/<id>")
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


@app.post("/editable_state/<id>")
@login_required
def editable_state(id):
    form = EmptyForm()
    if form.validate_on_submit():
        char = db.session.scalar(sa.select(Character).where(Character.id == id))
        if char:
            if char.editable:
                char.editable = False
            else:
                char.editable = True
            db.session.commit()
            return redirect(url_for("master", group_name=char.group))
    return redirect(url_for("index"))


@app.post("/hidden_state/<id>")
@login_required
def hidden_state(id):
    form = EmptyForm()
    if form.validate_on_submit():
        char = db.session.scalar(sa.select(Character).where(Character.id == id))
        if char:
            if char.hidden:
                char.hidden = False
            else:
                char.hidden = True
            db.session.commit()
    return redirect(url_for("index"))


@app.post("/change_group/<id>")
@login_required
def change_group(id):
    form = GroupChangeForm()
    if form.validate_on_submit():
        character = db.session.scalar(sa.select(Character).where(Character.id == id))
        character.group = form.group_c.data.capitalize()
        db.session.commit()
    return redirect(url_for("index"))


@app.post("/delete/<id>")
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


@app.post("/add_prepared/<id>")
@login_required
def add_prepared(id):
    form = EmptyForm()
    if form.validate_on_submit():
        spell = db.session.scalar(sa.select(Spell).where(Spell.id == id))
        if spell:
            spell.prepared = spell.prepared + 1
            db.session.commit()
    char_name = spell.spell_chars.name

    return redirect(url_for("incantesimi", char_name=char_name))


@app.post("/subtract_prepared/<id>")
@login_required
def subtract_prepared(id):
    form = EmptyForm()
    if form.validate_on_submit():
        spell = db.session.scalar(sa.select(Spell).where(Spell.id == id))
        if spell:
            if spell.prepared > 0:
                spell.prepared = spell.prepared - 1
                db.session.commit()

    char_name = spell.spell_chars.name
    return redirect(url_for("incantesimi", char_name=char_name))


@app.post("/delete_prepared/<id>")
@login_required
def delete_prepared(id):
    form = EmptyForm()
    if form.validate_on_submit():
        spell = db.session.scalar(sa.select(Spell).where(Spell.id == id))
        char_name = spell.spell_chars.name
        db.session.delete(spell)
        db.session.commit()
    return redirect(url_for("incantesimi", char_name=char_name))
