import typing

from celery.schedules import crontab
from flask_migrate import Migrate

from app import create_app, db
from app.models import User, Role, Post, Category
from app.tools.tasks import ask_for_confirm

if typing.TYPE_CHECKING:
    from celery import Celery

    celery_app = Celery

flask_app = create_app()
celery_app = flask_app.extensions['celery']

# if app.debug == True:
#     from werkzeug.middleware.profiler import ProfilerMiddleware
#     flask_app.wsgi_app = ProfilerMiddleware(flask_app.wsgi_app, restrictions=[20])
migrate = Migrate(flask_app, db)


# @app.errorhandler(DatabaseError)
# def special_exception_handler(error):
#      return 'Database connection failed', 500
@flask_app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Post=Post, Category=Category)


# @app.cli.command()
# @click.option('--mode', is_flag=True, show_default=True, default='dev', help='需要初始化的环境.')
# def initial(mode):
#     # upgrade()
#     # Role.insert_roles()
#     # Category.insert_categories()
#     print('initial')

@celery_app.on_after_finalize.connect
def schedule_task(sender, **kwargs):
    sender.add_periodic_task(crontab(minute='0', hour='0'), ask_for_confirm.s(), args=(2,))
