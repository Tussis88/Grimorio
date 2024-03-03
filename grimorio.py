from app import app, db
from app.models import User, Character, Spell

import sqlalchemy as sa
import sqlalchemy.orm as so

if __name__ == "__main__":
    app.run()

@app.shell_context_processor
def make_shell_context():
    return {
        "sa": sa,
        "so": so,
        "db": db,
        "User": User,
        "Character": Character,
        "Spell": Spell,
    }
