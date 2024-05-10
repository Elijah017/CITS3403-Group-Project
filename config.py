class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "123456789"

class DeploymentConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///memory"