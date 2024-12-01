from flask_migrate import Migrate

from app import create_app, db
from app.models import User, Role, Post, Category

app = create_app()
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User = User, Role = Role, Post= Post, Category = Category)
