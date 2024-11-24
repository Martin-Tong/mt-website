from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from app import mail


def send_async_mail(app, msg):
    with app.app_context():
        mail.send(msg)


def send_mail(to: str | list[str], subject: str, template: str, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + subject, sender=app.config['MAIL_ADMIN'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_mail, args=[app, msg])
    thr.start()
    return thr
