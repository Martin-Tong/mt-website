from flask_migrate import Migrate

from app import create_app, db
from app.models import User, Role, Post, Category

app = create_app()
migrate = Migrate(app, db)

# @app.errorhandler(DatabaseError)
# def special_exception_handler(error):
#      return 'Database connection failed', 500

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User = User, Role = Role, Post= Post, Category = Category)

# @app.cli.command()
# @click.option('--mode', is_flag=True, show_default=True, default='dev', help='需要初始化的环境.')
# def initial(mode):
#     # upgrade()
#     # Role.insert_roles()
#     # Category.insert_categories()
#     print('initial')
