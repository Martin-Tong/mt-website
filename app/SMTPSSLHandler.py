import logging
from logging.handlers import SMTPHandler
import time
from threading import Thread
from flask import has_request_context, request


class SMTPSSLHandler(SMTPHandler):
    def __init__(self, mailhost, fromaddr, toaddrs, subject, credentials, secure=None, timeout=3, timegap=300):
        super().__init__(mailhost, fromaddr, toaddrs, subject, credentials, secure, timeout)
        self.timegap = timegap
        self._recoder = dict()

    def emit(self, record):
        if not self._recoder.get('timestamp',None) or (time.time() - self._recoder['timestamp']) > self.timegap:
            try:
                _thread = Thread(target=self._emit, args=(record,))
                _thread.start()
            except Exception:
                print('邮件发送失败')
        else:
            return


    def _emit(self, record):
        try:
            import smtplib
            from email.message import EmailMessage
            import email.utils

            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP_SSL(self.mailhost, port, timeout=self.timeout)
            msg = EmailMessage()
            msg['From'] = self.fromaddr
            msg['To'] = ','.join(self.toaddrs)
            msg['Subject'] = self.getSubject(record)
            msg['Date'] = email.utils.localtime()
            msg.set_content(self.format(record))
            if self.username:
                if self.secure is not None:
                    smtp.ehlo()
                    smtp.starttls(*self.secure)
                    smtp.ehlo()
                smtp.login(self.username, self.password)
            smtp.send_message(msg)
            self._recoder['timestamp'] = time.time()
            smtp.quit()
        except Exception:
            self.handleError(record)

class SMTPHandlerFormater(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None
        return super().format(record)