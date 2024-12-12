import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:

    def __init__(self):
        print(self.__class__)
        if self.__class__ == ProductConfig:
            #检查必须设置的隐私项配置
            l = ['SECRET_KEY', 'MAIL_USERNAME', 'MAIL_PASSWORD']
            self.checkout_attrs(l)

    SECRET_KEY = os.environ.get('SECRET_KEY')
    POSTS_PER_PAGE = os.environ.get('POSTS_PER_PAGE', 10)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.qq.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 465))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'False').lower() in ['true', 'on', 1]
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'True').lower() in ['true', 'on', 1]
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SUBJECT_PREFIX = 'NOC[Not Only Code]'
    MAIL_ADMIN = os.environ.get('MAIL_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #SEND_FILE_MAX_AGE_DEFAULT = 691200 默认情况下服务器应用发送Cache-Control:no-cache，设置这个配置可以修改默认值为Cache-Control:public, max-age=691200


    def checkout_attrs(self, targets):
        l = []
        try:
            for i in targets:
                if not self.__getattribute__(i):
                    print(f'必须在环境变量中设置<{i}>值！')
                    l.append(i)
        finally:
            if l:
                raise AttributeError('环境变量缺少必须设置的值！')

    @classmethod
    def init_app(cls, app):
        pass

class DevConfig(Config):

    # def __init__(self):
    #     super(DevConfig, self).__init__()

    DEBUG = True
    SECRET_KEY = 'hard to guess string'
    MAIL_ADMIN = os.environ.get('MAIL_ADMIN', '1933981377@qq.com')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') or 'sqlite:///'+os.path.join(basedir, 'dev-database.sqlite')

    @classmethod
    def init_app(cls, app):
        print('Development mode')

class ProductConfig(Config):

    # def __init__(self):
    #     super().__init__()

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///'+os.path.join(basedir, 'database.sqlite')

config = {
    'development': DevConfig,
    'production': ProductConfig,
    'default': DevConfig
}