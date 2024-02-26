from flask import render_template
from app import app, db
from app.helpers import active_finder


@app.errorhandler(404)
def not_found_error(error):
    active_char = active_finder()
    return render_template("404.html", active_char=active_char), 404


@app.errorhandler(500)
def internal_error(error):
    active_char = active_finder()
    db.session.rollback()
    return render_template("500.html", active_char=active_char), 500
